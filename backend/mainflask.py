"""
SentinAI local gateway — desktop folder scans and SSE to the Tauri app.
"""

import os
import sys
import time
import uuid
import requests
import json
import hashlib
import logging
import secrets
import traceback
from collections import defaultdict
from datetime import datetime
from urllib.parse import unquote
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import queue as queue_module
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import database modules, fallback to JSON if not available
try:
    from backend.database import init_database, db as db_instance
    from backend.database.operations import Database
    SQL_ENABLED = True
except ImportError:
    SQL_ENABLED = False
    print("[WARNING] SQL database not available, falling back to JSON")

# Optional: Redis for live worker progress streaming (same backend as worker)
try:
    from backend.worker.core.redis_client import redis_client as _redis_client, REDIS_AVAILABLE as _REDIS_AVAILABLE
    _STREAM_PROGRESS_AVAILABLE = _REDIS_AVAILABLE and getattr(_redis_client, "rpush", None) and getattr(_redis_client, "blpop", None)
except Exception:
    _redis_client = None
    _STREAM_PROGRESS_AVAILABLE = False

app = Flask(__name__)

CORS(
    app,
    origins=["http://localhost:1420", "http://127.0.0.1:1420"],
    supports_credentials=False,
    allow_headers=["Content-Type", "X-Api-Key", "X-Worker-Secret"],
)

# Configuration
DB_FILE = "sentinel_db.json"
DB_URL = os.environ.get('DATABASE_URL', 'sqlite:///sentinel.db')
PORT = int(os.environ.get('PORT', '5001'))
WORKER_NODES = [u.strip() for u in os.environ.get('WORKER_NODES', 'http://127.0.0.1:5002').split(',') if u.strip()]
WORKER_SECRET = os.environ.get('WORKER_SECRET', '').strip()
if not WORKER_SECRET and (os.getenv("FLASK_ENV") == "production" or os.getenv("ENV") == "production"):
    raise RuntimeError("WORKER_SECRET is required in production.")

# Initialize databases (scan results only; no user accounts)
database = None
if SQL_ENABLED:
    try:
        database = init_database(DB_URL)
        print(f"[INFO] SQL Database initialized: {DB_URL}")
    except Exception as e:
        print(f"[WARNING] Failed to initialize SQL database: {e}")
        SQL_ENABLED = False

# File scanning settings
VALID_EXTENSIONS = {
    '.py', '.js', '.ts', '.html', '.php', '.java', '.c', '.cpp', '.go', '.rb',
    '.tsx', '.jsx', '.vue', '.rs', '.kt', '.swift', '.sol', '.ejs',
    '.yaml', '.yml', '.dockerfile', 'Dockerfile', '.json', '.xml', '.sql', '.env', '.config'
}
IGNORE_DIRS = {'__pycache__', '.git', 'node_modules', 'venv', 'env', '.idea', '.vscode', 
               'dist', 'build', 'coverage', 'public', 'assets', 'static', 'media', 
               'uploads', 'vendor', 'target', 'bin', 'obj'}
