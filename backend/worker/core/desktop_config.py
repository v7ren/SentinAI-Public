"""
Load SentinAI desktop settings written by the Tauri app.

Path: %LOCALAPPDATA%/SentinAI/settings.json (Windows) or ~/SentinAI/settings.json fallback.
Overrides process env when keys are present in the file.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Optional

_log = logging.getLogger(__name__)

_LOADED: Optional[dict[str, Any]] = None


def _settings_path() -> Optional[Path]:
    override = os.getenv("SENTINAI_SETTINGS_PATH")
    if override:
        return Path(override)
    local = os.getenv("LOCALAPPDATA")
    if local:
        return Path(local) / "SentinAI" / "settings.json"
    home = os.getenv("HOME") or os.getenv("USERPROFILE")
    if home:
        return Path(home) / "SentinAI" / "settings.json"
    return None


def load_desktop_settings() -> dict[str, Any]:
    global _LOADED
    if _LOADED is not None:
        return _LOADED
    path = _settings_path()
    if not path or not path.is_file():
        _LOADED = {}
        return _LOADED
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        _LOADED = data if isinstance(data, dict) else {}
        _log.info("Loaded desktop settings from %s", path)
    except Exception as e:
        _log.warning("Failed to load desktop settings from %s: %s", path, e)
        _LOADED = {}
    return _LOADED


def desktop_get(key: str) -> Optional[str]:
    """Desktop settings file overrides environment variables."""
    data = load_desktop_settings()
    mapping = {
        "OPENCODE_API_KEY": ("opencodeApiKey", "opencode_api_key"),
        "DEEPSEEK_API_KEY": ("opencodeApiKey", "opencode_api_key"),
        "OPENCODE_BRIDGE_URL": ("opencodeBridgeUrl", "opencode_bridge_url"),
        "CLOSESOURCE_URL": ("engineUrl", "engine_url"),
        "CLOSESOURCE_API_KEY": ("closesourceApiKey", "closesource_api_key"),
        "WORKER_SECRET": ("workerSecret", "worker_secret"),
        "SCAN_MODEL": ("scanModel", "scan_model"),
        "GATEWAY_URL": ("gatewayUrl", "gateway_url"),
    }
    keys = mapping.get(key, (key,))
    for k in keys:
        v = data.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    env_val = os.getenv(key)
    if env_val and str(env_val).strip():
        return str(env_val).strip()
    return None


def port_from_url(url: Optional[str], fallback: int) -> int:
    """Parse host:port from a URL. Never uses the generic PORT env (gateway vs engine clash)."""
    if not url:
        return fallback
    try:
        host = url.rsplit("/", 1)[-1]
        if ":" in host:
            port = int(host.rsplit(":", 1)[-1].split("/")[0])
            if 1 <= port <= 65535:
                return port
    except (TypeError, ValueError):
        pass
    return fallback
