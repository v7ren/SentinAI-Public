# SentinAI Desktop (Tauri)

Local UI for SentinAI. Configuration lives in **Settings** inside the app, not in `.env` files.

## Run

```bash
cd desktop
npm install
npm run tauri dev
```

Requires [Rust](https://rustup.rs/) and platform Tauri prerequisites.

## Settings file

On save, the app writes:

`%LOCALAPPDATA%\SentinAI\settings.json` (Windows)

The Python **worker** loads this file on startup (`backend/worker/core/desktop_config.py`) and overrides environment variables for:

- `OPENCODE_API_KEY` / `DEEPSEEK_API_KEY`
- `OPENCODE_BRIDGE_URL`, `SCAN_MODEL`, `WORKER_SECRET`
- Engine URL maps to `CLOSESOURCE_URL` when wired in gateway

**Restart** `client.py`, `closesource.py`, and `opencode-bridge` after changing settings.

## Backend stack (manual for now)

1. `backend/opencode-bridge` → `npm start`
2. `backend` → `python closesource.py --headless`
3. `backend` → `python client.py` (binds `127.0.0.1:5001`)

Then open the desktop app, set keys in Settings, save, restart backends.

The desktop calls `gatewayUrl` directly: `POST /api/scan/local-start` and SSE `/api/scan/events/{scanId}`.
