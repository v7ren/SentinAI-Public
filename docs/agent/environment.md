# Environment variables

Keys for local use are also written from the desktop **Settings** tab into `%LOCALAPPDATA%/SentinAI/settings.json` and loaded by `backend/worker/core/desktop_config.py`.

## Client gateway (`backend/client.py`)

| Variable | Role |
| --- | --- |
| `OPENCODE_API_KEY` | OpenCode / DeepSeek key (this is the only model key) |
| `DEEPSEEK_API_KEY` | Unused unless `OPENCODE_API_KEY` is empty (legacy alias) |
| `OPENROUTER_API_KEY` | **Deprecated** |
| `CLOSESOURCE_API_KEY` | Authenticates gateway → engine |
| `CLOSESOURCE_URL` | Engine base URL (default `http://127.0.0.1:5002`) |
| `WORKER_SECRET` | Same secret the desktop sends as `X-Api-Key` on local-start |
| `REDIS_OPTIONAL=1` | Use in-memory fallback instead of Redis |

Gateway may pass `X-Opencode-Api-Key`, `X-Deepseek-Key`, or legacy `x-openrouter-key` to the engine (per-scan override).

## Proprietary engine (`backend/closesource.py` / worker)

| Variable | Role |
| --- | --- |
| `CLOSESOURCE_API_KEY` | Must match the gateway’s key |
| `OPENCODE_API_KEY` | OpenCode key; worker passes it to the bridge |
| `OPENCODE_BRIDGE_URL` | Worker → bridge URL (default `http://127.0.0.1:5010`) |
| `OPENCODE_BASE_URL` | OpenCode `serve` URL (default `http://127.0.0.1:4096`) |
| `SCAN_MODEL` | OpenCode model id (default `deepseek-v4.1-flash`; `dsv4.1flash` / `deepseek-flash` / `deepseek-v4-flash` alias to that) |
| `REDIS_OPTIONAL=1` | In-memory fallback |
| Other scan toggles | See `backend/worker/core/config.py` |

## OpenCode bridge (`backend/opencode-bridge`)

Node.js process using `@opencode-ai/sdk` (run: `cd backend/opencode-bridge && npm install && npm start`). Requires the `opencode` CLI on `PATH` when `OPENCODE_AUTOSTART=1`. Go sources in the same folder are optional/legacy.

| Variable | Role |
| --- | --- |
| `OPENCODE_API_KEY` | OpenCode API key (preferred). Bridge also reads it from desktop Settings. |
| `DEEPSEEK_API_KEY` | Legacy alias only |
| `BRIDGE_PORT` / `BRIDGE_LISTEN` | HTTP listen (default `:5010`) |
| `OPENCODE_BASE_URL` | `opencode serve` URL the SDK attaches to (default `http://127.0.0.1:4096`) |
| `OPENCODE_AUTOSTART` | `1` (default) spawns `opencode serve` from the bridge directory; `0` = attach only |
| `OPENCODE_PROVIDER_ID` | Default `opencode-go` |
