"""
Sentinel AI Backend - SQL Version
Updated backend with SQL database support
"""

import os
import sys
import time
import requests
import random
import json
import tempfile
import traceback
from io import BytesIO
from flask import Flask, request, jsonify, Response, stream_with_context, make_response
from flask_cors import CORS
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import init_database, db
from backend.database.operations import Database

app = Flask(__name__)
CORS(app)

# Configuration
DB_URL = os.environ.get('DATABASE_URL', 'sqlite:///sentinel.db')
WORKER_NODES = [u.strip() for u in os.environ.get('WORKER_NODES', 'http://127.0.0.1:5002').split(',') if u.strip()]
WORKER_SECRET = os.environ.get('WORKER_SECRET', '109002104049989hcjh')
MAX_WORKERS = int(os.environ.get('MAX_WORKERS', '12'))
MAX_FILE_SIZE_BYTES = int(os.environ.get('MAX_FILE_SIZE_BYTES', '1000000'))  # 1MB

VALID_EXTENSIONS = {
    '.py', '.js', '.ts', '.html', '.php', '.java', '.c', '.cpp', '.go', '.rb', 'ejs',
    '.tsx', '.jsx', '.vue', '.rs', '.kt', '.swift', '.sol',
    '.yaml', '.yml', '.dockerfile', 'Dockerfile', '.json', '.xml', '.sql', '.env', '.config'
}
IGNORE_DIRS = {'__pycache__', '.git', 'node_modules', 'venv', 'env', '.idea', '.vscode', 'dist', 'build', 'coverage', 'public', 'assets', 'static', 'media', 'uploads', 'vendor', 'target', 'bin', 'obj'}
IGNORED_FILENAMES = {'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'Cargo.lock', 'go.sum'}
CONFIG_FILES = {'package.json', 'requirements.txt', 'pyproject.toml', 'go.mod', 'README.md'}

ANALYSIS_PROMPT = """
You are an Elite Security Architect. Analyze this project structure.
RETURN THIS EXACT JSON STRUCTURE:
{
    "project_info": {"name": "...", "framework": "...", "description": "..."},
    "security_context": {"has_authentication": true, "has_database": true, "external_apis": []},
    "risk_summary": {"top_concerns": []}
}
"""

# Initialize database on startup
database = None

def init_db():
    """Initialize database connection"""
    global database
    database = init_database(DB_URL)
    print(f"✅ Database initialized: {DB_URL}")


# ================= DATABASE HELPERS (Replaced from JSON) =================

def load_db():
    """Legacy compatibility - returns database object"""
    return database


def save_db(data):
    """Legacy compatibility - no-op for SQL"""
    pass  # Not needed with SQL


def save_scan_result(user_id, project_name, scan_data):
    """Save scan result to SQL database"""
    return database.save_scan(user_id, project_name, scan_data)


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
    first_node = _next_worker_node()
    if not first_node:
        print("[BACKEND] No worker nodes configured")
        return None
    nodes = [first_node] + [n for n in WORKER_NODES if n != first_node]

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
                        print(f"\n===== DEBUG WORKER RESPONSE ({filename}) =====")
                        print(json.dumps(data, indent=2)[:4000])
                        print("=============================================\n")
                        return data
                    except json.JSONDecodeError:
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
            break

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
    """Format duration in human-readable format"""
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"

    minutes, secs = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}m {secs}s"

    hours, mins = divmod(minutes, 60)
    return f"{hours}h {mins}m {secs}s"


def index_project_on_workers(target_folder, scan_id):
    """Indexes ALL valid files on the worker with SCAN ID. Uses relative paths so multiple files with the same name (e.g. page.tsx in different folders) are all indexed."""
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
                    rel_path = os.path.relpath(full_path, target_folder)
                    rel_path = rel_path.replace(os.sep, '/')
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        files_payload.append({"filename": rel_path, "content": f.read()})
                except Exception:
                    pass

    if files_payload:
        for node in WORKER_NODES:
            try:
                requests.post(
                    f"{node}/index_project",
                    json={"files": files_payload},
                    headers={"x-secret": WORKER_SECRET, "x-scan-id": scan_id},
                    timeout=60
                )
            except Exception as e:
                print(f"[BACKEND] index_project error on {node}: {e}")
                pass


