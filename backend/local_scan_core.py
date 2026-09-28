"""
Local folder scan without Flask gateway or HTTP to the worker: async calls into
``backend.worker.core.main`` (index, analyze, per-file ``scan_code_pipeline``, cross-file).

Import this only after ``sys.path`` bootstrap (see ``local_scan_server.py``).
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import sys
import time
import uuid
from typing import Any, Callable, Dict, List, Optional, Tuple

_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_BACKEND_DIR, ".."))
_WORKER_CORE_DIR = os.path.join(_BACKEND_DIR, "worker", "core")
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
if _BACKEND_DIR not in sys.path:
    sys.path.append(_BACKEND_DIR)
if _WORKER_CORE_DIR not in sys.path:
    sys.path.insert(0, _WORKER_CORE_DIR)

import aiohttp
from fastapi import HTTPException
from starlette.requests import Request

from backend.findings_md_generator import generate_findings_md
from backend.worker.core.main import (
    WORKER_SECRET,
    analyze_project,
    cross_file_consistency,
    index_project,
    index_project_deepwiki,
    scan_code_pipeline,
)
from backend.worker.core.models import (
    AnalyzeRequest,
    CrossFileConsistencyRequest,
    DeepWikiIndexRequest,
    FileData,
    IndexRequest,
    ScanRequest,
)
from backend.worker.core.output.sarif_emitter import SARIFEmitter
from backend.worker.core.redis_client import redis_client

logger = logging.getLogger(__name__)

VALID_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".html",
    ".php",
    ".java",
    ".c",
    ".cpp",
    ".go",
    ".rb",
    ".tsx",
    ".jsx",
    ".vue",
    ".rs",
    ".kt",
    ".swift",
    ".sol",
    ".ejs",
    ".yaml",
    ".yml",
    ".dockerfile",
    "Dockerfile",
    ".json",
    ".xml",
    ".sql",
    ".env",
    ".config",
}
IGNORE_DIRS = {
    "__pycache__",
    ".git",
    "node_modules",
    "venv",
    "env",
    ".idea",
    ".vscode",
    "dist",
    "build",
    "coverage",
    "public",
    "assets",
    "static",
    "media",
    "uploads",
    "vendor",
    "target",
    "bin",
    "obj",
}
IGNORED_FILENAMES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "Cargo.lock",
    "go.sum",
}
CONFIG_FILES = {
    "package.json",
    "requirements.txt",
    "pyproject.toml",
    "go.mod",
    "README.md",
}
MAX_FILE_SIZE_BYTES = 1_000_000

ANALYSIS_PROMPT = """
You are an Elite Security Architect. Analyze this project structure.
RETURN THIS EXACT JSON STRUCTURE:
{
    "project_info": {"name": "...", "framework": "...", "description": "..."},
    "security_context": {"has_authentication": true, "has_database": true, "external_apis": []},
    "risk_summary": {"top_concerns": []}
}
"""


def _file_sha1(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8", errors="ignore")).hexdigest()


def collect_index_file_data(target_folder: str) -> List[FileData]:
    """Files eligible for indexing (same rules as gateway ``_build_worker_files_payload``)."""
    out: List[FileData] = []
    target_folder = os.path.abspath(target_folder)
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
                    rel_path = os.path.relpath(full_path, target_folder).replace(os.sep, "/")
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    out.append(
                        FileData(filename=rel_path, content=content, sha1=_file_sha1(content))
                    )
                except OSError:
                    pass
    return out


def collect_scan_file_pairs(target_folder: str) -> List[Tuple[str, str]]:
    """(full_path, relative_posix) for per-file scan (extension filter, like ``_run_scan_events``)."""
    pairs: List[Tuple[str, str]] = []
    target_folder = os.path.abspath(target_folder)
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
                    rel = os.path.relpath(full_path, target_folder).replace(os.sep, "/")
                    pairs.append((full_path, rel))
                except ValueError:
                    pass
    return pairs


def _make_project_key(user_id: str, project_name: str, rel_paths: List[str]) -> str:
    fingerprint = "|".join(sorted(rel_paths))
    raw = f"{user_id}:{project_name}:{fingerprint}"
    return "project:" + hashlib.sha1(raw.encode("utf-8", errors="ignore")).hexdigest()


def _format_duration(seconds: float) -> str:
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"
    minutes, secs = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}m {secs}s"
    hours, mins = divmod(minutes, 60)
    return f"{hours}h {mins}m {secs}s"


def _worker_finding_to_issue_dict(finding: dict, scan_type: str) -> dict:
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
    for key in (
        "validation_status",
        "_fp_soft_flag",
        "_below_threshold_note",
        "_cross_file_flag",
        "_removal_rule",
    ):
        if finding.get(key) is not None:
            issue[key] = finding[key]
    return issue


async def _merge_agent_findings_async(scan_id: str, results: list, scan_type: str) -> None:
    """Poll Redis for agent findings without blocking the event loop."""
    if scan_type not in ["2", "3", "4"] or not results:
        return
    deadline = time.time() + 120.0
    raw = None
    while time.time() < deadline:
        try:
            raw = redis_client.get(f"{scan_id}:agent_findings")
        except Exception as e:
            logger.warning("Redis agent_findings read failed: %s", e)
            return
        if raw:
            break
        await asyncio.sleep(0.5)
    if not raw:
        return
    try:
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        agent_findings = json.loads(raw)
    except Exception as e:
        logger.warning("agent_findings JSON parse failed: %s", e)
        return
    if not isinstance(agent_findings, list) or not agent_findings:
        return
    mapped = [
        _worker_finding_to_issue_dict(f, scan_type) for f in agent_findings if isinstance(f, dict)
    ]
    if not mapped:
        return
    for r in results:
        r.setdefault("issues", []).extend(mapped)
        if r.get("status") != "VULNERABLE":
            r["status"] = "VULNERABLE"
    logger.info(
        "Merged %s agent findings into %s result rows (post-scan)", len(mapped), len(results)
    )


def _make_dummy_request(app: Any) -> Request:
    scope = {
        "type": "http",
        "asgi": {"spec_version": "2.3", "version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/local",
        "raw_path": b"/local",
        "query_string": b"",
        "headers": [],
        "client": ("127.0.0.1", 0),
        "server": ("127.0.0.1", 80),
        "app": app,
    }
    return Request(scope)


def save_scan_artifacts(scan_id: str, scan_data: Optional[dict], output_base: str) -> None:
    if not scan_id or scan_data is None:
        return
    scan_dir = os.path.join(output_base, scan_id)
    os.makedirs(scan_dir, exist_ok=True)
    result_path = os.path.join(scan_dir, "result.json")
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(scan_data, f, indent=2, ensure_ascii=False)
    logger.info("Wrote %s", result_path)
    try:
        SARIFEmitter(tool_name="SentinelAI", tool_version="2.0").emit(
            scan_data, os.path.join(scan_dir, "result.sarif")
        )
    except Exception as e:
        logger.warning("SARIF emit failed: %s", e)
    try:
        generate_findings_md(scan_data, os.path.join(scan_dir, "findings.md"))
    except Exception as e:
        logger.warning("findings.md failed: %s", e)


def _row_from_worker_response(
    data: dict, relative_path: str, content: str, scan_type: str
) -> dict:
    if data.get("status") == "VULNERABLE":
        worker_findings = data.get("findings", [])
        structured_issues = [_worker_finding_to_issue_dict(f, scan_type) for f in worker_findings]
        return {
            "filename": relative_path,
            "status": "VULNERABLE",
            "source_code": content,
            "issues": structured_issues,
        }
    if data.get("status") == "NOT_SCANNED" or data.get("skipped"):
        return {
            "filename": relative_path,
            "status": "NOT_SCANNED",
            "skipped": True,
            "skip_reason": data.get("skip_reason", "Low risk score"),
            "risk_score": data.get("risk_score"),
            "source_code": content,
            "issues": [],
        }
    return {"filename": relative_path, "status": "SAFE", "source_code": content, "issues": []}


async def run_local_folder_scan_async(
    worker_app: Any,
    source_dir: str,
    output_dir: str,
    scan_type: str = "2",
    project_name: str = "Local folder",
    user_id: str = "local",
    progress: Optional[Callable[[dict], None]] = None,
) -> dict:
    """
    Run full pipeline with ``worker_app.state.session`` set to a live ``aiohttp.ClientSession``.
    Caller must enter this inside ``async with aiohttp.ClientSession() as session: worker_app.state.session = session``.
    """
    source_dir = os.path.abspath(source_dir)
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    scan_id = f"local_{int(time.time())}_{uuid.uuid4().hex[:10]}"
    scan_type = str(scan_type)

    def emit(ev: dict) -> None:
        if progress:
            try:
                progress(ev)
            except Exception:
                pass

    scan_start = time.time()
    analysis: dict = {}

    pairs = collect_scan_file_pairs(source_dir)
    rels = [p[1] for p in pairs]
    project_key = _make_project_key(user_id, project_name, rels)
    index_files = collect_index_file_data(source_dir)

    emit({"type": "start", "msg": f"Starting Tier {scan_type} scan (direct)…"})

    if scan_type in ["2", "3", "4"]:
        emit({"type": "log", "filename": "SYSTEM", "msg": "Analyzing project layout…"})
        try:
            file_tree = []
            config_contents: dict = {}
            for root, dirs, files in os.walk(source_dir):
                dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
                file_tree.append(f"{os.path.basename(root)}/")
                for fn in files[:20]:
                    file_tree.append(f"  {fn}")
                    if fn in CONFIG_FILES:
                        try:
                            with open(
                                os.path.join(root, fn), "r", encoding="utf-8", errors="ignore"
                            ) as fp:
                                config_contents[fn] = fp.read()[:3000]
                        except OSError:
                            pass
            payload = (
                "STRUCTURE:\n" + "\n".join(file_tree[:300]) + "\nCONFIGS:\n" + str(config_contents)
            )
            req = _make_dummy_request(worker_app)
            analysis = await analyze_project(
                AnalyzeRequest(project_structure=payload, system_prompt=ANALYSIS_PROMPT),
                req,
                WORKER_SECRET,
            )
        except HTTPException as e:
            logger.warning("Project analyze failed: %s", e.detail)
            analysis = {}
        except Exception as e:
            logger.warning("Project analyze error: %s", e)
            analysis = {}

    emit({"type": "log", "filename": "SYSTEM", "msg": "Indexing project…"})
    if index_files:
        try:
            await index_project(
                IndexRequest(files=index_files, project_key=project_key),
                x_secret=WORKER_SECRET,
                x_scan_id=scan_id,
            )
        except HTTPException as e:
            logger.warning("index_project failed: %s", e.detail)

    if scan_type in ["2", "3", "4"] and index_files:

        async def _deepwiki_bg() -> None:
            try:
                await index_project_deepwiki(
                    DeepWikiIndexRequest(files=index_files, project_key=project_key),
                    x_secret=WORKER_SECRET,
                    x_scan_id=scan_id,
                )
            except Exception as e:
                logger.warning("DeepWiki indexing: %s", e)

        asyncio.create_task(_deepwiki_bg())
        emit(
            {
                "type": "log",
                "filename": "SYSTEM",
                "msg": "DeepWiki / graph indexing started in background.",
            }
        )

    concurrency = max(1, int(os.environ.get("LOCAL_SCAN_CONCURRENCY", "4")))
    sem = asyncio.Semaphore(concurrency)

    work_items: List[Tuple[str, str, str]] = []
    for full_path, relative_path in pairs:
        ext = os.path.splitext(full_path)[1]
        if ext not in VALID_EXTENSIONS or os.path.basename(full_path) in IGNORED_FILENAMES:
            continue
        try:
            if os.path.getsize(full_path) > MAX_FILE_SIZE_BYTES:
                emit(
                    {
                        "type": "log",
                        "filename": relative_path,
                        "msg": "Skipped: File too large (>1MB)",
                    }
                )
                continue
        except OSError:
            emit(
                {
                    "type": "log",
                    "filename": relative_path,
                    "msg": "Skipped: Unable to read file size",
                }
            )
            continue
        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception as e:
            emit({"type": "log", "filename": relative_path, "msg": f"Error: {e}"})
            continue
        if not content.strip():
            continue
        work_items.append((full_path, relative_path, content))

    total_files = len(work_items)
    emit({"type": "log", "filename": "SYSTEM", "msg": f"Scanning {total_files} files…"})
    if total_files > 0:
        emit({"type": "progress", "files_scanned": 0, "total_files": total_files})

    async def scan_one(
        idx: int, full_path: str, relative_path: str, content: str
    ) -> Tuple[int, Optional[dict], Optional[str]]:
        emit({"type": "file_start", "filename": relative_path})
        async with sem:
            req = _make_dummy_request(worker_app)
            try:
                body = await scan_code_pipeline(
                    ScanRequest(filename=relative_path, content=content),
                    req,
                    scan_id,
                    scan_type,
                )
            except Exception as e:
                emit({"type": "log", "filename": relative_path, "msg": f"Error: {e}"})
                return idx, None, False
        row = _row_from_worker_response(body, relative_path, content, scan_type)
        if row.get("status") == "VULNERABLE":
            emit(
                {
                    "type": "vuln_found",
                    "filename": relative_path,
                    "count": len(row.get("issues", [])),
                    "issues": row.get("issues", []),
                }
            )
            return idx, row, True
        if row.get("status") == "NOT_SCANNED" or row.get("skipped"):
            emit({"type": "file_safe", "filename": relative_path})
            return idx, row, True
        emit({"type": "file_safe", "filename": relative_path})
        return idx, None, True

    indexed_out = await asyncio.gather(
        *(scan_one(i, a, b, c) for i, (a, b, c) in enumerate(work_items))
    )
    indexed_out.sort(key=lambda t: t[0])
    results = [row for _, row, scanned in indexed_out if row is not None]
    files_scanned = sum(1 for _, _, scanned in indexed_out if scanned)
    if total_files > 0:
        emit({"type": "progress", "files_scanned": files_scanned, "total_files": total_files})

    elapsed_seconds = time.time() - scan_start
    duration_msg = _format_duration(elapsed_seconds)

    emit({"type": "start", "msg": "Compiling report…"})
    if results:
        await _merge_agent_findings_async(scan_id, results, scan_type)
        try:
            req_cf = _make_dummy_request(worker_app)
            cross = await cross_file_consistency(
                CrossFileConsistencyRequest(scan_id=scan_id, vulnerabilities=results),
                req_cf,
                WORKER_SECRET,
            )
            if cross and cross.get("vulnerabilities") is not None:
                results = cross.get("vulnerabilities", results)
        except HTTPException as e:
            logger.warning("cross_file_consistency: %s", e.detail)
        except Exception as e:
            logger.warning("cross_file_consistency: %s", e)

    final_scan_data = {
        "scan_id": scan_id,
        "scan_type": scan_type,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "stats": {
            "files_scanned": files_scanned,
            "vulnerabilities": len(results),
            "elapsed_seconds": elapsed_seconds,
        },
        "project_analysis": analysis,
        "vulnerabilities": results,
        "project_name": project_name,
    }
    save_scan_artifacts(scan_id, final_scan_data, output_dir)

    emit({"type": "log", "filename": "SYSTEM", "msg": f"Done in {duration_msg}."})
    emit({"type": "complete", "scan_id": scan_id})
    emit({"type": "_final", "data": final_scan_data})
    return final_scan_data


async def run_local_scan_session(
    worker_app: Any,
    source_dir: str,
    output_dir: str,
    scan_type: str = "2",
    project_name: str = "Local folder",
    progress: Optional[Callable[[dict], None]] = None,
) -> dict:
    """Attach aiohttp session to ``worker_app`` for the duration of the scan."""
    async with aiohttp.ClientSession() as session:
        worker_app.state.session = session
        return await run_local_folder_scan_async(
            worker_app,
            source_dir,
            output_dir,
            scan_type=scan_type,
            project_name=project_name,
            progress=progress,
        )


def run_local_scan_sync(
    worker_app: Any,
    source_dir: str,
    output_dir: str,
    scan_type: str = "2",
    project_name: str = "Local folder",
    progress: Optional[Callable[[dict], None]] = None,
) -> dict:
    return asyncio.run(
        run_local_scan_session(
            worker_app,
            source_dir,
            output_dir,
            scan_type=scan_type,
            project_name=project_name,
            progress=progress,
        )
    )
