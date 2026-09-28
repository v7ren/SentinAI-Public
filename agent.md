# Agent index (SentinAI v4)

**How to use this file:** Read this page first. It is intentionally short. Open **only** the linked doc that matches the task so you do not load unrelated context.

| Topic | Open this | What you will find |
| --- | --- | --- |
| Project shape, tiers, scan pipeline | [docs/agent/architecture.md](docs/agent/architecture.md) | Tauri → gateway → engine; multi-agent phases; key directories |
| Commands (Tauri, Python servers, tests) | [docs/agent/commands.md](docs/agent/commands.md) | Desktop, client/engine/bridge entrypoints |
| Environment variables | [docs/agent/environment.md](docs/agent/environment.md) | Client gateway, engine, OpenCode bridge |
| Desktop app (Tauri) | [desktop/README.md](desktop/README.md) | Local UI, in-app settings → `%LOCALAPPDATA%/SentinAI/settings.json` |
| Open-source gateway (`client.py`) | [docs/agent/backend-gateway.md](docs/agent/backend-gateway.md) | Loopback port, local-start + SSE |
| Proprietary scan engine | [docs/agent/backend-engine.md](docs/agent/backend-engine.md) | `closesource.py`, worker core layout, agents / indexers / validation |
| SQLite, Redis, artifacts | [docs/agent/data-storage.md](docs/agent/data-storage.md) | `sentinel.db`, scan output paths, fingerprints |
| Feature toggles | [docs/agent/config.md](docs/agent/config.md) | `config.py` flags that change scan behavior |
| CI, tests, benchmarks | [docs/agent/ci-testing-benchmark.md](docs/agent/ci-testing-benchmark.md) | GitHub Actions, pytest targets, benchmark folders |
| OSS vs proprietary split | [docs/agent/oss-boundary.md](docs/agent/oss-boundary.md) | What may ship in open source vs must stay private |
| Native Rust indexer | [native/sentinai-index/README.md](native/sentinai-index/README.md) | PyO3 `index_project`, maturin build, Python fallback |
| OpenCode → DeepSeek bridge | [backend/opencode-bridge/README.md](backend/opencode-bridge/README.md) | `npm start`; `@opencode-ai/sdk`; `deepseek-flash` only (Go optional) |

**Single-file alternative:** [CLAUDE.md](CLAUDE.md) duplicates much of the above in one document—use it if you prefer one long context block.

**Adding new topics:** Create `docs/agent/<topic>.md`, then add one row to the table above with a one-line description.
