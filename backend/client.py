"""
Open-source client gateway launcher.

Runs the Flask gateway (`backend/mainflask.py`) on port 5001 by default.
Desktop settings in `%LOCALAPPDATA%/SentinAI/settings.json` override env.
"""

import argparse
import os
import sys

_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_BACKEND_DIR, ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from backend.worker.core.desktop_config import desktop_get, port_from_url

for _key in (
    "CLOSESOURCE_API_KEY",
    "DEEPSEEK_API_KEY",
    "OPENCODE_API_KEY",
    "WORKER_SECRET",
    "OPENCODE_BRIDGE_URL",
    "SCAN_MODEL",
):
    _val = desktop_get(_key)
    if _val:
        os.environ[_key] = _val
_closesource_url = desktop_get("CLOSESOURCE_URL")
if _closesource_url:
    os.environ["CLOSESOURCE_URL"] = _closesource_url
_gateway_url = desktop_get("GATEWAY_URL")
os.environ["PORT"] = str(port_from_url(_gateway_url, 5001))

_worker_secret = desktop_get("WORKER_SECRET") or desktop_get("CLOSESOURCE_API_KEY")
if _worker_secret:
    os.environ["WORKER_SECRET"] = _worker_secret
if _closesource_url:
    os.environ["WORKER_NODES"] = _closesource_url
os.environ.setdefault("REDIS_OPTIONAL", "1")

from backend.mainflask import app, PORT, WORKER_NODES, WORKER_SECRET

CLOSESOURCE_URL = (_closesource_url or (WORKER_NODES[0] if WORKER_NODES else "http://127.0.0.1:5002"))
CLOSESOURCE_API_KEY = os.getenv("CLOSESOURCE_API_KEY") or WORKER_SECRET
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
RATE_LIMIT_BYPASS_KEY = os.getenv("RATE_LIMIT_BYPASS_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SentinAI client gateway")
    parser.add_argument("--headless", action="store_true", help="HTTP server only (same as default)")
    parser.parse_args()
    print(f"[SentinAI Client Gateway] Starting on port {PORT}")
    print(f"[CONFIG] CLOSESOURCE_URL: {CLOSESOURCE_URL}")
    _opencode = os.getenv("OPENCODE_API_KEY")
    print(f"[CONFIG] OPENCODE_API_KEY: {'SET' if _opencode else 'NOT SET'}")
    print(f"[CONFIG] DEEPSEEK_API_KEY: {'SET' if DEEPSEEK_API_KEY else 'NOT SET'}")
    print(f"[CONFIG] OPENROUTER_API_KEY (deprecated): {'SET' if OPENROUTER_API_KEY else 'NOT SET'}")
    print(f"[CONFIG] CLOSESOURCE_API_KEY: {'SET' if CLOSESOURCE_API_KEY else 'NOT SET'}")
    print(f"[SentinAI Client Gateway] Listening on http://127.0.0.1:{PORT}")
    app.run(host="127.0.0.1", port=PORT, debug=False, threaded=True)
