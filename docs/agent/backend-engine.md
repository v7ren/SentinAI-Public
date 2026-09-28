# Backend: proprietary scan engine

**Entry:** `backend/closesource.py` (FastAPI), typically port **5002**. **Do not distribute** as open source—contains LLM prompts, detection logic, and multi-agent implementation.

## Responsibilities

- Receives per-request `OPENROUTER_API_KEY` from the gateway.
- Runs tiered scans and the v4 multi-agent pipeline.
- Hosts enrichment, indexers, validation, PoC generation, DeepWiki indexing as wired in the worker core.

## Core layout (`backend/worker/core/`)

| Concern | Files / folders |
| --- | --- |
| Tier scanning & central detector | `ai_tier1.py`, `ai_tier2.py`, `ai_tier3.py`, `llm_centric_detector.py` |
| Agents & specialists | `agents/` |
| Enrichment | `enrichment/` (e.g. dataflow hints, risk ranker, context slicer) |
| Indexers | `indexers/` (file deps, call graph, sanitizer registry, dead code) |
| Validation | `validation/`, `skeptic_pass.py` |
| PoC / keywords / filtering | `poc.py`, `keywords.py`, `findings_filter.py`, `findings_validator.py`, `context_compactor.py` |
| DeepWiki | `LLMindexer.py`, `deepwiki_utils.py` |
| Config | `config.py` |
| Shared schemas (OSS-safe subset) | `models.py` |

## Modes

- **GUI:** launcher/status UI via `_run_gui()`.
- **Headless:** `python closesource.py --headless [--port ...]`.

## Dynamic docs note

Runtime-generated DeepWiki markdown may appear under `backend/worker/core/deepwiki_docs/` — treat as scan output, not hand-edited agent docs.
