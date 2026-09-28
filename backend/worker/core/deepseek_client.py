"""
HTTP client for the OpenCode bridge (Node @opencode-ai/sdk or legacy Go) — deepseek-flash only.
"""

import json
import logging
from contextvars import ContextVar, Token
from typing import Any, Optional, Tuple

import aiohttp

from backend.worker.core.config import (
    DEEPSEEK_API_KEY,
    OPENCODE_API_KEY,
    OPENCODE_BRIDGE_URL,
    SCAN_MODEL,
)

_log = logging.getLogger(__name__)

_BRIDGE_HEALTH_CACHE: Optional[bool] = None
_request_llm_key: ContextVar[Optional[str]] = ContextVar("request_llm_key", default=None)


def effective_llm_api_key() -> str:
    override = _request_llm_key.get()
    if override:
        return override
    return override or OPENCODE_API_KEY or DEEPSEEK_API_KEY or ""


def set_request_llm_api_key_from_request(req: Any) -> Optional[Token]:
    """Use per-scan key from gateway headers when present."""
    if req is None:
        return None
    headers = getattr(req, "headers", None)
    if headers is None:
        return None
    for name in ("x-opencode-api-key", "x-deepseek-key", "x-openrouter-key"):
        value = headers.get(name)
        if value and str(value).strip():
            return _request_llm_key.set(str(value).strip())
    auth = headers.get("authorization")
    if auth and str(auth).lower().startswith("bearer "):
        return _request_llm_key.set(str(auth)[7:].strip())
    return None


def reset_request_llm_api_key(token: Optional[Token]) -> None:
    if token is not None:
        _request_llm_key.reset(token)


def llm_configured() -> bool:
    return bool(effective_llm_api_key())


def _bridge_auth_headers() -> dict[str, str]:
    key = effective_llm_api_key()
    if not key:
        return {}
    return {
        "X-Opencode-Api-Key": key,
        "X-Deepseek-Key": key,
    }


async def bridge_healthy(session: Optional[aiohttp.ClientSession] = None) -> bool:
    global _BRIDGE_HEALTH_CACHE
    if not llm_configured():
        return False
    url = f"{OPENCODE_BRIDGE_URL.rstrip('/')}/health"
    own = session is None
    if own:
        session = aiohttp.ClientSession()
    try:
        timeout = aiohttp.ClientTimeout(total=5)
        async with session.get(url, timeout=timeout) as resp:
            ok = resp.status == 200
            if ok:
                _BRIDGE_HEALTH_CACHE = True
            return ok
    except Exception as e:
        _log.debug("bridge health check failed: %s", e)
        _BRIDGE_HEALTH_CACHE = False
        return False
    finally:
        if own and session:
            await session.close()


def bridge_healthy_sync() -> bool:
    import urllib.request

    if not llm_configured():
        return False
    url = f"{OPENCODE_BRIDGE_URL.rstrip('/')}/health"
    try:
        with urllib.request.urlopen(url, timeout=3) as resp:
            return resp.status == 200
    except Exception:
        return False


async def complete(
    session: aiohttp.ClientSession,
    scan_id: str,
    system: str,
    user: str,
    timeout_seconds: int = 300,
) -> Tuple[str, str]:
    """Returns (text, model). Raises on HTTP/bridge errors."""
    if not llm_configured():
        raise RuntimeError("OPENCODE_API_KEY not set")
    url = f"{OPENCODE_BRIDGE_URL.rstrip('/')}/complete"
    payload = {
        "scan_id": scan_id or "default",
        "system": system,
        "user": user,
    }
    headers = {"Content-Type": "application/json", **_bridge_auth_headers()}
    timeout = aiohttp.ClientTimeout(total=timeout_seconds)
    async with session.post(url, json=payload, headers=headers, timeout=timeout) as resp:
        body = await resp.text()
        if resp.status != 200:
            raise RuntimeError(f"bridge /complete {resp.status}: {body[:500]}")
        data = json.loads(body)
        text = data.get("text") or data.get("content") or ""
        model = data.get("model") or SCAN_MODEL
        return text, model


def complete_sync(scan_id: str, system: str, user: str, timeout_seconds: int = 300) -> Tuple[str, str]:
    import urllib.request

    if not llm_configured():
        raise RuntimeError("OPENCODE_API_KEY not set")
    url = f"{OPENCODE_BRIDGE_URL.rstrip('/')}/complete"
    payload = json.dumps(
        {
            "scan_id": scan_id or "default",
            "system": system,
            "user": user,
        }
    ).encode("utf-8")
    headers = {"Content-Type": "application/json", **_bridge_auth_headers()}
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data.get("text") or data.get("content") or "", data.get("model") or SCAN_MODEL


async def complete_json(
    session: aiohttp.ClientSession,
    scan_id: str,
    system: str,
    user: str,
    timeout_seconds: int = 300,
) -> Any:
    from backend.worker.core.utils import parse_json_with_fallbacks

    text, _model = await complete(session, scan_id, system, user, timeout_seconds=timeout_seconds)
    ok, parsed = parse_json_with_fallbacks(text, "bridge")
    if ok:
        return parsed
    return {"status": "UNKNOWN", "details": "Invalid JSON from bridge", "raw": text[:2000]}
