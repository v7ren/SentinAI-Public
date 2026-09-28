# CI, testing, benchmarks

## GitHub Actions

- Workflow: `.github/workflows/sentinai-security.yml`
- Triggers: PR and push to `main` / `master`
- Command (from CLAUDE.md): `backend/worker/core/github_action_scanner.py --scan-type 3 --comment-pr true`

## Tests

See [commands.md](commands.md) for `test.py`, `test_vulnerabilities.py`, and worker pytest path.

## Benchmark fixtures

| Directory | Purpose |
| --- | --- |
| `benchmark/servers/` | Primary vulnerable apps for server benchmarks (e.g. Juice Shop, XBOW-style clones, Flask/Next fixtures) |
| `benchmark/vulnerable-apps/` | Additional multi-stack samples — **do not deploy publicly** |

Runner: `benchmark/run_benchmark.py` (and related scripts in `benchmark/` if present).