IGNORED_FILENAMES = {'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'Cargo.lock', 'go.sum'}
CONFIG_FILES = {'package.json', 'requirements.txt', 'pyproject.toml', 'go.mod', 'README.md'}
MAX_WORKERS = int(os.environ.get('MAX_WORKERS', '12'))
MAX_FILE_SIZE_BYTES = 1_000_000  # 1MB

SCAN_RESULTS_DIR = os.environ.get('SCAN_RESULTS_DIR', os.path.join(os.path.dirname(__file__), 'scan_results'))
os.makedirs(SCAN_RESULTS_DIR, exist_ok=True)

ANALYSIS_PROMPT = """
You are an Elite Security Architect. Analyze this project structure.
RETURN THIS EXACT JSON STRUCTURE:
{
    "project_info": {"name": "...", "framework": "...", "description": "..."},
    "security_context": {"has_authentication": true, "has_database": true, "external_apis": []},
    "risk_summary": {"top_concerns": []}
}
"""

# Worker activity tracking
MAX_ACTIVITY_ENTRIES = 500
_worker_activity = []
_worker_activity_lock = threading.Lock()


def _log_worker_activity(record: dict):
    with _worker_activity_lock:
        _worker_activity.append(record)
        while len(_worker_activity) > MAX_ACTIVITY_ENTRIES:
            _worker_activity.pop(0)


def _file_sha1(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8", errors="ignore")).hexdigest()


def _build_worker_files_payload(target_folder):
    files_payload = []
    for root, dirs, files in os.walk(target_folder):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for file in files:
            full_path = os.path.join(root, file)
            if os.path.getsize(full_path) > MAX_FILE_SIZE_BYTES:
                continue
            ext = os.path.splitext(file)[1]
            if ext in VALID_EXTENSIONS or file in CONFIG_FILES:
                try:
                    rel_path = os.path.relpath(full_path, target_folder).replace(os.sep, '/')
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    files_payload.append({
                        "filename": rel_path,
                        "content": content,
                        "sha1": _file_sha1(content),
                    })
                except Exception:
                    pass
    return files_payload


def _make_project_key(user_id, project_name, saved_files):
    fingerprint = "|".join(sorted(path for _, path in saved_files))
    raw = f"{user_id}:{project_name}:{fingerprint}"
    return "project:" + hashlib.sha1(raw.encode("utf-8", errors="ignore")).hexdigest()


def _worker_finding_to_issue_dict(finding: dict, scan_type: str) -> dict:
    """Same shape as issues built in _run_scan_events from worker /scan findings."""
    issue = {
        "severity": finding.get("severity", "HIGH"),
        "type": finding.get("type", "Unknown"),
        "trigger": finding.get("function_name", "Unknown"),
        "line": finding.get("line", 1),
        "description": finding.get("reason", "..."),
        "vulnerable_code": finding.get("vulnerable_code", ""),
    }
    if scan_type in ["2", "3", "4"]:
        issue["subtype"] = finding.get("subtype", "")
        issue["impact_summary"] = finding.get("impact_summary", "")
        issue["keywords_detected"] = finding.get("keywords_detected", [])
        issue["confidence_score"] = finding.get("confidence_score", 0)
        issue["cwe_id"] = finding.get("cwe_id", "")
    if scan_type in ["3", "4"]:
        raw_rem = finding.get("remediation", [])
        issue["remediation"] = (
            [raw_rem] if isinstance(raw_rem, str) else (raw_rem if isinstance(raw_rem, list) else [])
        )
        raw_poc = finding.get("poc")
        if isinstance(raw_poc, dict):
            v, s = raw_poc.get("vectors"), raw_poc.get("steps")
            issue["poc_verbal"] = {
                "vectors": v if isinstance(v, list) else ([v] if v else []),
                "steps": s if isinstance(s, list) else ([s] if s else []),
            }
        issue["consequences"] = finding.get("consequences", "")
        issue["references"] = finding.get("references", [])
        issue["code_context"] = finding.get("code_context", {})
        issue["fingerprint"] = finding.get("fingerprint", "")
        issue["cvss_score"] = finding.get("cvss_score", 0.0)
        issue["fix_complexity"] = finding.get("fix_complexity", "UNKNOWN")
    for key in ("validation_status", "_fp_soft_flag", "_below_threshold_note", "_cross_file_flag", "_removal_rule"):
        if finding.get(key) is not None:
            issue[key] = finding[key]
    return issue


def _merge_agent_findings_from_redis(scan_id: str, results: list, scan_type: str) -> None:
    """
    Worker may finish per-file /scan before background DeepWiki+agent completes.
    Mirror worker-side merge of Redis agent_findings into every result row.
    """
    if scan_type not in ["2", "3", "4"] or not results:
        return
    if not _STREAM_PROGRESS_AVAILABLE or not _redis_client:
        return
    raw = None
    deadline = time.time() + 120.0
    while time.time() < deadline:
        try:
            raw = _redis_client.get(f"{scan_id}:agent_findings")
        except Exception as e:
            logger.warning("[SCAN] Redis agent_findings read failed: %s", e)
            return
        if raw:
            break
        time.sleep(0.5)
    if not raw:
        return
    try:
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        agent_findings = json.loads(raw)
    except Exception as e:
        logger.warning("[SCAN] agent_findings JSON parse failed: %s", e)
        return
    if not isinstance(agent_findings, list) or not agent_findings:
        return
    mapped = [_worker_finding_to_issue_dict(f, scan_type) for f in agent_findings if isinstance(f, dict)]
    if not mapped:
        return
    for r in results:
        r.setdefault("issues", []).extend(mapped)
        if r.get("status") != "VULNERABLE":
            r["status"] = "VULNERABLE"
    logger.info("[SCAN] Merged %s agent findings into %s result rows (post-scan)", len(mapped), len(results))


DESKTOP_USER = "desktop@local"


def _require_desktop():
    """401 unless loopback + matching API key. Returns (json, status) or None."""
    if not _desktop_local_auth_ok():
        return jsonify({"error": "Loopback and matching API key required"}), 401
    return None


# ================= DATABASE HELPERS =================

def load_db():
    if SQL_ENABLED and database:
        return {}
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}


def save_db(data):
    if not SQL_ENABLED:
        with open(DB_FILE, 'w') as f:
            json.dump(data, f, indent=4)


def save_scan_result(user_id, project_name, scan_data):
    if SQL_ENABLED and database:
        try:
            return database.save_scan(user_id, project_name, scan_data)
        except Exception as e:
            print(f"[ERROR] SQL save failed, falling back to JSON: {e}")
    
    db = load_db()
    if user_id not in db:
        db[user_id] = {"projects": []}
    project = next((p for p in db[user_id]["projects"] if p["name"] == project_name), None)
    if not project:
        project = {
            "id": f"proj_{int(time.time())}",
            "name": project_name,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "scans": []
        }
        db[user_id]["projects"].append(project)
    project["scans"].insert(0, scan_data)
    save_db(db)
    return project["id"]


def save_scan_result_to_file(scan_id, scan_data):
    if not scan_id or scan_data is None:
        return
    try:
        scan_dir = os.path.join(SCAN_RESULTS_DIR, scan_id)
        os.makedirs(scan_dir, exist_ok=True)

        # Standard JSON output
        result_path = os.path.join(scan_dir, "result.json")
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(scan_data, f, indent=2, ensure_ascii=False)
        print(f"[INFO] Scan result saved to {result_path}")

        # NEW: SARIF 2.1 output for CI/CD integration
        try:
            from backend.worker.core.output.sarif_emitter import SARIFEmitter

            sarif_emitter = SARIFEmitter(tool_name="SentinelAI", tool_version="2.0")
            sarif_path = os.path.join(scan_dir, "result.sarif")
            sarif_emitter.emit(scan_data, sarif_path)
            print(f"[INFO] SARIF output saved to {sarif_path}")
        except Exception as sarif_e:
            print(f"[WARNING] Failed to generate SARIF output: {sarif_e}")

        try:
            from backend.findings_md_generator import generate_findings_md

            findings_path = os.path.join(scan_dir, "findings.md")
            generate_findings_md(scan_data, findings_path)
            print(f"[INFO] Findings report saved to {findings_path}")
        except Exception as findings_e:
            print(f"[WARNING] Failed to generate findings.md: {findings_e}")

    except Exception as e:
        print(f"[ERROR] Failed to save scan result to file: {e}")


def get_scan_from_db(user_id, project_name, scan_id):
    if SQL_ENABLED and database:
        try:
            if database.scan_exists_for_user(user_id, scan_id):
                return database.export_scan_to_dict(scan_id)
        except Exception as e:
            print(f"[ERROR] SQL query failed: {e}")
    
    db = load_db()
    user_data = db.get(user_id, {})
    projects = user_data.get("projects", [])
    
    for project in projects:
        if project_name is not None and project.get("name") != project_name:
            continue
        for scan in project.get("scans", []):
            if scan.get("scan_id") == scan_id:
                return scan
    return None


def get_projects_from_db(user_id):
    if SQL_ENABLED and database:
        try:
            return database.get_user_projects_with_scans(user_id)
        except Exception as e:
            print(f"[ERROR] SQL get projects failed: {e}")
    
    db = load_db()
    user_data = db.get(user_id, {"projects": []})
    return user_data.get("projects", [])


def scan_exists_for_user(user_id, scan_id):
    if SQL_ENABLED and database:
        try:
            return database.scan_exists_for_user(user_id, scan_id)
        except Exception as e:
            print(f"[ERROR] SQL query failed: {e}")
    
    db = load_db()
    user_data = db.get(user_id, {})
    projects = user_data.get("projects", [])
    
    for project in projects:
        for scan in project.get("scans", []):
            if scan.get("scan_id") == scan_id:
                return True
    return False


def update_poc_in_db(scan_id, fingerprint, poc_data):
    if SQL_ENABLED and database:
        try:
            return database.update_issue_poc(fingerprint, poc_data)
        except Exception as e:
            print(f"[ERROR] SQL update failed: {e}")
    return False


def get_poc_from_db(user_id, scan_id, fingerprint):
    if SQL_ENABLED and database:
        try:
            poc = database.get_poc_by_fingerprint(user_id, scan_id, fingerprint)
            if poc:
                return {"script": poc.script, "language": poc.language}
        except Exception as e:
            print(f"[ERROR] SQL query failed: {e}")
    
    db = load_db()
    user_data = db.get(user_id, {})
    projects = user_data.get("projects", [])
    
    for project in projects:
        scans = project.get("scans", [])
        for scan in scans:
            if scan.get("scan_id") == scan_id:
                vulns = scan.get("vulnerabilities", [])
                for v in vulns:
                    for issue in v.get("issues", []):
                        if issue.get("fingerprint") == fingerprint:
                            poc = issue.get("poc_script") or issue.get("poc", {})
                            if isinstance(poc, dict):
                                return poc
    return None


# ================= WORKER COMMUNICATION =================

_worker_round_robin_lock = threading.Lock()
_worker_round_robin_index = 0

def _next_worker_node():
    global _worker_round_robin_index
    if not WORKER_NODES:
        return None
    with _worker_round_robin_lock:
        node = WORKER_NODES[_worker_round_robin_index % len(WORKER_NODES)]
        _worker_round_robin_index += 1
        return node

def send_to_worker(filename, content, scan_id, scan_type="1"):
    max_global_retries = 3
    first_node = _next_worker_node()
    if not first_node:
        print("[BACKEND] No worker nodes configured")
        return None
    nodes = [first_node] + [n for n in WORKER_NODES if n != first_node]

    task_id = str(uuid.uuid4())[:8]
    started_at = datetime.utcnow().isoformat() + "Z"
    record = {
        "id": task_id,
        "worker": None,
        "filename": filename,
        "scan_id": scan_id,
        "scan_type": str(scan_type),
        "started_at": started_at,
        "completed_at": None,
        "input_size": len(content),
        "input_preview": (content[:200] + "..." if len(content) > 200 else content).replace("\n", " "),
        "status": "running",
        "findings_count": None,
        "scan_status": None,
        "error": None,
    }
    _log_worker_activity(record)

    headers = {
        "x-secret": WORKER_SECRET,
        "x-scan-id": scan_id,
        "x-scan-type": str(scan_type)
    }

    for attempt in range(max_global_retries):
        workers_exhausted = 0
        for node_url in nodes:
            try:
                print(f"[BACKEND] Sending scan request to {node_url}/scan for {filename} (Tier {scan_type})")
                response = requests.post(
                    f"{node_url}/scan",
                    json={"filename": filename, "content": content},
                    headers=headers,
                    timeout=None
                )
                print(f"[BACKEND] Worker HTTP status for {filename}: {response.status_code}")

                if response.status_code == 200:
                    try:
                        data = response.json()
                        with _worker_activity_lock:
                            record["worker"] = node_url
                            record["completed_at"] = datetime.utcnow().isoformat() + "Z"
                            record["status"] = "ok"
                            record["scan_status"] = data.get("status", "UNKNOWN")
                            record["findings_count"] = len(data.get("findings", []))
                        print(f"\n===== DEBUG WORKER RESPONSE ({filename}) =====")
                        print(json.dumps(data, indent=2)[:4000])
                        print("=============================================\n")
                        return data
                    except json.JSONDecodeError:
                        with _worker_activity_lock:
                            record["worker"] = node_url
                            record["completed_at"] = datetime.utcnow().isoformat() + "Z"
                            record["status"] = "error"
                            record["error"] = "JSON parse error"
                        print(f"JSON Parse Error for {filename} from {node_url}")
                        print(response.text[:500])
                        return None

                elif response.status_code == 429:
                    print(f"[BACKEND] Worker rate-limited (429) on {node_url}")
                    workers_exhausted += 1
                    continue
                else:
                    print(f"[BACKEND] Worker returned non-200 status {response.status_code} for {filename}")
                    continue

            except Exception as e:
                print(f"[BACKEND] Worker request error to {node_url} for {filename}: {e}")
                continue

        if workers_exhausted == len(nodes):
            wait = 5 * (attempt + 1)
            print(f"[BACKEND] All workers exhausted (429). Sleeping {wait}s...")
            time.sleep(wait)
        else:
            break

    with _worker_activity_lock:
        record["worker"] = first_node
        record["completed_at"] = datetime.utcnow().isoformat() + "Z"
        record["status"] = "error"
        record["error"] = "Failed after retries"
    return None

def request_pocs_from_worker(filename, content, findings, scan_id, max_pocs=2):
    headers = {"x-secret": WORKER_SECRET, "x-scan-id": scan_id}
    try:
        response = requests.post(
            f"{WORKER_NODES[0]}/poc",
            json={"filename": filename, "content": content, "findings": findings, "max_pocs": max_pocs},
            headers=headers,
            timeout=240
        )
        print(f"[BACKEND] Tier 4 PoC HTTP status: {response.status_code}")
        if response.status_code != 200:
            return None
        return response.json()
    except Exception as e:
        print(f"[BACKEND] Tier 4 PoC request error: {e}")
        return None

def format_duration(seconds: float) -> str:
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"
    minutes, secs = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}m {secs}s"
    hours, mins = divmod(minutes, 60)
    return f"{hours}h {mins}m {secs}s"

