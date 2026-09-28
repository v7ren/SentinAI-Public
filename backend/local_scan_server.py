"""
Local SentinAI scan: no Flask gateway, no HTTP worker, no web UI.

- Uses ``tkinter`` folder pickers (source + output) by default.
- Calls worker logic directly via ``local_scan_core`` (async + aiohttp session).

Run from repo root:
  python backend/local_scan_server.py

Headless (typed paths, no GUI):
  python backend/local_scan_server.py --headless --source "C:\\code" --out "C:\\out" --tier 2

Env: ``WORKER_SECRET`` (optional default), ``REDIS_OPTIONAL=1``, ``OPENROUTER_API_KEY``,
``LOCAL_SCAN_CONCURRENCY`` (default 4 parallel files).
"""

from __future__ import annotations

import argparse
import logging
import os
import queue
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# ---------------------------------------------------------------------------
# Path + env bootstrap (before backend imports)
# ---------------------------------------------------------------------------
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
if _BACKEND_DIR not in sys.path:
    sys.path.append(_BACKEND_DIR)

_WORKER_CORE_DIR = os.path.join(_BACKEND_DIR, "worker", "core")
if _WORKER_CORE_DIR not in sys.path:
    sys.path.insert(0, _WORKER_CORE_DIR)

if not (os.getenv("WORKER_SECRET") or "").strip():
    os.environ["WORKER_SECRET"] = "local-dev-worker-secret-not-for-production"
os.environ.setdefault("REDIS_OPTIONAL", "1")

from dotenv import load_dotenv

load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "worker", ".env"))

from backend.local_scan_core import run_local_scan_sync
from backend.worker.core.main import app as worker_app


