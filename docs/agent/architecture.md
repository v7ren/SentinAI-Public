# Architecture

SentinAI v4 is an AI-powered SAST tool with a multi-agent pipeline. Before LLM-heavy scanning, recon/pattern/threat-model style agents build project context (call graph, dependencies, sanitizers, dead code). Specialist agents run in parallel, then deduplication, consensus scoring, and Skeptic-style validation.

The product is **local-only**: a Tauri desktop app plus Python/OpenCode processes on loopback. There is no hosted web UI.

## Three-tier layout

```
Tauri desktop (desktop/, Vite :1420 in dev)
  └─ POST /api/scan/local-start + SSE /api/scan/events
        → backend/client.py (:5001, 127.0.0.1) [open-source gateway]
             └─ x-secret → backend/closesource.py (:5002) [proprietary engine]
                  └─ OpenCode bridge :5010 (DeepSeek completions)
```

## Scan pipeline (high level)

1. **Indexing** — Regex symbol table plus DeepWiki-style context where enabled.
2. **Agent phase 1** — Recon, pattern, threat-model style briefings.
3. **Agent phase 2** — Parallel specialist agents (injection, auth, crypto, cipher design, logic, config, etc.).
4. **Agent phase 3** — Deduplication, consensus scoring, adversarial validation (Skeptic).
5. **Optional** — Scan diff, dependency/CVE correlation (OSV), git context, LLM security specialist.

## Where logic lives

| Area | Primary locations |
| --- | --- |
| Desktop UI | `desktop/` (Tauri + Vite) |
| Gateway (local-start, SSE) | `backend/client.py` launches `backend/mainflask.py` |
| Engine HTTP wrapper | `backend/closesource.py` launches `backend/worker/core/main.py` |
| Tier scans, LLM detector, PoC, keywords | `backend/worker/core/ai_tier*.py`, `llm_centric_detector.py`, `poc.py`, `keywords.py`, `findings_filter.py` |
| Multi-agent orchestration | `backend/worker/core/agents/` |
| Pre-scan enrichment | `backend/worker/core/enrichment/` |
| Indexers (deps, calls, sanitizers, dead code) | `backend/worker/core/indexers/` |
| Post-scan validation | `backend/worker/core/validation/`, `skeptic_pass.py` |
| DeepWiki helpers | `LLMindexer.py`, `deepwiki_utils.py` |

## Legacy / avoid for new work

- `backend/local_scan_server.py` — standalone CLI pattern; still referenced for local-only flows.
- Do not add a browser/Next.js UI. Desktop is the only frontend.