def _run_with_progress_stream(scan_id, blocking_fn, default_msg):
    """Run blocking_fn in a thread; yield {'type':'log', ...} from Redis until thread finishes. If Redis unavailable, yield default_msg and run in main thread."""
    if not _STREAM_PROGRESS_AVAILABLE:
        yield {'type': 'log', 'filename': 'SYSTEM', 'msg': default_msg}
        blocking_fn()
        return
    progress_key = f"{scan_id}:progress"
    try:
        _redis_client.delete(progress_key)
    except Exception:
        pass
    exc_holder = []

    def run():
        try:
            blocking_fn()
        except Exception as e:
            exc_holder.append(e)

    t = threading.Thread(target=run, daemon=True)
    t.start()
    while t.is_alive():
        try:
            raw = _redis_client.blpop(progress_key, timeout=1)
            if raw:
                _, payload = raw
                data = json.loads(payload) if isinstance(payload, str) else json.loads(payload.decode("utf-8"))
                if data.get("cache_detected"):
                    yield {'type': 'cache_detected', 'msg': data.get("msg", "Cached project data found.")}
                else:
                    msg = data.get("msg") or payload
                    yield {'type': 'log', 'filename': 'SYSTEM', 'msg': msg}
        except Exception:
            pass
    if exc_holder:
        raise exc_holder[0]