def _run_gui() -> None:
    root = tk.Tk()
    root.title("SentinAI — local scan")
    root.geometry("640x520")

    source_var = tk.StringVar()
    out_var = tk.StringVar()
    project_var = tk.StringVar(value="Local folder")
    tier_var = tk.StringVar(value="2")

    log_q: queue.Queue = queue.Queue()
    running = {"v": False}

    frm = ttk.Frame(root, padding=12)
    frm.pack(fill=tk.BOTH, expand=True)

    def pick_source() -> None:
        d = filedialog.askdirectory(title="Select source code folder")
        if d:
            source_var.set(d)

    def pick_out() -> None:
        d = filedialog.askdirectory(title="Select output folder for reports")
        if d:
            out_var.set(d)

    ttk.Label(frm, text="Source folder").grid(row=0, column=0, sticky="w")
    ttk.Entry(frm, textvariable=source_var, width=58).grid(row=1, column=0, columnspan=2, sticky="ew")
    ttk.Button(frm, text="Browse…", command=pick_source).grid(row=1, column=2, padx=(8, 0))

    ttk.Label(frm, text="Output folder").grid(row=2, column=0, sticky="w", pady=(12, 0))
    ttk.Entry(frm, textvariable=out_var, width=58).grid(row=3, column=0, columnspan=2, sticky="ew")
    ttk.Button(frm, text="Browse…", command=pick_out).grid(row=3, column=2, padx=(8, 0))

    ttk.Label(frm, text="Project name").grid(row=4, column=0, sticky="w", pady=(12, 0))
    ttk.Entry(frm, textvariable=project_var, width=40).grid(row=5, column=0, columnspan=2, sticky="w")

    ttk.Label(frm, text="Tier").grid(row=6, column=0, sticky="w", pady=(12, 0))
    tier_cb = ttk.Combobox(
        frm,
        textvariable=tier_var,
        values=("1", "2", "3", "4"),
        width=8,
        state="readonly",
    )
    tier_cb.grid(row=7, column=0, sticky="w")

    log_text = tk.Text(frm, height=16, wrap=tk.WORD, state=tk.DISABLED)
    log_text.grid(row=8, column=0, columnspan=3, sticky="nsew", pady=(12, 0))
    sb = ttk.Scrollbar(frm, command=log_text.yview)
    sb.grid(row=8, column=3, sticky="ns", pady=(12, 0))
    log_text["yscrollcommand"] = sb.set

    frm.columnconfigure(0, weight=1)
    frm.rowconfigure(8, weight=1)

    def append_log(line: str) -> None:
        log_text.configure(state=tk.NORMAL)
        log_text.insert(tk.END, line + "\n")
        log_text.see(tk.END)
        log_text.configure(state=tk.DISABLED)

    def poll_queue() -> None:
        try:
            while True:
                line = log_q.get_nowait()
                append_log(line)
        except queue.Empty:
            pass
        root.after(200, poll_queue)

    def progress_to_queue(ev: dict) -> None:
        t = ev.get("type", "")
        if t == "log":
            log_q.put(f"[log] {ev.get('filename') or ''}: {ev.get('msg', '')}")
        elif t == "start":
            log_q.put(f"[{t}] {ev.get('msg', '')}")
        elif t in ("file_start", "vuln_found", "file_safe", "progress", "complete"):
            log_q.put(f"[{t}] {ev.get('filename') or ev.get('scan_id') or ''} {ev.get('msg', '')}")
        elif t == "_final":
            data = ev.get("data") or {}
            sid = data.get("scan_id", "")
            log_q.put(f"Finished. scan_id={sid}")

    def start_scan() -> None:
        if running["v"]:
            messagebox.showinfo("Busy", "A scan is already running.")
            return
        src = source_var.get().strip()
        out = out_var.get().strip()
        if not src or not out:
            messagebox.showerror("Missing path", "Choose source and output folders.")
            return
        if not os.path.isdir(src):
            messagebox.showerror("Invalid source", f"Not a directory:\n{src}")
            return

        running["v"] = True
        btn_run.state(["disabled"])
        log_text.configure(state=tk.NORMAL)
        log_text.delete("1.0", tk.END)
        log_text.configure(state=tk.DISABLED)

        tier = tier_var.get().strip() or "2"
        pname = project_var.get().strip() or "Local folder"

        def worker() -> None:
            try:

                def prog(ev: dict) -> None:
                    progress_to_queue(ev)

                run_local_scan_sync(
                    worker_app,
                    src,
                    out,
                    scan_type=tier,
                    project_name=pname,
                    progress=prog,
                )
                log_q.put("--- OK: reports written under output folder (see scan_id subfolder). ---")
            except Exception as e:
                log_q.put(f"--- ERROR: {e} ---")
            finally:
                running["v"] = False
                root.after(0, lambda: btn_run.state(["!disabled"]))

        threading.Thread(target=worker, daemon=True).start()

    btn_run = ttk.Button(frm, text="Run scan", command=start_scan)
    btn_run.grid(row=7, column=1, columnspan=2, sticky="e", pady=(12, 0))

    root.after(200, poll_queue)
    root.mainloop()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    parser = argparse.ArgumentParser(description="SentinAI local scan (tkinter + direct worker calls)")
    parser.add_argument("--headless", action="store_true", help="No GUI; requires --source and --out")
    parser.add_argument("--source", type=str, default="")
    parser.add_argument("--out", type=str, default="")
    parser.add_argument("--tier", type=str, default="2")
    parser.add_argument("--project-name", type=str, default="Local folder")
    args = parser.parse_args()

    if args.headless:
        if not args.source.strip() or not args.out.strip():
            parser.error("--headless requires --source and --out")
        def _cli_progress(ev: dict) -> None:
            if ev.get("type") in ("log", "start", "progress", "complete", "_final"):
                print(ev)

        run_local_scan_sync(
            worker_app,
            args.source.strip(),
            args.out.strip(),
            scan_type=args.tier,
            project_name=args.project_name,
            progress=_cli_progress,
        )
        return

    _run_gui()


if __name__ == "__main__":
    main()