def index_project_deepwiki_on_workers(target_folder, scan_id):
    """Builds LLM (DeepWiki) index on the worker with SCAN ID. Uses relative paths so multiple files with the same name (e.g. page.tsx in different routes) are all included."""
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
                    rel_path = os.path.relpath(full_path, target_folder)
                    rel_path = rel_path.replace(os.sep, '/')
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        files_payload.append({"filename": rel_path, "content": f.read()})
                except Exception:
                    pass

    if files_payload:
        for node in WORKER_NODES:
            try:
                print(f"[BACKEND] Sending DeepWiki index request to {node}/index_project_deepwiki")
                res = requests.post(
                    f"{node}/index_project_deepwiki",
                    json={"files": files_payload},
                    headers={"x-secret": WORKER_SECRET, "x-scan-id": scan_id},
                    timeout=600
                )
                print(f"[BACKEND] DeepWiki index HTTP status: {res.status_code}")
            except Exception as e:
                print(f"[BACKEND] DeepWiki index error on {node}: {e}")
                pass


def analyze_project_structure(target_folder):
    """Analyze project structure via worker"""
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

@app.route('/api/scan/stream', methods=['POST'])
def scan_stream_endpoint():
    """Streaming scan endpoint"""
    if 'files' not in request.files:
        return jsonify({"error": "No files"}), 400

    user_id = request.form.get('user_id', 'anonymous')
    project_name = request.form.get('project_name', 'Untitled Project')
    scan_type = request.form.get('scan_type', '1')
    files = request.files.getlist('files')

    # Generate unique scan ID
    scan_id = f"scan_{user_id}_{int(time.time())}"

    # Ensure user exists in database
    database.get_or_create_user(user_id)

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
        scan_start = time.time()
        try:
            yield f"data: {json.dumps({'type': 'start', 'msg': f'Initializing Tier {scan_type} Scan...'})}\n\n"

            # Only analyze structure if requested or if it's a deeper scan
            if scan_type in ["2", "3"]:
                yield f"data: {json.dumps({'type': 'start', 'msg': 'Analyzing project architecture...'})}\n\n"
                analysis = analyze_project_structure(temp_dir)
            else:
                analysis = {}

            # Run indexing silently and ignore failures
            try:
                index_project_on_workers(temp_dir, scan_id)
            except Exception as e:
                print(f"[BACKEND] index_project_on_workers FAILED: {e}")
                traceback.print_exc()

            if scan_type in ["2", "3"]:
                try:
                    index_project_deepwiki_on_workers(temp_dir, scan_id)
                except Exception as e:
                    print(f"[BACKEND] index_project_deepwiki_on_workers FAILED: {e}")
                    traceback.print_exc()

            results = []
            files_scanned = 0

            # Parallel file scanning
            executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
            future_map = {}

            # Submit tasks
            for full_path, relative_path in saved_files:
                ext = os.path.splitext(full_path)[1]
                if ext not in VALID_EXTENSIONS or os.path.basename(full_path) in IGNORED_FILENAMES:
                    continue

                # Check file size
                try:
                    if os.path.getsize(full_path) > MAX_FILE_SIZE_BYTES:
                        yield f"data: {json.dumps({'type': 'log', 'filename': relative_path, 'msg': 'Skipped: File too large (>1MB)'})}\n\n"
                        continue
                except OSError:
                    yield f"data: {json.dumps({'type': 'log', 'filename': relative_path, 'msg': 'Skipped: Unable to read file size'})}\n\n"
                    continue

                # Tell frontend this file is starting
                yield f"data: {json.dumps({'type': 'file_start', 'filename': relative_path})}\n\n"

                # Read content once here
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except Exception as e:
                    traceback.print_exc()
                    yield f"data: {json.dumps({'type': 'log', 'filename': relative_path, 'msg': f'Error: {str(e)}'})}\n\n"
                    continue

                if not content.strip():
                    continue

                future = executor.submit(
                    send_to_worker,
                    os.path.basename(relative_path),
                    content,
                    scan_id,
                    scan_type
                )
                future_map[future] = {
                    "relative_path": relative_path,
                    "content": content
                }

            # Consume as they finish
            for future in as_completed(future_map):
                meta = future_map[future]
                relative_path = meta["relative_path"]
                content = meta["content"]

                try:
                    data = future.result()
                    files_scanned += 1
                except Exception as e:
                    traceback.print_exc()
                    yield f"data: {json.dumps({'type': 'log', 'filename': relative_path, 'msg': f'Error: {str(e)}'})}\n\n"
                    continue

                if not data:
                    yield f"data: {json.dumps({'type': 'file_safe', 'filename': relative_path})}\n\n"
                    continue

                worker_logs = data.get('logs', [])
                for log in worker_logs:
                    yield f"data: {json.dumps({'type': 'log', 'filename': relative_path, 'msg': log})}\n\n"

                if data.get("status") == "VULNERABLE":
                    worker_findings = data.get("findings", [])
                    structured_issues = []

                    for finding in worker_findings:
                        # Base fields (Tier 1)
                        issue = {
                            "severity": finding.get("severity", "HIGH"),
                            "type": finding.get("type", "Unknown"),
                            "trigger": finding.get("function_name", "Unknown"),
                            "line": finding.get("line", 1),
                            "description": finding.get("reason", "..."),
                            "vulnerable_code": finding.get("vulnerable_code", "")
                        }

                        # Tier 2 Fields (Standard)
                        if scan_type in ["2", "3"]:
                            issue["subtype"] = finding.get("subtype", "")
                            issue["impact_summary"] = finding.get("impact_summary", "")
                            issue["keywords_detected"] = finding.get("keywords_detected", [])
                            issue["confidence_score"] = finding.get("confidence_score", 0)
                            issue["cwe_id"] = finding.get("cwe_id", "")

                        # Tier 3 Fields (Advanced)
                        if scan_type == "3":
                            raw_rem = finding.get("remediation", [])
                            if isinstance(raw_rem, str):
                                issue["remediation"] = [raw_rem]
                            elif isinstance(raw_rem, list):
                                issue["remediation"] = raw_rem
                            else:
                                issue["remediation"] = []

                            raw_poc = finding.get("poc")
                            if isinstance(raw_poc, dict):
                                vectors = raw_poc.get("vectors")
                                steps = raw_poc.get("steps")
                                if not isinstance(vectors, list):
                                    vectors = [vectors] if vectors else []
                                if not isinstance(steps, list):
                                    steps = [steps] if steps else []
                                issue["poc_verbal"] = {
                                    "vectors": vectors,
                                    "steps": steps
                                }
                            else:
                                issue["poc_verbal"] = {
                                    "vectors": [],
                                    "steps": []
                                }

                            issue["consequences"] = finding.get("consequences", "")
                            issue["references"] = finding.get("references", [])
                            issue["code_context"] = finding.get("code_context", {})
                            issue["fingerprint"] = finding.get("fingerprint", "")
                            issue["cvss_score"] = finding.get("cvss_score", 0.0)
                            issue["fix_complexity"] = finding.get("fix_complexity", "UNKNOWN")

                        structured_issues.append(issue)

                    file_result = {
                        "filename": relative_path,
                        "status": "VULNERABLE",
                        "source_code": content,
                        "issues": structured_issues
                    }
                    results.append(file_result)

                    yield f"data: {json.dumps({'type': 'vuln_found', 'filename': relative_path, 'count': len(structured_issues), 'issues': structured_issues})}\n\n"
                else:
                    yield f"data: {json.dumps({'type': 'file_safe', 'filename': relative_path})}\n\n"

            executor.shutdown(wait=True)

            # Timing block
            scan_end = time.time()
            elapsed_seconds = scan_end - scan_start
            duration_msg = format_duration(elapsed_seconds)

            yield f"data: {json.dumps({'type': 'start', 'msg': 'Compiling final report...'})}\n\n"

            final_scan_data = {
                "scan_id": scan_id,
                "scan_type": scan_type,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "stats": {
                    "files_scanned": files_scanned,
                    "vulnerabilities": len(results),
                    "elapsed_seconds": elapsed_seconds
                },
                "project_analysis": analysis if analysis else {},
                "vulnerabilities": results,
                "project_name": project_name
            }
            
            # Save to SQL database
            save_scan_result(user_id, project_name, final_scan_data)

            yield f"data: {json.dumps({'type': 'log', 'filename': 'SYSTEM', 'msg': f'Scan finished in {duration_msg}.'})}\n\n"
            yield f"data: {json.dumps({'type': 'complete', 'scan_id': scan_id})}\n\n"

        except Exception as e:
            traceback.print_exc()
            yield f"data: {json.dumps({'type': 'log', 'filename': 'SYSTEM', 'msg': f'CRITICAL ERROR: {str(e)}'})}\n\n"

    return Response(generate(), mimetype='text/event-stream')