def index_project_on_workers(target_folder, scan_id, project_key=None):
    files_payload = _build_worker_files_payload(target_folder)
    if files_payload:
        for node in WORKER_NODES:
            try:
                requests.post(
                    f"{node}/index_project",
                    json={"files": files_payload, "project_key": project_key},
                    headers={"x-secret": WORKER_SECRET, "x-scan-id": scan_id},
                    timeout=60
                )
            except Exception as e:
                print(f"[BACKEND] index_project error on {node}: {e}")

def index_project_deepwiki_on_workers(target_folder, scan_id, project_key=None):
    """Kick DeepWiki pipeline on one worker; worker runs it in background (do not wait for completion)."""
    files_payload = _build_worker_files_payload(target_folder)
    if not files_payload:
        return
    node = _next_worker_node() or (WORKER_NODES[0] if WORKER_NODES else None)
    if not node:
        print("[BACKEND] No worker nodes for DeepWiki")
        return
    try:
        res = requests.post(
            f"{node}/index_project_deepwiki",
            json={"files": files_payload, "project_key": project_key},
            headers={"x-secret": WORKER_SECRET, "x-scan-id": scan_id},
            timeout=45,
        )
        print(f"[BACKEND] DeepWiki kick → {node} HTTP {res.status_code} {res.text[:200]!r}")
    except Exception as e:
        print(f"[BACKEND] DeepWiki kick error on {node}: {e}")


def request_cross_file_consistency(scan_id, vulnerabilities):
    if not vulnerabilities:
        return None
    try:
        response = requests.post(
            f"{WORKER_NODES[0]}/cross_file_consistency",
            json={"scan_id": scan_id, "vulnerabilities": vulnerabilities},
            headers={"x-secret": WORKER_SECRET},
            timeout=240,
        )
        if response.status_code != 200:
            print(f"[BACKEND] Cross-file consistency HTTP status: {response.status_code}")
            return None
        return response.json()
    except Exception as e:
        print(f"[BACKEND] Cross-file consistency request error: {e}")
        return None

def analyze_project_structure(target_folder):
    file_tree = []
    config_contents = {}
    for root, dirs, files in os.walk(target_folder):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        file_tree.append(f"{os.path.basename(root)}/")
        for file in files[:20]:
            file_tree.append(f"  {file}")
            if file in CONFIG_FILES:
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                        config_contents[file] = f.read()[:3000]
                except:
                    pass
    payload = "STRUCTURE:\n" + "\n".join(file_tree[:300]) + "\nCONFIGS:\n" + str(config_contents)
    for node in WORKER_NODES:
        try:
            res = requests.post(
                f"{node}/analyze",
                json={"project_structure": payload, "system_prompt": ANALYSIS_PROMPT},
                headers={"x-secret": WORKER_SECRET},
                timeout=90
            )
            if res.status_code == 200:
                return res.json()
        except:
            pass
    return None


