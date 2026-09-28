"""
Proprietary scan engine launcher.

Runs the FastAPI worker (`backend/worker/core/main.py`) on port 5002 by default.
Supports GUI (start/stop) and `--headless [--port]`.
"""

from __future__ import annotations

import argparse
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk

import uvicorn

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

_worker_secret = desktop_get("WORKER_SECRET") or desktop_get("CLOSESOURCE_API_KEY")
if _worker_secret:
    os.environ["WORKER_SECRET"] = _worker_secret
_engine_url = desktop_get("CLOSESOURCE_URL")
if _engine_url:
    os.environ["CLOSESOURCE_URL"] = _engine_url

os.environ.setdefault("REDIS_OPTIONAL", "1")

from backend.worker.core.main import app

DEFAULT_PORT = port_from_url(_engine_url, 5002)


def _run_uvicorn(port: int, server_holder: dict | None = None) -> None:
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="info")
    server = uvicorn.Server(config)
    if server_holder is not None:
        server_holder["server"] = server
    server.run()


def _run_gui(port: int) -> None:
    root = tk.Tk()
    root.title("SentinAI engine")
    root.geometry("420x180")

    status = tk.StringVar(value=f"Stopped — will listen on 127.0.0.1:{port}")
    holder: dict = {}
    thread: list[threading.Thread | None] = [None]

    frm = ttk.Frame(root, padding=16)
    frm.pack(fill=tk.BOTH, expand=True)
    ttk.Label(frm, textvariable=status).pack(anchor=tk.W, pady=(0, 12))

    def start() -> None:
        if thread[0] and thread[0].is_alive():
            return
        holder.clear()
        t = threading.Thread(target=_run_uvicorn, args=(port, holder), daemon=True)
        thread[0] = t
        t.start()
        status.set(f"Running on http://127.0.0.1:{port}")

    def stop() -> None:
        server = holder.get("server")
        if server is not None:
            server.should_exit = True
        status.set("Stopped")

    btns = ttk.Frame(frm)
    btns.pack(anchor=tk.W)
    ttk.Button(btns, text="Start", command=start).pack(side=tk.LEFT, padx=(0, 8))
    ttk.Button(btns, text="Stop", command=stop).pack(side=tk.LEFT)

    root.protocol("WM_DELETE_WINDOW", lambda: (stop(), root.destroy()))
    root.mainloop()


def main() -> None:
    parser = argparse.ArgumentParser(description="SentinAI proprietary scan engine")
    parser.add_argument("--headless", action="store_true", help="HTTP server only (no GUI)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()

    print(f"[SentinAI engine] port={args.port} headless={args.headless}")
    print(f"[CONFIG] WORKER_SECRET: {'SET' if os.getenv('WORKER_SECRET') else 'NOT SET'}")
    print(
        f"[CONFIG] OPENCODE_API_KEY: {'SET' if os.getenv('OPENCODE_API_KEY') else 'NOT SET'}"
    )
    print(
        f"[CONFIG] OPENCODE_BRIDGE_URL: {os.getenv('OPENCODE_BRIDGE_URL', 'http://127.0.0.1:5010')}"
    )

    if args.headless:
        _run_uvicorn(args.port)
        return
    _run_gui(args.port)


if __name__ == "__main__":
    main()
