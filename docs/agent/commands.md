# Commands

## Desktop (Tauri)

From the repo root (workspaces: `desktop`, `backend/opencode-bridge`):

```bash
npm install
npm run desktop
```

Or from `desktop/` directly:

```bash
cd desktop
npm install
npm run tauri dev
```

Configure API keys and URLs in the app **Settings** tab (writes `%LOCALAPPDATA%/SentinAI/settings.json`). Restart Python services after saving.

## Open-source client gateway (port 5001, loopback)

```bash
cd backend
python client.py
```

Listens on **127.0.0.1**. Routes live in `backend/mainflask.py`.

Headless folder scan example (if the launcher still exposes CLI flags):

```bash
cd backend
python client.py --headless --source "C:\code" --out "C:\out" --tier 2
```

## OpenCode → DeepSeek bridge (port 5010, before DeepSeek scans)

```bash
cd backend/opencode-bridge
npm install
npm start
```

Requires `OPENCODE_API_KEY` (or `DEEPSEEK_API_KEY`) and `opencode` on `PATH` (unless `OPENCODE_AUTOSTART=0` and OpenCode is already running). Worker uses `OPENCODE_BRIDGE_URL=http://127.0.0.1:5010`. Optional legacy: `go run .` in the same folder.

## Native Rust indexer (optional)

```bash
cd native/sentinai-index
maturin develop --release
```

## Proprietary scan engine (port 5002 typical)

```bash
cd backend
python closesource.py
```

Headless HTTP only:

```bash
cd backend
python closesource.py --headless
```

Custom port:

```bash
cd backend
python closesource.py --headless --port 5003
```

## Benchmark

```bash
python benchmark/run_benchmark.py
```

Optional: `USE_STREAMING=1` for SSE mode (when supported by the benchmark harness).

## Tests

```bash
python test.py
python test_vulnerabilities.py
```

Worker tests:

```bash
cd backend/worker/core && python -m pytest ../tests/
```

## Legacy

Prefer `client.py` + `closesource.py` instead of running `main.py` or `local_scan_server.py` directly:

```bash
cd backend/worker/core && python main.py
cd backend && python local_scan_server.py
```