# ================= SCAN EVENTS GENERATOR =================

_scan_progress = {}
_scan_progress_lock = threading.Lock()
_scan_event_queues = {}
_scan_event_queues_lock = threading.Lock()
_SSE_QUEUE_IN_USE = object()
_scan_event_log = {}
_scan_event_log_lock = threading.Lock()
SSE_HEARTBEAT_INTERVAL = 15
MAX_SCAN_PROGRESS_ENTRIES = 200


def _run_scan_background_async(temp_dir, saved_files, user_id, project_name, scan_type, scan_id, event_log, cleanup_temp=True):
    """Run scan in background thread; append events to event_log for SSE replay."""
    vuln_count = [0]

    def _update_progress(evt):
        with _scan_progress_lock:
            entry = _scan_progress.get(scan_id, {})
            etype = evt.get('type')
            if etype == 'progress':
                fs = evt.get('files_scanned', 0)
                tf = evt.get('total_files', 1)
                entry['progress_pct'] = round(100 * fs / tf, 1) if tf else 0
            elif etype == 'vuln_found':
                vuln_count[0] += evt.get('count', 0)
                entry['vuln_count'] = vuln_count[0]
            if evt.get('msg'):
                entry['message'] = evt['msg']
            elif evt.get('filename'):
                entry['message'] = evt['filename']
            entry['status'] = 'running'
            _scan_progress[scan_id] = entry

    def _push(evt):
        try:
            with event_log["cond"]:
                event_log["events"].append(evt)
                event_log["cond"].notify_all()
        except Exception:
            pass

    try:
        for evt in _run_scan_events(temp_dir, saved_files, user_id, project_name, scan_type, scan_id):
            _push(evt)
            if evt.get('type') == '_final':
                with _scan_progress_lock:
                    prev = _scan_progress.get(scan_id, {})
                    _ts = prev.get('_ts', time.time())
                    if evt.get('error'):
                        _scan_progress[scan_id] = {'status': 'error', 'message': evt['error'], 'result': None, '_ts': _ts}
                    else:
                        data = evt.get('data')
                        _scan_progress[scan_id] = {
                            'status': 'done', 'message': 'Scan complete!', 'progress_pct': 100,
                            'vuln_count': len(data.get('vulnerabilities', [])) if data else 0,
                            'result': data, '_ts': _ts,
                        }
                    if len(_scan_progress) > MAX_SCAN_PROGRESS_ENTRIES:
                        keys = sorted(_scan_progress, key=lambda k: _scan_progress[k].get('_ts', 0))[:len(_scan_progress) - MAX_SCAN_PROGRESS_ENTRIES]
                        for k in keys:
                            _scan_progress.pop(k, None)
                break
            else:
                _update_progress(evt)
    except Exception as e:
        traceback.print_exc()
        with _scan_progress_lock:
            _scan_progress[scan_id] = {'status': 'error', 'message': str(e), 'result': None}
    finally:
        try:
            with event_log["cond"]:
                event_log["done"] = True
                event_log["cond"].notify_all()
        except Exception:
            pass
        with _scan_event_log_lock:
            _scan_event_log.pop(scan_id, None)
        try:
            import shutil
            if cleanup_temp and temp_dir and os.path.isdir(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass

def _run_scan_events(temp_dir, saved_files, user_id, project_name, scan_type, scan_id):
    scan_start = time.time()
    analysis = {}
    project_key = _make_project_key(user_id, project_name, saved_files)
    try:
        yield {'type': 'start', 'msg': f'Starting Tier {scan_type} scan…'}

        if scan_type in ["2", "3", "4"]:
            yield {'type': 'log', 'filename': 'SYSTEM', 'msg': 'Analyzing project layout…'}
            analysis = analyze_project_structure(temp_dir)

        for evt in _run_with_progress_stream(
            scan_id,
            lambda: index_project_on_workers(temp_dir, scan_id, project_key),
            'Indexing project for scan context…'
        ):
            yield evt

        if scan_type in ["2", "3", "4"]:
            def _kick_deepwiki():
                try:
                    index_project_deepwiki_on_workers(temp_dir, scan_id, project_key)
                except Exception as e:
                    print(f"[BACKEND] DeepWiki kick thread error: {e}")

            threading.Thread(target=_kick_deepwiki, daemon=True).start()
            yield {
                'type': 'log',
                'filename': 'SYSTEM',
                'msg': 'DeepWiki + graph indexing started on worker (parallel with file scans). '
                'Progress may continue via Redis after file scanning begins.',
            }

        yield {'type': 'log', 'filename': 'SYSTEM', 'msg': 'Scanning files…'}

        results = []
        files_scanned = 0
        executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
        future_map = {}

        for full_path, relative_path in saved_files:
            ext = os.path.splitext(full_path)[1]
            if ext not in VALID_EXTENSIONS or os.path.basename(full_path) in IGNORED_FILENAMES:
                continue
            try:
                if os.path.getsize(full_path) > MAX_FILE_SIZE_BYTES:
                    yield {'type': 'log', 'filename': relative_path, 'msg': 'Skipped: File too large (>1MB)'}
                    continue
            except OSError:
                yield {'type': 'log', 'filename': relative_path, 'msg': 'Skipped: Unable to read file size'}
                continue

            yield {'type': 'file_start', 'filename': relative_path}

            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception as e:
                yield {'type': 'log', 'filename': relative_path, 'msg': f'Error: {str(e)}'}
                continue

            if not content.strip():
                continue

            future = executor.submit(send_to_worker, relative_path, content, scan_id, scan_type)
            future_map[future] = {"relative_path": relative_path, "content": content}

        total_files = len(future_map)
        if total_files > 0:
            yield {'type': 'progress', 'files_scanned': 0, 'total_files': total_files}
        for future in as_completed(future_map):
            meta = future_map[future]
            relative_path = meta["relative_path"]
            content = meta["content"]

            try:
                data = future.result()
                files_scanned += 1
            except Exception as e:
                yield {'type': 'log', 'filename': relative_path, 'msg': f'Error: {str(e)}'}
                continue

            if data.get("status") == "VULNERABLE":
                worker_findings = data.get("findings", [])
                structured_issues = []
                for finding in worker_findings:
                    issue = {
                        "severity": finding.get("severity", "HIGH"),
                        "type": finding.get("type", "Unknown"),
                        "trigger": finding.get("function_name", "Unknown"),
                        "line": finding.get("line", 1),
                        "description": finding.get("reason", "..."),
                        "vulnerable_code": finding.get("vulnerable_code", "")
                    }
                    if scan_type in ["2", "3", "4"]:
                        issue["subtype"] = finding.get("subtype", "")
                        issue["impact_summary"] = finding.get("impact_summary", "")
                        issue["keywords_detected"] = finding.get("keywords_detected", [])
                        issue["confidence_score"] = finding.get("confidence_score", 0)
                        issue["cwe_id"] = finding.get("cwe_id", "")
                    if scan_type in ["3", "4"]:
                        raw_rem = finding.get("remediation", [])
                        issue["remediation"] = [raw_rem] if isinstance(raw_rem, str) else (raw_rem if isinstance(raw_rem, list) else [])
                        raw_poc = finding.get("poc")
                        if isinstance(raw_poc, dict):
                            v, s = raw_poc.get("vectors"), raw_poc.get("steps")
                            issue["poc_verbal"] = {
                                "vectors": v if isinstance(v, list) else ([v] if v else []),
                                "steps": s if isinstance(s, list) else ([s] if s else [])
                            }
                        issue["consequences"] = finding.get("consequences", "")
                        issue["references"] = finding.get("references", [])
                        issue["code_context"] = finding.get("code_context", {})
                        issue["fingerprint"] = finding.get("fingerprint", "")
                        issue["cvss_score"] = finding.get("cvss_score", 0.0)
                        issue["fix_complexity"] = finding.get("fix_complexity", "UNKNOWN")
                    # Validation/certainty metadata for reporting
                    for key in ("validation_status", "_fp_soft_flag", "_below_threshold_note", "_cross_file_flag", "_removal_rule"):
                        if finding.get(key) is not None:
                            issue[key] = finding[key]
                    structured_issues.append(issue)

                results.append({"filename": relative_path, "status": "VULNERABLE", "source_code": content, "issues": structured_issues})
                yield {'type': 'vuln_found', 'filename': relative_path, 'count': len(structured_issues), 'issues': structured_issues}
                yield {'type': 'progress', 'files_scanned': files_scanned, 'total_files': total_files}
            elif data.get("status") == "NOT_SCANNED" or data.get("skipped"):
                # Record skipped (low-risk) files so reports can show "Skipped for cost"
                results.append({
                    "filename": relative_path,
                    "status": "NOT_SCANNED",
                    "skipped": True,
                    "skip_reason": data.get("skip_reason", "Low risk score"),
                    "risk_score": data.get("risk_score"),
                    "source_code": content,
                    "issues": [],
                })
                yield {'type': 'file_safe', 'filename': relative_path}
                yield {'type': 'progress', 'files_scanned': files_scanned, 'total_files': total_files}
            else:
                yield {'type': 'file_safe', 'filename': relative_path}
                yield {'type': 'progress', 'files_scanned': files_scanned, 'total_files': total_files}

        executor.shutdown(wait=True)
        elapsed_seconds = time.time() - scan_start
        duration_msg = format_duration(elapsed_seconds)

        yield {'type': 'start', 'msg': 'Compiling report…'}

        if results:
            _merge_agent_findings_from_redis(scan_id, results, scan_type)
            cross_file_result = request_cross_file_consistency(scan_id, results)
            if cross_file_result and cross_file_result.get("vulnerabilities") is not None:
                results = cross_file_result.get("vulnerabilities", results)
                logger.info(
                    "[SCAN] Cross-file consistency: %s findings after aggregation",
                    sum(len(r.get("issues", [])) for r in results),
                )

        final_scan_data = {
            "scan_id": scan_id,
            "scan_type": scan_type,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "stats": {"files_scanned": files_scanned, "vulnerabilities": len(results), "elapsed_seconds": elapsed_seconds},
            "project_analysis": analysis,
            "vulnerabilities": results,
            "project_name": project_name
        }
        save_scan_result(user_id, project_name, final_scan_data)
        save_scan_result_to_file(scan_id, final_scan_data)

        yield {'type': 'log', 'filename': 'SYSTEM', 'msg': f'Done in {duration_msg}.'}
        yield {'type': 'complete', 'scan_id': scan_id}
        yield {'type': '_final', 'data': final_scan_data}

    except Exception as e:
        yield {'type': 'log', 'filename': 'SYSTEM', 'msg': f'CRITICAL ERROR: {str(e)}'}
        yield {'type': '_final', 'data': None, 'error': str(e)}


# ================= API ROUTES =================

def _is_loopback_addr(addr: str) -> bool:
    return addr in ("127.0.0.1", "::1", "localhost")


def _desktop_local_auth_ok() -> bool:
    if not _is_loopback_addr(request.remote_addr or ""):
        return False
    provided = (
        (request.headers.get("X-Api-Key") or request.headers.get("X-Worker-Secret") or "")
        .strip()
    )
    expected = (os.getenv("WORKER_SECRET") or os.getenv("CLOSESOURCE_API_KEY") or "").strip()
    if not expected:
        return True
    if not provided:
        return False
    return secrets.compare_digest(provided, expected)


def _collect_folder_files(source_dir: str):
    """Walk a local project folder. Returns list of (full_path, relative_posix)."""
    saved = []
    root = os.path.abspath(source_dir)
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for name in files:
            if name in IGNORED_FILENAMES:
                continue
            ext = os.path.splitext(name)[1]
            if ext not in VALID_EXTENSIONS and name not in CONFIG_FILES:
                continue
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, root).replace("\\", "/")
            if ".." in rel.split("/"):
                continue
            saved.append((full, rel))
    return saved