@app.route('/api/scan/pocs', methods=['POST'])
def generate_pocs_for_scan():
    """
    Tier 4: Generate PoCs for selected findings in a completed scan.
    """
    data = request.get_json(force=True)
    user_id = data.get("user_id")
    project_name = data.get("project_name")
    scan_id = data.get("scan_id")
    requested_fps = data.get("fingerprints", [])

    if not (user_id and project_name and scan_id):
        return jsonify({"error": "Missing user_id, project_name, or scan_id"}), 400

    # Verify scan exists and belongs to user
    scan = database.get_scan_by_user_project(user_id, project_name, scan_id)
    if not scan:
        return jsonify({"error": "Scan not found"}), 404

    # Export scan data to dict for processing
    scan_data = database.export_scan_to_dict(scan_id)
    if not scan_data:
        return jsonify({"error": "Failed to export scan data"}), 500

    # Collect issues that need PoCs
    issues_needing_poc = []
    for v in scan_data.get("vulnerabilities", []):
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

    # Group by filename
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
            max_pocs=len(findings)
        )
        if not poc_data or poc_data.get("status") != "OK":
            continue

        for f in poc_data.get("findings", []):
            fp = f.get("fingerprint")
            poc = f.get("poc")
            if fp and isinstance(poc, dict):
                poc_map[fp] = poc
                # Update in database
                database.update_issue_poc(fp, poc)

    if poc_map:
        return jsonify({"status": "OK", "poc_map": poc_map})

    return jsonify({"error": "PoC generation failed or returned nothing"}), 500


