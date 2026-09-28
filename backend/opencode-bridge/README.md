# OpenCode bridge (DeepSeek Flash)

Localhost HTTP process that the SentinAI Python worker calls for every model completion. It uses the official **`@opencode-ai/sdk`** (TypeScript) against a local `opencode serve` instance configured for **DeepSeek** — never OpenRouter.

## Prerequisites

- **Node.js 20+** and npm
- **`opencode` CLI** on `PATH` (used when the bridge autostarts the server)
- `OPENCODE_API_KEY` or `DEEPSEEK_API_KEY` in the environment (same DeepSeek key; `OPENCODE_API_KEY` is preferred for the bridge)

Go 1.22+ is **optional** — see [Legacy Go implementation](#legacy-go-implementation-optional) below.

## Run (primary)

```bash
cd backend/opencode-bridge
npm install
npm start
```

Default listen address: `http://127.0.0.1:5010`

On startup the bridge attaches to `OPENCODE_BASE_URL` (default `http://127.0.0.1:4096`). If that URL is down and `OPENCODE_AUTOSTART` is not `0`, it runs:

```bash
opencode serve --hostname 127.0.0.1 --port 4096
```

from this directory so `opencode.json` is loaded (provider `deepseek`, model `deepseek-flash` only).

## Environment variables

| Variable | Default | Meaning |
| --- | --- | --- |
| `OPENCODE_API_KEY` | _(preferred)_ | DeepSeek API key for OpenCode (also sets `DEEPSEEK_API_KEY` on child `opencode serve`) |
| `DEEPSEEK_API_KEY` | _(alias)_ | Same key if `OPENCODE_API_KEY` is unset |
| `OPENCODE_BASE_URL` | `http://127.0.0.1:4096` | Existing `opencode serve` URL to attach to |
| `OPENCODE_AUTOSTART` | `1` | Set to `0` to never spawn `opencode serve` (attach-only) |
| `BRIDGE_LISTEN` | `127.0.0.1:5010` | Bridge HTTP listen address (`:5010` and `5010` are also accepted) |

The worker uses `OPENCODE_BRIDGE_URL` (default `http://127.0.0.1:5010`) — unchanged.

## HTTP contract

### `GET /health`

```json
{
  "ok": true,
  "opencode": "reachable",
  "model": "deepseek-flash",
  "opencode_base_url": "http://127.0.0.1:4096"
}
```

`opencode` is `"reachable"` or `"unreachable"`. This endpoint always returns HTTP 200 so process liveness is separate from OpenCode readiness.

### `POST /complete`

Request:

```json
{
  "scan_id": "abc123",
  "system": "optional system prompt",
  "user": "user / file prompt"
}
```

Response (HTTP 200):

```json
{
  "scan_id": "abc123",
  "text": "assistant reply…",
  "session_id": "ses_…",
  "model": "deepseek-flash"
}
```

Errors:

- `400` — missing `scan_id` / `user` or bad JSON
- `503` — OpenCode server unreachable (clear message; **no OpenRouter fallback**)
- `502` — OpenCode reachable but the prompt failed

One OpenCode session is created per `scan_id`. Each `/complete` is one `session.prompt` on that session; the bridge waits for the assistant message and returns its text.

## Safety

- `opencode.json` denies `shell`, `edit`, and `write` permissions.
- Each prompt also disables `bash` / `shell` / `edit` / `write` tools.
- A background event watcher rejects any shell or file-edit permission requests that still appear.

## Tests

```bash
cd backend/opencode-bridge
npm test
```

## Legacy Go implementation (optional)

The original Go bridge (`bridge.go`, `server.go`, …) remains for reference and parity tests. It is **not** required for normal operation.

```bash
cd backend/opencode-bridge
go mod tidy
go run .
# or: go test ./...
```

Prefer `npm start` unless you explicitly want the Go binary.
