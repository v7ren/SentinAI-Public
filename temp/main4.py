import os
import sys
import time
import uuid
import shutil
import requests
import random
import json
import tempfile
import traceback
from io import BytesIO
from datetime import datetime
from flask import Flask, request, jsonify, Response, stream_with_context, make_response
from flask_cors import CORS
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import queue as queue_module

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

app = Flask(__name__)
CORS(app)

# Configuration
DB_FILE = "sentinel_db.json"
DB_URL = os.environ.get('DATABASE_URL', 'sqlite:///sentinel.db')
PORT = int(os.environ.get('PORT', '5001'))  # Main backend on 5001
WORKER_NODES = [u.strip() for u in os.environ.get('WORKER_NODES', 'http://127.0.0.1:5002').split(',') if u.strip()]
_worker_secret = os.environ.get('WORKER_SECRET', '').strip()
if not _worker_secret:
    import warnings
    warnings.warn("WORKER_SECRET is not set; set it in production to secure gateway–worker communication.")
    _worker_secret = '109002104049989hcjh'  # dev fallback only
WORKER_SECRET = _worker_secret

# Initialize database if SQL is enabled
database = None
if SQL_ENABLED:
    try:
        database = init_database(DB_URL)
        print(f"[INFO] SQL Database initialized: {DB_URL}")
    except Exception as e:
        print(f"[WARNING] Failed to initialize SQL database: {e}")
        SQL_ENABLED = False

# UPDATED: Added .yaml, .dockerfile, .env, .sql, etc.
VALID_EXTENSIONS = {
    '.py', '.js', '.ts', '.html', '.php', '.java', '.c', '.cpp', '.go', '.rb', 'ejs',
    '.tsx', '.jsx', '.vue', '.rs', '.kt', '.swift', '.sol',
    '.yaml', '.yml', '.dockerfile', 'Dockerfile', '.json', '.xml', '.sql', '.env', '.config'
}
IGNORE_DIRS = {'__pycache__', '.git', 'node_modules', 'venv', 'env', '.idea', '.vscode', 'dist', 'build', 'coverage', 'public', 'assets', 'static', 'media', 'uploads', 'vendor', 'target', 'bin', 'obj'}
IGNORED_FILENAMES = {'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'Cargo.lock', 'go.sum'}
CONFIG_FILES = {'package.json', 'requirements.txt', 'pyproject.toml', 'go.mod', 'README.md'}
MAX_WORKERS = int(os.environ.get('MAX_WORKERS', '12'))  # Parallel file scans; use more workers + multiple nodes for speed
INDEX_NODE_WORKERS = int(os.environ.get('INDEX_NODE_WORKERS', '8'))  # Parallel index requests per index step (across worker nodes)
# Admin: in-memory worker activity log (last N tasks per worker)
MAX_ACTIVITY_ENTRIES = 500
_worker_activity = []
_worker_activity_lock = threading.Lock()


def _log_worker_activity(record: dict):
    """Append an activity record and trim if over limit."""
    with _worker_activity_lock:
        _worker_activity.append(record)
        while len(_worker_activity) > MAX_ACTIVITY_ENTRIES:
            _worker_activity.pop(0)
# NEW: Prevent RAM Crashes
MAX_FILE_SIZE_BYTES = 1_000_000  # 1MB

# Physical JSON output: one folder per scan, result saved as result.json
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

# ================= DATABASE HELPERS =================
def load_db():
    """Load database - returns dict for compatibility"""
    if SQL_ENABLED and database:
        # Return empty dict as we use SQL now
        return {}
    # Fallback to JSON
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}


def save_db(data):
    """Save database - only used for JSON fallback"""
    if not SQL_ENABLED:
        with open(DB_FILE, 'w') as f:
            json.dump(data, f, indent=4)


def save_scan_result(user_id, project_name, scan_data):
    """Save scan result to database (SQL preferred, JSON fallback)"""
    if SQL_ENABLED and database:
        try:
            return database.save_scan(user_id, project_name, scan_data)
        except Exception as e:
            print(f"[ERROR] SQL save failed, falling back to JSON: {e}")
    
    # Fallback to JSON
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
    """Save scan result as a physical JSON file in a folder per scan: scan_results/<scan_id>/result.json"""
    if not scan_id or scan_data is None:
        return
    try:
        scan_dir = os.path.join(SCAN_RESULTS_DIR, scan_id)
        os.makedirs(scan_dir, exist_ok=True)
        result_path = os.path.join(scan_dir, "result.json")
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(scan_data, f, indent=2, ensure_ascii=False)
        print(f"[INFO] Scan result saved to {result_path}")
    except Exception as e:
        print(f"[ERROR] Failed to save scan result to file: {e}")


