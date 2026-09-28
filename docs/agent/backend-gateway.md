# Backend: open-source client gateway

**Entry:** `backend/client.py` (launches Flask in `backend/mainflask.py`), typically port **5001** on **127.0.0.1**.

## Responsibilities

- Accept a local folder path from the Tauri app and orchestrate scans against the proprietary engine.
- Stream results via SSE.
- Authenticate to the engine with `WORKER_SECRET` / `CLOSESOURCE_API_KEY`.

Not a hosted multi-user API: no OAuth, payments, browser file uploads, or public bind.

## API surface

Desktop (`X-Api-Key` + loopback):

- `POST /api/scan/local-start` — JSON `{ source_dir, project_name, scan_type }`
- `GET /api/scan/events/<scan_id>` — SSE progress
- `GET /api/scan/status/<scan_id>`
- `POST /api/scan/cache-choice` — DeepWiki cache reuse prompt
- `GET /api/health`

Unused by the current UI but still local-key gated (for later desktop screens):

- `GET /api/scan/by-id/<scan_id>`
- `POST /api/scan/pocs`
- `GET /api/scan/docs/<scan_id>`

## Related files

- `backend/local_scan_core.py`, `backend/local_scan_server.py` — standalone local scan pattern (legacy but still useful reference).
- Environment: [environment.md](environment.md).