def _start_background_scan(temp_dir, saved_files, user_email, project_name, scan_type, cleanup_temp=True):
    scan_id = f"scan_{user_email}_{int(time.time())}"
    with _scan_progress_lock:
        _scan_progress[scan_id] = {
            "status": "running",
            "message": "Initializing...",
            "progress_pct": 0,
            "vuln_count": 0,
            "_ts": time.time(),
        }
    event_log = {"events": [], "cond": threading.Condition(), "done": False}
    with _scan_event_log_lock:
        _scan_event_log[scan_id] = event_log
    t = threading.Thread(
        target=_run_scan_background_async,
        args=(temp_dir, saved_files, user_email, project_name, scan_type, scan_id, event_log, cleanup_temp),
        daemon=True,
    )
    t.start()
    return scan_id


@app.route("/api/scan/local-start", methods=["POST", "OPTIONS"])
def scan_local_start():
    """Desktop-only: scan a folder already on this machine. Loopback + API key."""
    if request.method == "OPTIONS":
        return ("", 204)
    if not _desktop_local_auth_ok():
        return jsonify({"error": "Desktop local scan requires loopback and a matching API key"}), 401

    data = request.get_json(silent=True) or {}
    source_dir = (data.get("source_dir") or data.get("source") or "").strip()
    if not source_dir or not os.path.isdir(source_dir):
        return jsonify({"error": "source_dir must be an existing folder on this machine"}), 400

    project_name = (data.get("project_name") or os.path.basename(os.path.abspath(source_dir)) or "Local folder").strip()
    scan_type = str(data.get("scan_type") or "2")
    if scan_type not in ("1", "2", "3", "4"):
        scan_type = "2"

    saved_files = _collect_folder_files(source_dir)
    if not saved_files:
        return jsonify({"error": "No scannable files in that folder"}), 400

    user_email = DESKTOP_USER
    scan_id = _start_background_scan(
        os.path.abspath(source_dir),
        saved_files,
        user_email,
        project_name,
        scan_type,
        cleanup_temp=False,
    )
    return jsonify({"scan_id": scan_id, "file_count": len(saved_files)})