def get_scan_from_db(user_id, project_name, scan_id):
    """Get scan data from database"""
    if SQL_ENABLED and database:
        try:
            # First check if scan exists for this user
            if database.scan_exists_for_user(user_id, scan_id):
                return database.export_scan_to_dict(scan_id)
        except Exception as e:
            print(f"[ERROR] SQL query failed: {e}")
    
    # Fallback to JSON
    db = load_db()
    user_data = db.get(user_id, {})
    projects = user_data.get("projects", [])
    
    for project in projects:
        if project.get("name") != project_name:
            continue
        for scan in project.get("scans", []):
            if scan.get("scan_id") == scan_id:
                return scan
    return None


def get_projects_from_db(user_id):
    """Get projects for user (with full scans array when SQL, so frontend gets same JSON shape)."""
    if SQL_ENABLED and database:
        try:
            return database.get_user_projects_with_scans(user_id)
        except Exception as e:
            print(f"[ERROR] SQL get projects failed: {e}")
    
    # Fallback to JSON
    db = load_db()
    user_data = db.get(user_id, {"projects": []})
    return user_data.get("projects", [])


def scan_exists_for_user(user_id, scan_id):
    """Check if scan exists for user"""
    if SQL_ENABLED and database:
        try:
            return database.scan_exists_for_user(user_id, scan_id)
        except Exception as e:
            print(f"[ERROR] SQL query failed: {e}")
    
    # Fallback to JSON
    db = load_db()
    user_data = db.get(user_id, {})
    projects = user_data.get("projects", [])
    
    for project in projects:
        for scan in project.get("scans", []):
            if scan.get("scan_id") == scan_id:
                return True
    return False


def update_poc_in_db(scan_id, fingerprint, poc_data):
    """Update PoC in database"""
    if SQL_ENABLED and database:
        try:
            return database.update_issue_poc(fingerprint, poc_data)
        except Exception as e:
            print(f"[ERROR] SQL update failed: {e}")
    
    # Fallback to JSON - scan already loaded and modified in memory
    # The caller is responsible for calling save_db()
    return False


def get_poc_from_db(user_id, scan_id, fingerprint):
    """Get PoC from database"""
    if SQL_ENABLED and database:
        try:
            poc = database.get_poc_by_fingerprint(user_id, scan_id, fingerprint)
            if poc:
                return {"script": poc.script, "language": poc.language}
        except Exception as e:
            print(f"[ERROR] SQL query failed: {e}")
    
    # Fallback to JSON
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
    """Thread-safe round-robin across WORKER_NODES so parallel scans spread across workers."""
    global _worker_round_robin_index
    if not WORKER_NODES:
        return None
    with _worker_round_robin_lock:
        node = WORKER_NODES[_worker_round_robin_index % len(WORKER_NODES)]
        _worker_round_robin_index += 1
        return node

