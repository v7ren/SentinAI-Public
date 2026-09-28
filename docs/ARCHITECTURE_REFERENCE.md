# SentinAI v4 — Technical reference (Redis, env, modules)

Companion to [`ARCHITECTURE_AND_FLOWS.md`](../ARCHITECTURE_AND_FLOWS.md). Use this for lookups while writing a thesis (keys, defaults, file paths).

---

## 1. Service topology

| Service | Entry | Default port | Role |
|--------|--------|--------------|------|
| Frontend | `src/` (Next.js) | 5000 | UI, Clerk auth, calls Flask via `src/app/api/proxy/*` |
| API gateway | `backend/mainflask.py` | 5001 | Uploads, `scan_id`, SSE, SQLite/JSON storage, worker dispatch |
| Worker | `backend/worker/core/main.py` | 5002 | Indexing, DeepWiki, extended indexers, multi-agent scan, `/scan`, `/poc` |

Headers on worker requests: `x-secret` (shared `WORKER_SECRET`), `x-scan-id`, `x-scan-type`.

---

## 2. Redis keys (per `scan_id`)

| Key suffix | Content |
|------------|---------|
| `deepwiki_index` | Project IR JSON from `LLMProjectIndexer` |
| `file_deps` | File dependency map (`FileDependencyMapper`) |
| `call_graph` | Function call graph (`FunctionCallMapper`) |
| `sanitizer_registry` | Sanitizer candidates (`SanitizerRegistry`) |
| `dead_code_map` | Dead/unreachable hints (`DeadCodeDetector`) |
| `api_surface` | List of entry-point-like functions (from call graph metadata) |
| `file_store` | Filename → content map for tool-using validators / agentic paths |
| `agent_findings` | JSON list of project-level agent findings (merged into per-file results and report) |
| `agent_chains` | Optional `VulnerabilityChain` payloads (if chain combiner enabled) |
| `agent_attack_paths` | Optional simulated attack paths |
| `agent_remediations` | Optional remediation records |
| `deepwiki_complete` | Presence flag: DeepWiki + indexers + agent scan phase finished (used to avoid merging incomplete agent output) |
| `indexing_meta` | Metadata including incremental DeepWiki stats |

**Project-scoped cache (optional):** When the gateway sends a `project_key`, the worker may read/write cache keys prefixed with `{project_key}:` for DeepWiki-related blobs (digest-based incremental reuse). Per-scan keys above still use `{scan_id}:` for the active run.

**TTL:** `SCAN_TTL` (default 3600s) for scan-scoped keys; `PROJECT_CACHE_TTL` for longer-lived project cache entries.

---

## 3. Environment variables (worker — `backend/worker/core/config.py`)

### LLM routing (OpenRouter)

| Variable | Default (if unset) | Role |
|----------|-------------------|------|
| `OPENROUTER_API_KEY` | — | Required for tier scans, DeepWiki indexer, agents |
| `AGENT_MODEL` | `MINIMAX_MODEL` | Multi-agent specialists |
| `MINIMAX_MODEL` | `minimax/minimax-m2.7` | Default agent model slug |
| `INDEXER_MODEL` | `openai/gpt-oss-120b` | `LLMProjectIndexer` / DeepWiki |
| `CHEAP_MODEL` | `qwen/qwen3.5-9b` | Tier 1 triage, parts of Tier 4 filter |
| `SMART_MODEL` | `z-ai/glm-5` | Tier 3, PoC, Skeptic, many “smart” paths |
| `OPENROUTER_TIER2_MODEL` | aliases `TIER2_MODEL` to `SMART_MODEL` if not set | Tier 2 |
| `COMPACTION_CHEAP_MODEL` | `CHEAP_MODEL` | Context compaction arbitration |

### Agents and agentic loop

| Variable | Default | Role |
|----------|---------|------|
| `AGENT_SCAN_ENABLED` | `true` | Run project-level multi-agent scan after extended indexers |
| `AGENT_AGENTIC_ENABLED` | `true` | Specialists use OpenRouter tool loop (`openrouter_agentic.py`) + `pipeline_tools` |
| `AGENT_AGENTIC_MAX_ROUNDS` | `10` | Max tool rounds per specialist (when agentic) |
| `AGENT_OPENROUTER_TIMEOUT_SECONDS` | `240` | Request/body read budget for agent calls |
| `AGENT_MAX_FILE_TOKENS` | `50000` | Cap on file text injected into agent context |
| `AGENT_LLM_SECURITY_ENABLED` | `true` | Appends `LLMSecurityAgent` (prompt injection, tool misuse, etc.) |
| `AGENT_CHAIN_COMBINER_ENABLED` | `true` | After Skeptic: optional chain combiner |
| `AGENT_ATTACK_PATH_SIMULATOR_ENABLED` | `true` | Optional paths from chains |
| `AGENT_REMEDIATION_ENABLED` | `true` | Optional remediation generation |

