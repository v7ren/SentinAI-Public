# SAST Server Benchmark — Analysis

Generated: 2026-03-05T19:02:27.187919

## Summary

| Server | Status | Files with vulns | Total findings |
|--------|--------|-------------------|----------------|
| XBEN-005-24 | OK | 2 | 3 |

## Ground truth comparison

- **01-vulnerable-server**: In-repo Flask + Next.js; no formal count in this run.
- **02-vulnerable-server-bank**: See `benchmark/servers/vulnerable-server-bank/VULNERABILITIES.md` for expected issues (NoSQL, LDAP, XSS, etc.).
- **03-vulnerable-server-sast-test**: **40+** planted issues (see `temp/VULNERABILITIES.md`). Compare findings to that list for recall/precision.
- **04-juice-shop**: OWASP Top 10; compare CWE coverage (SQLi, XSS, auth, etc.).
- **05-xbow**: XBOW validation benchmarks; compare to published detection rates.

## How well the SAST performed

### XBEN-005-24

- CWE-915: 2
- CWE-798: 1

### Conclusion

Review the result.json files in each server folder for full findings. Use temp/VULNERABILITIES.md and benchmark/servers/vulnerable-server-bank/VULNERABILITIES.md to compute true positives and false negatives for servers 02 and 03.