def send_to_worker(filename, content, scan_id, scan_type="1"):
    """Sends a single file to a worker node (round-robin). Retries other nodes on failure."""
    max_global_retries = 3
    # Try round-robin node first, then rest (so parallel tasks spread across workers)
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
    with _worker_activity_lock:
        _worker_activity.append(record)
        while len(_worker_activity) > MAX_ACTIVITY_ENTRIES:
            _worker_activity.pop(0)

    headers = {
        "x-secret": WORKER_SECRET,
        "x-scan-id": scan_id,
        "x-scan-type": str(scan_type)  # Pass the scan tier (1, 2, or 3)
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
                    timeout=None  # No timeout to prevent blocking
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
                        print(f"❌ JSON Parse Error for {filename} from {node_url}. Raw text:")
                        print(response.text[:500])
                        return None

                elif response.status_code == 429:
                    print(f"[BACKEND] Worker rate-limited (429) on {node_url}")
                    workers_exhausted += 1
                    continue
                else:
                    print(f"[BACKEND] Worker returned non-200 status {response.status_code} for {filename}")
                    print(f"[BACKEND] Body: {response.text[:500]}")
                    continue

            except Exception as e:
                print(f"[BACKEND] Worker request error to {node_url} for {filename}: {e}")
                continue

        if workers_exhausted == len(nodes):
            wait = 5 * (attempt + 1)
            print(f"[BACKEND] All workers exhausted (429). Sleeping {wait}s then retrying...")
            time.sleep(wait)
        else:
            # No rate limit, but still failed; don't loop infinitely
            break

    with _worker_activity_lock:
        record["worker"] = first_node
        record["completed_at"] = datetime.utcnow().isoformat() + "Z"
        record["status"] = "error"
        record["error"] = "Failed after retries"
    print(f"[BACKEND] send_to_worker FAILED for {filename} after retries")
    return None

def request_pocs_from_worker(filename, content, findings, scan_id, max_pocs=2):
    """Call worker Tier 4 /poc to enrich findings with PoCs."""
    headers = {
        "x-secret": WORKER_SECRET,
        "x-scan-id": scan_id
    }

    try:
        response = requests.post(
            f"{WORKER_NODES[0]}/poc",
            json={
                "filename": filename,
                "content": content,
                "findings": findings,
                "max_pocs": max_pocs
            },
            headers=headers,
            timeout=240
        )
        print(f"[BACKEND] Tier 4 PoC HTTP status: {response.status_code}")

        if response.status_code != 200:
            print("[BACKEND] Tier 4 PoC error body:", response.text[:400])
            return None

        data = response.json()
        print("\n===== DEBUG TIER 4 POC RESPONSE =====")
        print(json.dumps(data, indent=2)[:4000])
        print("=====================================\n")
        return data

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


def _build_index_files_payload(target_folder):
    """Build list of {filename, content} for indexing. Shared by regex and DeepWiki indexers."""
    files_payload = []
    for root, dirs, files in os.walk(target_folder):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for file in files:
            full_path = os.path.join(root, file)
            try:
                if os.path.getsize(full_path) > MAX_FILE_SIZE_BYTES:
                    continue
            except OSError:
                continue
            ext = os.path.splitext(file)[1]
            if ext in VALID_EXTENSIONS or file in CONFIG_FILES:
                try:
                    rel_path = os.path.relpath(full_path, target_folder)
                    rel_path = rel_path.replace(os.sep, '/')
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        files_payload.append({"filename": rel_path, "content": f.read()})
                except Exception:
                    pass
    return files_payload


def _post_index_to_node(node_url, scan_id, files_payload, endpoint, timeout):
    """POST index payload to a single worker node. Returns (node_url, success, error)."""
    try:
        res = requests.post(
            f"{node_url}/{endpoint}",
            json={"files": files_payload},
            headers={"x-secret": WORKER_SECRET, "x-scan-id": scan_id},
            timeout=timeout,
        )
        if res.status_code != 200:
            return (node_url, False, f"HTTP {res.status_code}")
        return (node_url, True, None)
    except Exception as e:
        return (node_url, False, str(e))


def index_project_on_workers(target_folder, scan_id):
    """Indexes ALL valid files on all worker nodes in parallel. Uses relative paths so multiple files with the same name are all indexed."""
    files_payload = _build_index_files_payload(target_folder)
    if not files_payload or not WORKER_NODES:
        return
    n_workers = min(len(WORKER_NODES), INDEX_NODE_WORKERS)
    with ThreadPoolExecutor(max_workers=n_workers) as ex:
        futures = [
            ex.submit(_post_index_to_node, node, scan_id, files_payload, "index_project", 60)
            for node in WORKER_NODES
        ]
        for fut in as_completed(futures):
            node_url, ok, err = fut.result()
            if not ok:
                print(f"[BACKEND] index_project error on {node_url}: {err}")


def index_project_deepwiki_on_workers(target_folder, scan_id):
    """Builds LLM (DeepWiki) index on all worker nodes in parallel."""
    files_payload = _build_index_files_payload(target_folder)
    if not files_payload or not WORKER_NODES:
        return
    n_workers = min(len(WORKER_NODES), INDEX_NODE_WORKERS)
    with ThreadPoolExecutor(max_workers=n_workers) as ex:
        futures = [
            ex.submit(_post_index_to_node, node, scan_id, files_payload, "index_project_deepwiki", 600)
            for node in WORKER_NODES
        ]
        for fut in as_completed(futures):
            node_url, ok, err = fut.result()
            if not ok:
                print(f"[BACKEND] DeepWiki index error on {node_url}: {err}")


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

# ================= API ROUTES =================

# In-memory progress for async scan (polling). Key: scan_id, Value: { status, message, progress_pct, vuln_count, result?, error? }
_scan_progress = {}
_scan_progress_lock = threading.Lock()
# SSE: event log per scan_id so multiple/reconnecting clients can subscribe; background thread appends events
_scan_event_log = {}  # scan_id -> {"events": list, "cond": Condition, "done": bool}
_scan_event_log_lock = threading.Lock()
SSE_HEARTBEAT_INTERVAL = 15  # seconds; keep connection alive for proxies/HTTP2
MAX_SCAN_PROGRESS_ENTRIES = 200  # prevent unbounded growth


def _run_scan_events(temp_dir, saved_files, user_id, project_name, scan_type, scan_id):
    """Generator that yields scan event dicts; finally yields {"type": "_final", "data": final_scan_data}."""
    scan_start = time.time()
    analysis = {}
    try:
        yield {'type': 'start', 'msg': f'Initializing Tier {scan_type} Scan...'}

        if scan_type in ["2", "3", "4"]:
            yield {'type': 'log', 'filename': 'SYSTEM', 'msg': 'Analyzing project architecture...'}
            analysis = analyze_project_structure(temp_dir)

        yield {'type': 'log', 'filename': 'SYSTEM', 'msg': 'Indexing project for scan context...'}
        index_error = None
        deepwiki_error = None

        def _run_regex_index():
            try:
                index_project_on_workers(temp_dir, scan_id)
                return None
            except Exception as e:
                return e

        def _run_deepwiki_index():
            try:
                index_project_deepwiki_on_workers(temp_dir, scan_id)
                return None
            except Exception as e:
                return e

        if scan_type == "1":
            # Tier 1: regex index only (skip DeepWiki to start scanning sooner)
            try:
                _log_worker_activity({
                    "id": str(uuid.uuid4())[:8],
                    "worker": WORKER_NODES[0] if WORKER_NODES else None,
                    "filename": "[Index] project",
                    "scan_id": scan_id,
                    "scan_type": str(scan_type),
                    "started_at": datetime.utcnow().isoformat() + "Z",
                    "completed_at": None,
                    "input_size": 0,
                    "input_preview": "Sending file list to workers (parallel nodes)",
                    "status": "running",
                    "findings_count": None,
                    "scan_status": None,
                    "error": None,
                })
                index_project_on_workers(temp_dir, scan_id)
                _log_worker_activity({
                    "id": str(uuid.uuid4())[:8],
                    "worker": ",".join(WORKER_NODES) if WORKER_NODES else None,
                    "filename": "[Index] project",
                    "scan_id": scan_id,
                    "scan_type": str(scan_type),
                    "started_at": datetime.utcnow().isoformat() + "Z",
                    "completed_at": datetime.utcnow().isoformat() + "Z",
                    "input_size": 0,
                    "input_preview": "Done",
                    "status": "ok",
                    "findings_count": None,
                    "scan_status": None,
                    "error": None,
                })
            except Exception as e:
                index_error = e
                print(f"[BACKEND] index_project_on_workers FAILED: {e}")
                traceback.print_exc()
                _log_worker_activity({
                    "id": str(uuid.uuid4())[:8],
                    "worker": None,
                    "filename": "[Index] project",
                    "scan_id": scan_id,
                    "scan_type": str(scan_type),
                    "started_at": datetime.utcnow().isoformat() + "Z",
                    "completed_at": datetime.utcnow().isoformat() + "Z",
                    "input_size": 0,
                    "input_preview": "",
                    "status": "error",
                    "findings_count": None,
                    "scan_status": None,
                    "error": str(e),
                })
        else:
            # Tier 2/3/4: run regex index and DeepWiki index in parallel
            try:
                _log_worker_activity({
                    "id": str(uuid.uuid4())[:8],
                    "worker": WORKER_NODES[0] if WORKER_NODES else None,
                    "filename": "[Index] project + DeepWiki",
                    "scan_id": scan_id,
                    "scan_type": str(scan_type),
                    "started_at": datetime.utcnow().isoformat() + "Z",
                    "completed_at": None,
                    "input_size": 0,
                    "input_preview": "Indexing in parallel (regex + DeepWiki)",
                    "status": "running",
                    "findings_count": None,
                    "scan_status": None,
                    "error": None,
                })
                with ThreadPoolExecutor(max_workers=2) as ex:
                    fut_regex = ex.submit(_run_regex_index)
                    fut_deepwiki = ex.submit(_run_deepwiki_index)
                    index_error = fut_regex.result()
                    deepwiki_error = fut_deepwiki.result()
                _log_worker_activity({
                    "id": str(uuid.uuid4())[:8],
                    "worker": ",".join(WORKER_NODES) if WORKER_NODES else None,
                    "filename": "[Index] project + DeepWiki",
                    "scan_id": scan_id,
                    "scan_type": str(scan_type),
                    "started_at": datetime.utcnow().isoformat() + "Z",
                    "completed_at": datetime.utcnow().isoformat() + "Z",
                    "input_size": 0,
                    "input_preview": "Done",
                    "status": "ok" if not (index_error or deepwiki_error) else "error",
                    "findings_count": None,
                    "scan_status": None,
                    "error": (index_error or deepwiki_error) and str(index_error or deepwiki_error),
                })
                if index_error:
                    print(f"[BACKEND] index_project_on_workers FAILED: {index_error}")
                    traceback.print_exc()
                if deepwiki_error:
                    print(f"[BACKEND] index_project_deepwiki_on_workers FAILED: {deepwiki_error}")
                    traceback.print_exc()
            except Exception as e:
                print(f"[BACKEND] parallel index FAILED: {e}")
                traceback.print_exc()
                _log_worker_activity({
                    "id": str(uuid.uuid4())[:8],
                    "worker": None,
                    "filename": "[Index] project + DeepWiki",
                    "scan_id": scan_id,
                    "scan_type": str(scan_type),
                    "started_at": datetime.utcnow().isoformat() + "Z",
                    "completed_at": datetime.utcnow().isoformat() + "Z",
                    "input_size": 0,
                    "input_preview": "",
                    "status": "error",
                    "findings_count": None,
                    "scan_status": None,
                    "error": str(e),
                })

        yield {'type': 'log', 'filename': 'SYSTEM', 'msg': 'Scanning files...'}

        # Build list of files to scan (same filters as below) and yield skip messages for large files
        files_to_scan = []
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
            files_to_scan.append((full_path, relative_path))

        # Preload file contents in parallel to avoid sequential I/O
        def _read_file(args):
            full_path, relative_path = args
            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                return (relative_path, content) if content.strip() else (relative_path, None)
            except Exception as e:
                return (relative_path, None, str(e))

        preload_workers = min(len(files_to_scan), MAX_WORKERS, 16)
        preloaded = []
        if files_to_scan and preload_workers > 0:
            with ThreadPoolExecutor(max_workers=preload_workers) as preload_ex:
                futures = [preload_ex.submit(_read_file, item) for item in files_to_scan]
                for fut in as_completed(futures):
                    result = fut.result()
                    if len(result) == 3:
                        yield {'type': 'log', 'filename': result[0], 'msg': f'Error: {result[2]}'}
                    elif result[1] is not None:
                        preloaded.append((result[0], result[1]))

        results = []
        files_scanned = 0
        executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
        future_map = {}

        for relative_path, content in preloaded:
            yield {'type': 'file_start', 'filename': relative_path}
            future = executor.submit(
                send_to_worker,
                os.path.basename(relative_path),
                content,
                scan_id,
                scan_type
            )
            future_map[future] = {"relative_path": relative_path, "content": content}

        total_files = len(future_map)
        for future in as_completed(future_map):
            meta = future_map[future]
            relative_path = meta["relative_path"]
            content = meta["content"]

            try:
                data = future.result()
                files_scanned += 1
            except Exception as e:
                traceback.print_exc()
                yield {'type': 'log', 'filename': relative_path, 'msg': f'Error: {str(e)}'}
                continue

            if not data:
                yield {'type': 'file_safe', 'filename': relative_path}
                yield {'type': 'progress', 'files_scanned': files_scanned, 'total_files': total_files, 'msg': f'Scanned {relative_path}'}
                continue

            for log in data.get('logs', []):
                yield {'type': 'log', 'filename': relative_path, 'msg': log}

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
                            issue["poc_verbal"] = {"vectors": v if isinstance(v, list) else ([v] if v else []), "steps": s if isinstance(s, list) else ([s] if s else [])}
                        else:
                            issue["poc_verbal"] = {"vectors": [], "steps": []}
                        issue["consequences"] = finding.get("consequences", "")
                        issue["references"] = finding.get("references", [])
                        issue["code_context"] = finding.get("code_context", {})
                        issue["fingerprint"] = finding.get("fingerprint", "")
                        issue["cvss_score"] = finding.get("cvss_score", 0.0)
                        issue["fix_complexity"] = finding.get("fix_complexity", "UNKNOWN")
                    structured_issues.append(issue)

                results.append({"filename": relative_path, "status": "VULNERABLE", "source_code": content, "issues": structured_issues})
                yield {'type': 'vuln_found', 'filename': relative_path, 'count': len(structured_issues), 'issues': structured_issues}
                yield {'type': 'progress', 'files_scanned': files_scanned, 'total_files': total_files, 'msg': f'Found {len(structured_issues)} issues in {relative_path}'}
            else:
                yield {'type': 'file_safe', 'filename': relative_path}
                yield {'type': 'progress', 'files_scanned': files_scanned, 'total_files': total_files, 'msg': f'Scanned {relative_path}'}

        executor.shutdown(wait=True)
        elapsed_seconds = time.time() - scan_start
        duration_msg = format_duration(elapsed_seconds)

        yield {'type': 'start', 'msg': 'Compiling final report...'}

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

        # Store DeepWiki doc in DB when available (so we don't rely on worker files)
        if SQL_ENABLED and database and WORKER_NODES and scan_type in ["2", "3", "4"]:
            try:
                res = requests.get(
                    f"{WORKER_NODES[0]}/deepwiki_docs",
                    headers={"x-secret": WORKER_SECRET, "x-scan-id": scan_id},
                    timeout=60,
                )
                if res.status_code == 200 and res.text:
                    database.update_scan_deepwiki(scan_id, res.text)
            except Exception as e:
                print(f"[BACKEND] Failed to store DeepWiki doc in DB: {e}")

        yield {'type': 'log', 'filename': 'SYSTEM', 'msg': f'Scan finished in {duration_msg}.'}
        yield {'type': 'complete', 'scan_id': scan_id}
        yield {'type': '_final', 'data': final_scan_data}

    except Exception as e:
        traceback.print_exc()
        yield {'type': 'log', 'filename': 'SYSTEM', 'msg': f'CRITICAL ERROR: {str(e)}'}
        yield {'type': '_final', 'data': None, 'error': str(e)}


@app.route('/api/scan/stream', methods=['POST'])
def scan_stream_endpoint():
    if 'files' not in request.files:
        return jsonify({"error": "No files"}), 400

    user_id = request.form.get('user_id', 'anonymous')
    project_name = request.form.get('project_name', 'Untitled Project')
    scan_type = request.form.get('scan_type', '1')
    files = request.files.getlist('files')

    scan_id = f"scan_{user_id}_{int(time.time())}"

    temp_dir = tempfile.mkdtemp()
    saved_files = []
    for file in files:
        safe_path = file.filename.lstrip('/')
        full_path = os.path.join(temp_dir, safe_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        file.save(full_path)
        saved_files.append((full_path, safe_path))

    @stream_with_context
    def generate():
        try:
            for evt in _run_scan_events(temp_dir, saved_files, user_id, project_name, scan_type, scan_id):
                yield f"data: {json.dumps(evt)}\n\n"
        finally:
            if temp_dir and os.path.isdir(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

    resp = Response(generate(), mimetype='text/event-stream')
    # Headers to avoid proxy buffering and HTTP/2 protocol errors with streaming
    resp.headers['Content-Type'] = 'text/event-stream; charset=utf-8'
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['X-Accel-Buffering'] = 'no'  # nginx: disable buffering
    resp.headers['Connection'] = 'keep-alive'
    return resp


@app.route('/api/scan', methods=['POST'])
def scan_no_stream_endpoint():
    """Non-streaming scan: same as /api/scan/stream but returns one JSON when done. Use when streaming fails (e.g. ERR_HTTP2_PROTOCOL_ERROR behind a proxy)."""
    if 'files' not in request.files:
        return jsonify({"error": "No files"}), 400

    user_id = request.form.get('user_id', 'anonymous')
    project_name = request.form.get('project_name', 'Untitled Project')
    scan_type = request.form.get('scan_type', '1')
    files = request.files.getlist('files')

    scan_id = f"scan_{user_id}_{int(time.time())}"

    temp_dir = tempfile.mkdtemp()
    saved_files = []
    for file in files:
        safe_path = file.filename.lstrip('/')
        full_path = os.path.join(temp_dir, safe_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        file.save(full_path)
        saved_files.append((full_path, safe_path))

    try:
        final_data = None
        for evt in _run_scan_events(temp_dir, saved_files, user_id, project_name, scan_type, scan_id):
            if evt.get('type') == '_final':
                final_data = evt.get('data')
                if evt.get('error'):
                    return jsonify({"error": evt["error"]}), 500

        if not final_data:
            return jsonify({"error": "Scan produced no result"}), 500

        return jsonify({
            "ok": True,
            "scan_id": final_data["scan_id"],
            "project_name": final_data["project_name"],
            "stats": final_data["stats"],
            "vulnerabilities": final_data.get("vulnerabilities", [])
        })
    finally:
        if temp_dir and os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)


def _run_scan_background(temp_dir, saved_files, user_id, project_name, scan_type, scan_id, event_log=None):
    """Run scan in background; write progress to _scan_progress and append each event to event_log for SSE (supports reconnection)."""
    vuln_count = [0]  # use list so inner closure can update

    def update(evt):
        with _scan_progress_lock:
            entry = _scan_progress.get(scan_id, {})
            if evt.get('type') == 'progress':
                fs = evt.get('files_scanned', 0)
                tf = evt.get('total_files', 1)
                entry['progress_pct'] = round(100 * fs / tf, 1) if tf else 0
                entry['message'] = evt.get('msg', '')
            elif evt.get('type') == 'vuln_found':
                vuln_count[0] += evt.get('count', 0)
                entry['vuln_count'] = vuln_count[0]
                entry['message'] = evt.get('msg', entry.get('message', ''))
            elif evt.get('type') in ('file_safe', 'file_start', 'log', 'start'):
                entry['message'] = evt.get('msg') or evt.get('filename') or str(evt.get('type', ''))
            entry['status'] = 'running'
            _scan_progress[scan_id] = entry

    def push(evt):
        if event_log is not None:
            try:
                with event_log["cond"]:
                    event_log["events"].append(evt)
                    event_log["cond"].notify_all()
            except Exception:
                pass

    try:
        for evt in _run_scan_events(temp_dir, saved_files, user_id, project_name, scan_type, scan_id):
            push(evt)
            if evt.get('type') == '_final':
                with _scan_progress_lock:
                    prev = _scan_progress.get(scan_id, {})
                    _ts = prev.get('_ts', time.time())
                    if evt.get('error'):
                        _scan_progress[scan_id] = {'status': 'error', 'message': evt.get('error', 'Unknown error'), 'result': None, '_ts': _ts}
                    else:
                        data = evt.get('data')
                        _scan_progress[scan_id] = {
                            'status': 'done',
                            'message': 'Scan complete!',
                            'progress_pct': 100,
                            'vuln_count': len(data.get('vulnerabilities', [])) if data else 0,
                            'result': data,
                            '_ts': _ts
                        }
                    # trim old entries
                    if len(_scan_progress) > MAX_SCAN_PROGRESS_ENTRIES:
                        keys = sorted(_scan_progress.keys(), key=lambda k: _scan_progress[k].get('_ts', 0))[:len(_scan_progress) - MAX_SCAN_PROGRESS_ENTRIES]
                        for k in keys:
                            _scan_progress.pop(k, None)
                break
            elif evt.get('type') != '_final':
                update(evt)
    except Exception as e:
        traceback.print_exc()
        with _scan_progress_lock:
            _scan_progress[scan_id] = {'status': 'error', 'message': str(e), 'result': None}
    finally:
        if event_log is not None:
            try:
                with event_log["cond"]:
                    event_log["done"] = True
                    event_log["cond"].notify_all()
            except Exception:
                pass
        with _scan_event_log_lock:
            _scan_event_log.pop(scan_id, None)
        try:
            if temp_dir and os.path.isdir(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass


@app.route('/api/scan/start', methods=['POST'])
def scan_start_async():
    """Start scan in background; returns scan_id immediately. Poll GET /api/scan/status/<scan_id> for progress."""
    if 'files' not in request.files:
        return jsonify({"error": "No files"}), 400

    user_id = request.form.get('user_id', 'anonymous')
    project_name = request.form.get('project_name', 'Untitled Project')
    scan_type = request.form.get('scan_type', '1')
    files = request.files.getlist('files')

    scan_id = f"scan_{user_id}_{int(time.time())}"

    temp_dir = tempfile.mkdtemp()
    saved_files = []
    for file in files:
        safe_path = file.filename.lstrip('/')
        full_path = os.path.join(temp_dir, safe_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        file.save(full_path)
        saved_files.append((full_path, safe_path))

    with _scan_progress_lock:
        _scan_progress[scan_id] = {'status': 'running', 'message': 'Initializing...', 'progress_pct': 0, 'vuln_count': 0, '_ts': time.time()}

    event_log = {"events": [], "cond": threading.Condition(), "done": False}
    with _scan_event_log_lock:
        _scan_event_log[scan_id] = event_log

    t = threading.Thread(
        target=_run_scan_background,
        args=(temp_dir, saved_files, user_id, project_name, scan_type, scan_id, event_log),
        daemon=True
    )
    t.start()

    return jsonify({"scan_id": scan_id})


@app.route('/api/scan/status/<path:scan_id>', methods=['GET'])
def scan_status(scan_id):
    """Return current progress for an async scan. Use path so scan_id is never truncated."""
    with _scan_progress_lock:
        entry = _scan_progress.get(scan_id, {})
    if not entry:
        # Not found yet (e.g. just started) or expired: return 200 with pending so client keeps polling
        return jsonify({
            "status": "pending",
            "message": "Scan starting or not found. Keep polling.",
            "progress_pct": 0,
            "vuln_count": 0,
        })
    out = {k: v for k, v in entry.items() if k != '_ts'}
    return jsonify(out)


@app.route('/api/scan/events/<path:scan_id>', methods=['GET'])
def scan_events_sse(scan_id):
    """SSE stream: replay event log from start then stream new events. Supports reconnection (multiple clients get same events)."""
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
        finally:
            pass

    resp = Response(generate(), mimetype='text/event-stream')
    resp.headers['Content-Type'] = 'text/event-stream; charset=utf-8'
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['X-Accel-Buffering'] = 'no'
    resp.headers['Connection'] = 'keep-alive'
    return resp


@app.route('/api/scan/pocs', methods=['POST'])
def generate_pocs_for_scan():
    """
    Tier 4: Generate PoCs for selected findings in a completed scan.
    Request JSON:
    {
      "user_id": "...",
      "project_name": "...",
      "scan_id": "...",
      "fingerprints": ["fp1", "fp2"]  # optional; if empty, we can pick all/highest severity
    }
    """
    data = request.get_json(force=True)
    user_id = data.get("user_id")
    project_name = data.get("project_name")
    scan_id = data.get("scan_id")
    requested_fps = data.get("fingerprints", [])

    if not (user_id and project_name and scan_id):
        return jsonify({"error": "Missing user_id, project_name, or scan_id"}), 400

    # Get scan data from database
    target_scan = get_scan_from_db(user_id, project_name, scan_id)
    if not target_scan:
        return jsonify({"error": "Scan not found"}), 404

    # Collect issues that need PoCs
    issues_needing_poc = []
    for v in target_scan.get("vulnerabilities", []):
        filename = v.get("filename")
        source_code = v.get("source_code", "")
        for issue in v.get("issues", []):
            fp = issue.get("fingerprint")
            # Skip if SCRIPT PoC already exists
            if issue.get("poc_script"):
                continue
            # If specific fingerprints requested, filter by them
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

    # Group by filename so we can call worker once per file
    from collections import defaultdict
    per_file = defaultdict(list)
    per_file_source = {}

    for f in issues_needing_poc:
        fname = f.pop("_filename")
        src = f.pop("_source_code")
        per_file[fname].append(f)
        per_file_source[fname] = src

    poc_map = {}

    for fname, findings in per_file.items():
        poc_data = request_pocs_from_worker(
            fname,
            per_file_source[fname],
            findings,
            scan_id,
            max_pocs=len(findings)  # or cap this to 1–2 for speed
        )
        if not poc_data or poc_data.get("status") != "OK":
            continue

        for f in poc_data.get("findings", []):
            fp = f.get("fingerprint")
            poc = f.get("poc")
            if fp and isinstance(poc, dict):
                poc_map[fp] = poc
                # Update in database
                update_poc_in_db(scan_id, fp, poc)

    if poc_map:
        return jsonify({"status": "OK", "poc_map": poc_map})

    return jsonify({"error": "PoC generation failed or returned nothing"}), 500

@app.route("/api/scan/docs/<scan_id>", methods=["GET"])
def get_scan_docs(scan_id):
    """Return DeepWiki docs for the scan (from DB if stored, else from worker)."""
    user_id = request.args.get("user_id")
    # Derive user_id from scan_id when format is scan_{user_id}_{timestamp}
    if not user_id and scan_id.startswith("scan_") and scan_id.count("_") >= 2:
        user_id = scan_id[5:scan_id.rfind("_")]
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    # Verify user owns this scan
    if not scan_exists_for_user(user_id, scan_id):
        return jsonify({"error": "Scan not found"}), 404

    # Prefer doc stored in DB (single source of truth, no worker files needed)
    if SQL_ENABLED and database:
        doc = database.get_scan_deepwiki(scan_id)
        if doc:
            return Response(doc, mimetype="text/plain; charset=utf-8")

    # Fallback: fetch from worker (e.g. old scans before we stored in DB)
    try:
        worker_url = WORKER_NODES[0]
        res = requests.get(
            f"{worker_url}/deepwiki_docs",
            headers={
                "x-secret": WORKER_SECRET,
                "x-scan-id": scan_id
            },
            timeout=60
        )
        if res.status_code != 200:
            return jsonify({"error": "No DeepWiki docs", "status": res.status_code}), res.status_code

        return Response(res.text, mimetype="text/plain; charset=utf-8")
    except Exception as e:
        print("[BACKEND] get_scan_docs error:", e)
        return jsonify({"error": "Internal error"}), 500

@app.route('/api/projects/<user_id>', methods=['GET'])
def get_projects(user_id):
    """Get all projects for a user (from SQL when enabled). Returns [] if none; add debug hint when empty."""
    projects = get_projects_from_db(user_id)
    if not projects and SQL_ENABLED and database:
        # Help debug "empty": show which user_id was queried (scans are stored under the user_id sent at scan start)
        return jsonify({
            "projects": [],
            "debug": {
                "queried_user_id": user_id,
                "hint": "Scans are stored under the user_id sent when starting the scan. If you used 'anonymous' or a different id, try that id, or run a new scan while signed in."
            }
        })
    return jsonify(projects)


# NEW: Download PoC script by user_id + scan_id + fingerprint
@app.route('/api/poc/<user_id>/<scan_id>/<fingerprint>', methods=['GET'])
def download_poc(user_id, scan_id, fingerprint):
    """Download PoC script by fingerprint"""
    poc = get_poc_from_db(user_id, scan_id, fingerprint)
    
    if not poc:
        return jsonify({"error": "PoC not found"}), 404

    poc_script = poc.get("script")
    language = poc.get("language", "text")

    # Decide extension by language
    if language == "python":
        filename = f"poc_{fingerprint}.py"
    elif language in ("javascript", "node", "js"):
        filename = f"poc_{fingerprint}.js"
    else:
        filename = f"poc_{fingerprint}.txt"

    buf = BytesIO(poc_script.encode("utf-8"))
    resp = make_response(buf.getvalue())
    resp.headers["Content-Type"] = "text/plain; charset=utf-8"
    resp.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp


# Admin: worker activity for admin page
@app.route('/api/admin/worker-activity', methods=['GET'])
def get_worker_activity():
    """Return worker nodes and recent activity (input/output) for admin view."""
    with _worker_activity_lock:
        activity = list(_worker_activity)
    activity.reverse()  # newest first
    return jsonify({
        "workers": WORKER_NODES,
        "max_parallel_workers": MAX_WORKERS,
        "activity": activity,
    })


@app.route('/api/admin/worker-activity/stream', methods=['GET'])
def get_worker_activity_stream():
    """SSE stream of worker activity. Sends a snapshot every 3 seconds."""
    def generate():
        interval = 3.0
        while True:
            with _worker_activity_lock:
                activity = list(_worker_activity)
            activity.reverse()
            payload = json.dumps({
                "workers": WORKER_NODES,
                "max_parallel_workers": MAX_WORKERS,
                "activity": activity,
            })
            yield f"data: {payload}\n\n"
            time.sleep(interval)

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# NEW: Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Check database and worker health"""
    # Check database
    db_status = "healthy" if (SQL_ENABLED and database) else "json-fallback"
    
    # Check workers
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
        "version": "2.0-sql",
        "port": PORT
    })


# NEW: Get scan details endpoint
@app.route('/api/scan/<user_id>/<project_name>/<scan_id>', methods=['GET'])
def get_scan_details(user_id, project_name, scan_id):
    """Get full scan details"""
    scan_data = get_scan_from_db(user_id, project_name, scan_id)
    if not scan_data:
        return jsonify({"error": "Scan not found"}), 404
    
    return jsonify(scan_data)


if __name__ == "__main__":
    print(f"[INFO] Sentinel Backend (SQL Edition)")
    print(f"[INFO] Database: {DB_URL}")
    print(f"[INFO] SQL Enabled: {SQL_ENABLED}")
    print(f"[INFO] Running on http://localhost:{PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=True, threaded=True, use_reloader=False)
