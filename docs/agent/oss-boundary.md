# Open source vs proprietary boundary

Use this when packaging releases or deciding what to commit to public repos.

## Typically **include** in open source

- `backend/client.py` — gateway launcher
- `backend/mainflask.py` — local-start + SSE (no hosted auth/pay)
- `backend/local_scan_core.py`, `backend/local_scan_server.py` — standalone CLI pattern
- `backend/worker/core/models.py` — API schemas (no proprietary logic)
- `backend/worker/core/redis_client.py`, `utils.py`, `project_indexer.py` — non-LLM infrastructure / regex indexer
- `desktop/` — Tauri app
- `backend/database/` — scan storage schemas
- `CLAUDE.md`, `agent.md`, `docs/agent/`, tests, benchmarks

## Typically **keep proprietary** (do not ship in OSS)

- `backend/closesource.py`
- `ai_tier1.py`, `ai_tier2.py`, `ai_tier3.py`, `llm_centric_detector.py`
- `poc.py`, `keywords.py`, `findings_filter.py`, `findings_validator.py`, `context_compactor.py`
- `deepwiki_utils.py`, `LLMindexer.py`
- `backend/worker/core/agents/`, `enrichment/`, `indexers/`, `validation/`

Legal and product policy trump this file—confirm with maintainers before any release.
