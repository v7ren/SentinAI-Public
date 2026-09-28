# SentinAI v4 — Thesis-oriented notes (problems, design claims, evaluation hooks)

Use this as a **scratchpad for dissertation structure**. It is not a substitute for reading the code; it links concepts to concrete modules so you can cite implementation faithfully.

---

## 1. Problem statement (candidate framing)

- **Traditional SAST** is strong on pattern coverage but weak on semantic context and produces noisy alerts.
- **Single-pass LLM scanning** is strong on reasoning but expensive, inconsistent, and blind to whole-program structure unless context is engineered.
- **SentinAI v4** combines: (1) deterministic indexers and rules, (2) tiered LLM escalation for cost control, (3) a **project-level multi-agent** pass with shared graph context, (4) layered validation (FP filters, optional agentic validator, SkepticPass, multi-signal scoring).

---

## 2. Research contributions you can argue (verify against measurements)

1. **Structured project context before per-file LLM calls** — Regex index + DeepWiki IR + dependency/call-graph/sanitizer/dead-code maps (`indexers/*`, Redis keys in `ARCHITECTURE_REFERENCE.md`).
2. **Economical tiering** — Tier 1 triage (`CHEAP_MODEL`) before `TIER2_MODEL` / `SMART_MODEL` escalation (`ai_tier1.py` … `ai_tier3.py`); Tier 4 flips priority (`llm_centric_detector.py`).
3. **Multi-agent decomposition** — Pre-scan context agents + parallel specialists + deduplication + consensus + skeptic review (`agents/*`, `main.run_agent_scan`).
4. **Defense in depth for false positives** — Hard rules → optional parallel LLM validation → SkepticPass → confidence aggregation (`findings_filter.py`, `findings_validator.py`, `validation/*`).
5. **Operational parallelism vs. correctness** — DeepWiki/agent pipeline overlaps per-file scans; explicit `deepwiki_complete` and gateway **reconciliation merge** mitigate races (`mainflask._merge_agent_findings_from_redis`).

---

## 3. System boundaries for a “methods” section

| Boundary | Responsibility |
|----------|------------------|
| Browser | Upload, SSE consumption, results UI, Clerk |
| Gateway | Persistence, progress events, worker orchestration, final report assembly |
| Worker | All LLM and heavy analysis; Redis-backed shared context |
| Redis | Ephemeral scan state and caches (not long-term audit storage) |
| SQLite / JSON | Durable scan records (`sentinel.db`, `scan_results/`) |

---

## 4. Evaluation ideas (map to repo)

- **Benchmark harness:** `benchmark/run_benchmark.py`, `backend/worker/tests/benchmarks/`, ground-truth manifests.
- **Ablation stories** (conceptual): disable `AGENT_SCAN_ENABLED`; disable extended indexers (compare Tier 1-only vs Tier 2+); toggle `SKEPTIC_PASS_ENABLED`; vary `FP_FILTER_STRICTNESS` / `HIGH_RECALL_MODE`.
- **Cost metrics:** tokens per tier, per-phase validation counts, agent rounds (`AGENT_AGENTIC_MAX_ROUNDS`).
- **Latency:** time to first file result vs. time to DeepWiki completion; effect of gateway 120s agent merge wait.

---

## 5. Ethical / safety angles for a thesis

- Generated **PoCs** (`poc.py`, `/poc`) are offensive aids; document access control, responsible use, and difference from exploit delivery.
- **User code** is sent to third-party LLM APIs (OpenRouter); data handling and retention policies belong in a privacy section.

---

## 6. Glossary (short)

| Term | Meaning in this codebase |
|------|---------------------------|
| DeepWiki | LLM-generated wiki sections + merged markdown under `deepwiki_docs/` + `deepwiki_index` in Redis |
| Agent findings | Project-level vulnerabilities from specialists; merged into per-file pipeline and final report |
| Tier | User-selected scan depth (`x-scan-type` 1–4) |
| Two-phase filter | Hard exclusions (Phase 1) + per-finding LLM validation (Phase 2); Tier 3 may use agentic Phase 2 |
| Skeptic (agent pipeline) | `SkepticAgent` after consensus, inside `run_agent_scan` |
| SkepticPass | Separate post-scan pass on high-severity tier findings |

---

## 7. Suggested chapter outline (editable)

1. Introduction — SAST limits, LLM limits, hybrid motivation.  
2. Requirements — functional (tiers, PoC), non-functional (cost, latency, security).  
3. Architecture — three-tier services; data flow; see main architecture doc.  
4. Indexing & context — regex, DeepWiki IR, graph indexers, Redis.  
5. Multi-agent design — roles, prompts/skill, tool loop, synthesis order.  
6. Per-file scan pipelines — Tier 1–4 decision trees.  
7. Validation & scoring — FP filter, agentic validator, SkepticPass, multi-signal.  
8. Consistency & reporting — cross-file check, gateway merge, fingerprints.  
9. Evaluation — benchmarks, ablations, case studies.  
10. Conclusion — limitations (races, model drift, third-party API dependence).