@app.route("/api/scan/docs/<scan_id>", methods=["GET"])
def get_scan_docs(scan_id):
    """Get DeepWiki docs for a scan"""
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    # Verify user owns this scan
    if not database.scan_exists_for_user(user_id, scan_id):
        return jsonify({"error": "Scan not found"}), 404

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

        return Response(res.text, mimetype="text/plain")
    except Exception as e:
        print("[BACKEND] get_scan_docs error:", e)
        return jsonify({"error": "Internal error"}), 500


@app.route('/api/projects/<user_id>', methods=['GET'])
def get_projects(user_id):
    """Get all projects for a user"""
    projects = database.get_user_projects(user_id)
    return jsonify(projects)


@app.route('/api/scans/<user_id>/<project_name>', methods=['GET'])
def get_project_scans(user_id, project_name):
    """Get all scans for a specific project"""
    project = database.get_project(user_id, project_name)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    
    # Get scans for this project
    with database.get_session() as session:
        from database.models import Scan
        scans = session.query(Scan).filter_by(project_id=project.id).order_by(Scan.timestamp.desc()).all()
        return jsonify([{
            "scan_id": s.id,
            "scan_type": s.scan_type,
            "timestamp": s.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "stats": {
                "files_scanned": s.files_scanned,
                "vulnerabilities": s.vulnerabilities_count,
                "elapsed_seconds": s.elapsed_seconds
            }
        } for s in scans])


@app.route('/api/scan/<user_id>/<project_name>/<scan_id>', methods=['GET'])
def get_scan_details(user_id, project_name, scan_id):
    """Get full scan details"""
    scan_data = database.export_scan_to_dict(scan_id)
    if not scan_data:
        return jsonify({"error": "Scan not found"}), 404
    
    # Verify ownership
    if not database.scan_exists_for_user(user_id, scan_id):
        return jsonify({"error": "Scan not found"}), 404
    
    return jsonify(scan_data)


@app.route('/api/poc/<user_id>/<scan_id>/<fingerprint>', methods=['GET'])
def download_poc(user_id, scan_id, fingerprint):
    """Download PoC script by fingerprint"""
    poc = database.get_poc_by_fingerprint(user_id, scan_id, fingerprint)
    
    if not poc:
        return jsonify({"error": "PoC not found"}), 404

    # Decide extension by language
    if poc.language == "python":
        filename = f"poc_{fingerprint}.py"
    elif poc.language in ("javascript", "node", "js"):
        filename = f"poc_{fingerprint}.js"
    else:
        filename = f"poc_{fingerprint}.txt"

    buf = BytesIO(poc.script.encode("utf-8"))
    resp = make_response(buf.getvalue())
    resp.headers["Content-Type"] = "text/plain; charset=utf-8"
    resp.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp


# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Check database and worker health"""
    try:
        # Check database
        with database.get_session() as session:
            from database.models import User
            session.query(User).first()
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
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
        "workers": worker_status,
        "version": "2.0-sql"
    })


if __name__ == "__main__":
    print("🔥 Initializing Sentinel SQL Backend...")
    init_db()
    print(f"🔥 Running on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)
