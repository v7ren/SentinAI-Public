# Benchmark servers — 5 vulnerable apps for SAST testing

Used by `run_server_benchmark.py`. Servers are listed in `benchmark/servers_config.txt` (source paths relative to project root).

| ID | App | Source | Ground truth |
|----|-----|--------|--------------|
| 01 | vulnerable-server | `benchmark/servers/vulnerable-server/` | See repo docs |
| 02 | vulnerable-server-bank | `benchmark/servers/vulnerable-server-bank/` | `benchmark/servers/vulnerable-server-bank/VULNERABILITIES.md` |
| 03 | vulnerable-server-sast-test | `benchmark/servers/vulnerable-server-sast-test/` | `temp/VULNERABILITIES.md` (40+ issues) |
| 04 | OWASP Juice Shop | Cloned into `04-juice-shop/` | OWASP Top 10 |
| 05 | XBOW validation (Python) | Cloned into `05-xbow/` | XBOW challenges |

**Setup:** `python benchmark/setup_benchmark_servers.py`  
**Run scans:** `python benchmark/run_server_benchmark.py` (uses `.env.benchmark`)

Results: `benchmark/servers/<id>-<name>/result.json` and `benchmark/servers/ANALYSIS.md`.