@app.route('/api/scan/cache-choice', methods=['POST'])
def scan_cache_choice():
    """Set choice for cached scan: use cache (1) or rescan from 0 (0). Worker blocks until this is set."""
    denied = _require_desktop()
    if denied:
        return denied
    user_email = DESKTOP_USER
    data = request.get_json(silent=True) or {}
    scan_id = (data.get('scan_id') or request.form.get('scan_id') or '').strip()
    use_cache = data.get('use_cache', request.form.get('use_cache', True))
    if not scan_id or not scan_id.startswith('scan_'):
        return jsonify({"error": "Invalid scan_id"}), 400
    parts = scan_id.split('_')
    if len(parts) < 3:
        return jsonify({"error": "Invalid scan_id"}), 400
    scan_user = '_'.join(parts[1:-1]).lower()
    if scan_user != user_email.lower():
        return jsonify({"error": "Scan not found"}), 404
    try:
        val = '1' if use_cache in (True, '1', 'true', 'yes') else '0'
        if _STREAM_PROGRESS_AVAILABLE and getattr(_redis_client, 'lpush', None):
            _redis_client.lpush(f"{scan_id}:cache_choice", val)
        return jsonify({"ok": True, "use_cache": use_cache})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/scan/status/<path:scan_id>', methods=['GET'])
def scan_status(scan_id):
    """Return current progress for an async scan."""
    with _scan_progress_lock:
        entry = _scan_progress.get(scan_id, {})
    if not entry:
        return jsonify({"status": "pending", "message": "Scan starting or not found. Keep polling.", "progress_pct": 0, "vuln_count": 0})
    out = {k: v for k, v in entry.items() if k != '_ts'}
    return jsonify(out)


@app.route('/api/scan/events/<path:scan_id>', methods=['GET'])
def scan_events_sse(scan_id):
    """SSE stream: replay event log from start then stream new events."""
    with _scan_event_log_lock:
        event_log = _scan_event_log.get(scan_id)
    if event_log is None:
        return jsonify({"error": "Scan not found"}), 404

    @stream_with_context
    def generate():
        last_idx = 0
        try:
            while True:
                with event_log["cond"]:
                    events = event_log["events"]
                    done = event_log["done"]
                    to_send = list(events[last_idx:])
                    last_idx = len(events)
                    if done:
                        break
                    event_log["cond"].wait(timeout=SSE_HEARTBEAT_INTERVAL)
                for evt in to_send:
                    yield f"data: {json.dumps(evt)}\n\n"
                if done:
                    break
                if not done and len(to_send) == 0:
                    yield ": heartbeat\n\n"
            for evt in to_send:
                yield f"data: {json.dumps(evt)}\n\n"
        except GeneratorExit:
            raise

    resp = Response(generate(), mimetype='text/event-stream')
    resp.headers['Content-Type'] = 'text/event-stream; charset=utf-8'
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['X-Accel-Buffering'] = 'no'
    resp.headers['Connection'] = 'keep-alive'
    return resp


