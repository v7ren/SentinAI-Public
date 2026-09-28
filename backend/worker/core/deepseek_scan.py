"""Single deepseek-flash completion per file (replaces tier ladder when bridge is up)."""

import json
import logging
from typing import Any, Dict, List, Optional, Tuple

import aiohttp

from backend.worker.core.deepseek_client import bridge_healthy, complete, complete_json
from backend.worker.core.utils import detect_language, find_line_number

_log = logging.getLogger(__name__)

_FILE_SCAN_SCHEMA = {
    "status": "VULNERABLE or SAFE",
    "findings": [
        {
            "type": "string",
            "severity": "LOW|MEDIUM|HIGH|CRITICAL",
            "confidence_score": "number 1-10",
            "line": "integer",
            "function_name": "string",
            "vulnerable_code": "string",
            "description": "string",
            "reason": "string",
            "cwe_id": "string optional",
        }
    ],
}


def _build_system_prompt(filename: str) -> str:
    language, _ = detect_language(filename)
    return (
        "You are a static application security testing engine. "
        "Analyze the given source file for real exploitable vulnerabilities. "
        f"Language context: {language}. "
        "Respond with JSON only matching this schema:\n"
        f"{json.dumps(_FILE_SCAN_SCHEMA, indent=2)}\n"
        "Do not use tools, shell, or file edits. No markdown fences."
    )


def _build_user_prompt(
    filename: str,
    content: str,
    context_slice_text: str,
    enriched_context: str,
) -> str:
    parts = [f"File: {filename}\n"]
    if enriched_context:
        parts.append(f"Project context:\n{enriched_context[:4000]}\n")
    if context_slice_text:
        parts.append(f"Graph slice:\n{context_slice_text[:2000]}\n")
    parts.append("Source:\n")
    parts.append(content[:120000])
    return "\n".join(parts)


async def deepseek_single_file_scan(
    session: aiohttp.ClientSession,
    scan_id: Optional[str],
    filename: str,
    content: str,
    enriched_context: str = "",
    context_slice_text: str = "",
) -> Dict[str, Any]:
    system = _build_system_prompt(filename)
    user = _build_user_prompt(filename, content, context_slice_text, enriched_context)
    data = await complete_json(session, scan_id or "scan", system, user)
    if isinstance(data, dict) and data.get("findings"):
        status = data.get("status", "VULNERABLE")
        findings: List[dict] = data["findings"]
        for f in findings:
            f["line"] = find_line_number(
                content,
                f.get("vulnerable_code", ""),
                function_name=f.get("function_name", ""),
            )
        return {"status": status, "findings": findings, "scan_type": "deepseek-flash"}
    if isinstance(data, dict) and data.get("status") == "SAFE":
        return {"status": "SAFE", "findings": [], "scan_type": "deepseek-flash"}
    text, model = await complete(session, scan_id or "scan", system, user)
    return {
        "status": "UNKNOWN",
        "details": text[:500],
        "model": model,
        "scan_type": "deepseek-flash",
    }


async def maybe_summarize_project(
    session: aiohttp.ClientSession,
    scan_id: str,
    project_ir: Dict[str, Any],
) -> Optional[str]:
    if not await bridge_healthy(session):
        return None
    system = (
        "Summarize this project security index for downstream SAST agents. "
        "Plain text, under 800 words. No tools."
    )
    user = json.dumps(project_ir)[:100000]
    text, _ = await complete(session, scan_id, system, user, timeout_seconds=120)
    return text.strip() or None
