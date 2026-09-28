# Data and storage

| Artifact | Location / notes |
| --- | --- |
| SQLite DB | `sentinel.db` — scan data; schema see `backend/database/models.py` |
| JSON fallback | `sentinel_db.json` when SQLite unavailable |
| Redis | Per-scan index, DeepWiki, extended indexers; TTL often 3600s unless configured otherwise |
| Scan output dirs | `backend/scan_results/` — per-scan result folders |
| Finding identity | `fingerprint` — e.g. `sha256(filename:line:snippet)` style identity for deduplication |
| Desktop settings | `%LOCALAPPDATA%/SentinAI/settings.json` |

## Database package

- `backend/database/` — scan persistence helpers (see files in that directory when changing storage).