Set any of the last three to `false` to disable that post-processing block (all are implemented in `main.run_agent_scan` after `SkepticAgent`).

### Scan / validation

| Variable | Default | Role |
|----------|---------|------|
| `PHASE1_CONFIDENCE_THRESHOLD` / `PHASE2_CONFIDENCE_THRESHOLD` | `6.0` | FP filter thresholds |
| `FREE_TIER_PHASE2_MAX_FINDINGS` | `8` | Tier 1 Phase 2 cap |
| `SKEPTIC_PASS_ENABLED` | `true` | Post-scan SkepticPass on worker |
| `SKEPTIC_CVSS_THRESHOLD` | `7.0` | Which findings SkepticPass prioritizes |
| `SCAN_DIFF_ENABLED` | `true` | Incremental scan support in worker utilities |
| `DEPENDENCY_SCANNER_ENABLED` | `true` | OSV-backed dependency/CVE correlation |
| `GIT_CONTEXT_ENABLED` | `true` | Git churn / recency signals |
| `HIGH_RECALL_MODE` | `false` | Keep more low-confidence items as informational |
| `FP_FILTER_STRICTNESS` | `strict` | FP filter behavior |
| `LOG_SERVER_URL` | — | If set, `AgentLogger` POSTs events for live dashboards |

### Infrastructure

| Variable | Default | Role |
|----------|---------|------|
| `WORKER_SECRET` | — | Gateway ↔ worker auth |
| `REDIS_HOST` / `REDIS_PORT` | `localhost` / `6379` | Context + scan state |
| `REDIS_OPTIONAL` | `0` | `1` allows in-memory fallback (tests / no Redis) |

---

## 4. Core Python modules (worker)

| Area | Paths |
|------|--------|
| Tier scans | `ai_tier1.py`, `ai_tier2.py`, `ai_tier3.py`, `llm_centric_detector.py` |
| Indexing | `LLMindexer.py` (DeepWiki + IR), `project_indexer.py`, `indexers/*` |
| Enrichment | `enrichment/dataflow_hints.py`, `file_risk_ranker.py`, `context_slicer.py` (package `enrichment`) |
| FP filter / validation | `findings_filter.py`, `findings_validator.py`, `validation/skeptic_pass.py`, `validation/multi_signal_scorer.py` |
| Agents | `agents/coordinator.py`, `agents/base_agent.py`, `agents/openrouter_agentic.py`, `agents/pipeline_tools.py`, `agents/skill.md`, `agents/specialists/*` |
| Agent synthesis | `agents/deduplication_engine.py`, `agents/consensus_scorer.py`, `agents/skeptic_agent.py`, optional `chain_combiner.py`, `attack_path_simulator.py`, `remediation_agent.py` |

---

## 5. Gateway behaviors worth citing in a thesis

1. **Regex index** runs to completion before per-file `/scan` jobs are submitted.
2. **DeepWiki** is kicked with a **short HTTP timeout** (`timeout=45` on the kick request); the worker still runs the full `POST /index_project_deepwiki` pipeline (which can take much longer). The gateway **does not block** the scan on DeepWiki finishing.
3. **Per-file scans** and **DeepWiki + agent scan** therefore **overlap in time** for tiers 2–4.
4. **`_merge_agent_findings_from_redis`** (after all files complete) polls Redis for up to **120 seconds** for `agent_findings`, then **appends the same mapped agent findings to every result row** so the stored report includes project-level findings even when per-file worker responses missed them (e.g. race before `deepwiki_complete`).
5. **`request_cross_file_consistency`** posts aggregated vulnerabilities to the worker’s `/cross_file_consistency` endpoint (when configured) before persisting the final report.

---

## 6. Auth / CSRF (gateway)

`backend/csrf_helpers.py` integrates with Flask sessions: state-changing routes expect CSRF validation; `GET /api/csrf-token` and the `XSRF-TOKEN` cookie expose the token to the frontend. Details belong in a security chapter, not duplicated here.
