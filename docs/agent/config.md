# Configuration (`backend/worker/core/config.py`)

Important boolean-style toggles (names as in CLAUDE.md; verify current defaults in the file):

| Flag | Effect |
| --- | --- |
| `AGENT_SCAN_ENABLED` | Multi-agent pipeline on/off |
| `SCAN_DIFF_ENABLED` | Incremental scan on changed files |
| `DEPENDENCY_SCANNER_ENABLED` | OSV CVE correlation |
| `SKEPTIC_PASS_ENABLED` | Adversarial validation pass |
| `HIGH_RECALL_MODE` | Retain low-confidence findings as informational |

When editing behavior, search for these symbols in `config.py` and follow imports into the modules that consume each flag.
