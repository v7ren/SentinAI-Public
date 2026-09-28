# SentinAI v4 — Multi-agent security pipeline (detailed)

This document describes the **project-level** multi-agent scan that runs inside the worker after extended indexers complete during `POST /index_project_deepwiki`. Per-file tier scanning (`POST /scan`) is separate; agent output is **merged** into those results and into the final gateway report.

**Code entrypoint:** `backend/worker/core/main.py` → `run_agent_scan()`  
**Orchestration:** `backend/worker/core/agents/coordinator.py` → `AgentCoordinator.run_scan()`  
**LLM client:** `MinimaxClient` from `llm_client.py` with `AGENT_MODEL` (OpenRouter).

---

## 1. When the pipeline runs

| Condition | Behavior |
|-----------|----------|
| `AGENT_SCAN_ENABLED` is false | Skip entirely |
| `OPENROUTER_API_KEY` missing | Skip (logged warning) |
| Tier 1 only (`scan_type` 1) | DeepWiki kick is not used for standard gateway flow; agent scan is not triggered for that path |
| Tiers 2–4 | Worker builds extended maps, then may run `run_agent_scan`, then sets Redis `agent_findings` and `deepwiki_complete` |

**Timing vs. per-file scans:** The Flask gateway starts a **background thread** to call `/index_project_deepwiki` while **per-file `/scan` requests are already in flight**. Therefore:

- Early `/scan` responses may run **before** `deepwiki_complete` is set; the worker then **skips** merging `agent_findings` for that file (see warning log in `main.py`).
- After all files finish, the gateway **`_merge_agent_findings_from_redis`** waits (up to 120s) and attaches agent findings to **every** result row so the stored report is consistent.

---

## 2. Coordinator phases (actual execution order)

### Pre-scan (context enrichment)

1. **ReconAgent** and **PatternAgent** run **in parallel** (`asyncio.gather` of two `to_thread` calls).
2. **ThreatModelAgent** runs **after** both finish, consuming updated `entry_points` and pattern-derived `architecture_patterns`.

Outputs attached to `AgentContext`:

- `entry_points` — routes, handlers, exposure hints  
- `architecture_patterns` — middleware order, ORM, templates, CORS, etc. (`ArchPattern`)  
- `threat_model` — structured threat scenarios from the threat agent  

### Detection (parallel specialists)

All specialists receive the same enriched `AgentContext`. Each `agent.run(context)` is executed in a thread; results are merged into one finding list.

**Default specialists (six):**

| Agent | Module | Focus (high level) |
|-------|--------|---------------------|
| InjectionSpecialist | `specialists/injection_specialist.py` | Injection-class issues |
| AuthSpecialist | `specialists/auth_specialist.py` | Authentication / authorization |
| CryptoSpecialist | `specialists/crypto_specialist.py` | Cryptographic misuse |
| CipherDesignSpecialist | `specialists/cipher_design_specialist.py` | Cipher/mode/padding/IV misuse |
| LogicAnalyst | `specialists/logic_analyst.py` | Business logic flaws |
| ConfigHunter | `specialists/config_hunter.py` | Dangerous configuration |

**Optional seventh:** `LLMSecurityAgent` (`specialists/llm_security_agent.py`) when `AGENT_LLM_SECURITY_ENABLED=true` — prompt injection, unsafe tool use, sensitive data in prompts, etc.

### Agentic tool loop (when enabled)

`BaseAgent` uses `AGENT_AGENTIC_ENABLED` (default true). When on, specialists use **`run_openrouter_agentic_loop`** (`openrouter_agentic.py`) with **`pipeline_tools.PipelineToolExecutor`** — models can request file slices, graph lookups, and other tools instead of consuming full repositories in one prompt. Central instructions are loaded from **`agents/skill.md`** (cached).

---

## 3. Post-coordinator synthesis (`run_agent_scan` in `main.py`)

The coordinator returns raw merged specialist findings. The worker then applies **deterministic + LLM steps** in this order:

1. **DeduplicationEngine** — collapse duplicates (overlapping locations, same class, shared taint sink, etc.).
2. **ConsensusScorer** — boost confidence when multiple agents agree; adjust for chains and dead-code hints.
3. **SkepticAgent** — adversarial pass (sanitizers, dead code, framework defenses, auth context). Findings that survive are tagged so **SkepticPass** on the per-file pipeline can skip re-review when appropriate.
4. **Optional (flags, all default true in `config.py` but can be disabled):**
   - **ChainCombiner** — builds `VulnerabilityChain` objects; may reshape the finding list (chained + unchained).
   - **AttackPathSimulator** — steps / narrative from chains.
   - **RemediationAgent** — fix snippets, tests, verification hints.
5. Serialized artifacts written to Redis: `agent_chains`, `agent_attack_paths`, `agent_remediations` (when non-empty).
6. **AgentLogger.finalize** — progress for optional log server (`LOG_SERVER_URL`).

**Note:** `AgentCoordinator`’s class docstring describes a “post_scan_agents” hook; in the shipped wiring, **`post_scan_agents` is empty** and the above steps live in **`main.run_agent_scan`** after `coordinator.run_scan`.

---

## 4. Output shape and merge

- Findings are converted to the same dict shape as tier findings (`_agent_finding_to_dict`), including `agent_source`, CWE, severity, line, snippet, etc.
- Stored under Redis key **`{scan_id}:agent_findings`**.
- **Per-file Tier 2/3 path:** After tier enrichment, if `deepwiki_complete` is set, worker **extends** `final_result["findings"]` with the full agent list (same findings repeated per file is intentional for downstream filters — gateway merge also duplicates across rows for report symmetry).
- **Tier 4 LLM-centric success path** can **return early** before the Tier 2/3 merge block; rely on **gateway `_merge_agent_findings_from_redis`** for agent rows in that case.
- All merged findings continue through **Phase 1 / Phase 2** FP filtering where the worker pipeline applies them.

---

## 5. Configuration quick reference

See [`ARCHITECTURE_REFERENCE.md`](ARCHITECTURE_REFERENCE.md) for full tables. Agent-relevant keys include:

- `AGENT_MODEL`, `AGENT_SCAN_ENABLED`, `AGENT_AGENTIC_ENABLED`, `AGENT_AGENTIC_MAX_ROUNDS`  
- `AGENT_LLM_SECURITY_ENABLED`  
- `AGENT_CHAIN_COMBINER_ENABLED`, `AGENT_ATTACK_PATH_SIMULATOR_ENABLED`, `AGENT_REMEDIATION_ENABLED`  
- `AGENT_OPENROUTER_TIMEOUT_SECONDS`, `AGENT_MAX_FILE_TOKENS`  
- `LOG_SERVER_URL` (optional live agent dashboard)