@app.route('/api/scan/pocs', methods=['POST'])
def generate_pocs_for_scan():
    """Generate PoCs for selected findings."""
    denied = _require_desktop()
    if denied:
        return denied
    user_email = DESKTOP_USER

    data = request.get_json(force=True)
    project_name = data.get("project_name")
    scan_id = data.get("scan_id")
    requested_fps = data.get("fingerprints", [])

    if not (project_name and scan_id):
        return jsonify({"error": "Missing project_name or scan_id"}), 400

    target_scan = get_scan_from_db(user_email, project_name, scan_id)
    if not target_scan:
        return jsonify({"error": "Scan not found"}), 404

    issues_needing_poc = []
    for v in target_scan.get("vulnerabilities", []):
        filename = v.get("filename")
        source_code = v.get("source_code", "")
        for issue in v.get("issues", []):
            fp = issue.get("fingerprint")
            if issue.get("poc_script"):
                continue
            if requested_fps and fp not in requested_fps:
                continue

            issues_needing_poc.append({
                "fingerprint": fp,
                "type": issue.get("type"),
                "subtype": issue.get("subtype"),
                "severity": issue.get("severity"),
                "function_name": issue.get("trigger"),
                "vulnerable_code": issue.get("vulnerable_code"),
                "reason": issue.get("description"),
                "impact_summary": issue.get("impact_summary"),
                "surrounding_code": "\n".join(issue.get("code_context", {}).get("before", [])) + "\n" +
                                    issue.get("code_context", {}).get("target", "") + "\n" +
                                    "\n".join(issue.get("code_context", {}).get("after", [])),
                "_filename": filename,
                "_source_code": source_code
            })

    if not issues_needing_poc:
        return jsonify({"error": "No findings needing PoCs"}), 400

    per_file = defaultdict(list)
    per_file_source = {}

    for f in issues_needing_poc:
        fname = f.pop("_filename")
        src = f.pop("_source_code")
        per_file[fname].append(f)
        per_file_source[fname] = src

    poc_map = {}

    for fname, findings in per_file.items():
        poc_data = request_pocs_from_worker(fname, per_file_source[fname], findings, scan_id, max_pocs=len(findings))
        if not poc_data or poc_data.get("status") != "OK":
            continue

        for f in poc_data.get("findings", []):
            fp = f.get("fingerprint")
            poc = f.get("poc")
            if fp and isinstance(poc, dict):
                poc_map[fp] = poc
                update_poc_in_db(scan_id, fp, poc)

    if poc_map:
        return jsonify({"status": "OK", "poc_map": poc_map})

    return jsonify({"error": "PoC generation failed"}), 500


@app.route("/api/scan/docs/<scan_id>", methods=["GET"])
def get_scan_docs(scan_id):
    """Get DeepWiki docs for a scan."""
    denied = _require_desktop()
    if denied:
        return denied
    user_email = DESKTOP_USER

    if not scan_exists_for_user(user_email, scan_id):
        return jsonify({"error": "Scan not found"}), 404

    try:
        worker_url = WORKER_NODES[0]
        res = requests.get(
            f"{worker_url}/deepwiki_docs",
            headers={"x-secret": WORKER_SECRET, "x-scan-id": scan_id},
            timeout=60
        )
        if res.status_code != 200:
            return jsonify({"error": "No DeepWiki docs", "status": res.status_code}), res.status_code
        return Response(res.text, mimetype="text/plain")
    except Exception as e:
        print("[BACKEND] get_scan_docs error:", e)
        return jsonify({"error": "Internal error"}), 500


@app.route('/api/scan/by-id/<path:scan_id>', methods=['GET'])
def get_scan_by_id(scan_id):
    """Get full scan details by scan_id."""
    denied = _require_desktop()
    if denied:
        return denied
    user_email = DESKTOP_USER

    try:
        decoded = scan_id
        for _ in range(2):
            nxt = unquote(decoded)
            if nxt == decoded:
                break
            decoded = nxt
        scan_id = decoded
    except Exception:
        pass

    if not scan_exists_for_user(user_email, scan_id):
        return jsonify({"error": "Scan not found"}), 404
    scan_data = get_scan_from_db(user_email, None, scan_id)
    if not scan_data:
        return jsonify({"error": "Scan not found"}), 404
    return jsonify(scan_data)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Check database and worker health."""
    db_status = "healthy" if (SQL_ENABLED and database) else "json-fallback"

    worker_status = []
    for node in WORKER_NODES:
        try:
            res = requests.get(f"{node}/health", timeout=5)
            worker_status.append({"node": node, "status": res.status_code})
        except Exception as e:
            worker_status.append({"node": node, "status": "unreachable", "error": str(e)})

    return jsonify({
        "database": db_status,
        "sql_enabled": SQL_ENABLED,
        "workers": worker_status,
        "version": "desktop-local",
        "port": PORT
    })


if __name__ == "__main__":
    print("[INFO] SentinAI local gateway")
    print(f"[INFO] Database: {DB_URL}")
    print(f"[INFO] SQL Enabled: {SQL_ENABLED}")
    print(f"[INFO] Listening on http://127.0.0.1:{PORT}")
    app.run(host="127.0.0.1", port=PORT, debug=False, threaded=True, use_reloader=False)
