# Realistic Web Apps & Benchmarks for SAST Testing

Use these to test SentinAI (recall, precision, CWE coverage) beyond the in-repo targets (`vulnerable-server`, `vulnerable-server-bank`, and the FastAPI+Vite test server in `temp/VULNERABILITIES.md`).

---

## 1. OWASP Juice Shop

**Best for:** Modern Node/JS stack, OWASP Top 10, REST API, real app surface.

| | |
|---|---|
| **Repo** | https://github.com/juice-shop/juice-shop |
| **Stack** | Node.js, Express, Angular |
| **Deploy** | `docker run -p 3000:3000 bkimminich/juice-shop` or clone + `npm install && npm start` |
| **Docs** | https://owasp.org/www-project-juice-shop, https://pwning.owasp-juice.shop/ |

- Intentionally vulnerable web app with OWASP Top 10 + many real-world flaws.
- Good for SAST: SQLi, XSS (e.g. `bypassSecurityTrustHtml()`), insecure auth, broken access control, etc.
- Distinction: “challenges” (CTF-style) vs “underlying code vulnerabilities”; SAST should find the latter in source.
- Use the **source code** as SAST input (backend + frontend).

---

## 2. XBOW Validation Benchmarks

**Best for:** Tool comparison, known ground truth, low “train set” overlap.

| | |
|---|---|
| **Repo** | https://github.com/xbow-engineering/validation-benchmarks |
| **Blog** | https://xbow.com/blog/benchmarks |
| **Results** | https://xbow-website.pages.dev/results (Google Sheets) |

- **104** small apps (Python + PHP) with intentional vulnerabilities.
- Vulnerability types: SQLi, XSS, IDOR, SSRF, business logic, auth.
- Levels: Easy (L1) → Hard (L3). CTF-style (find a flag).
- Benchmarks were kept confidential until release (no training-data leakage).
- **Warning:** Repo contains unfixed vulns on purpose — use only in isolated environments.
- Use adapted versions if you need false-positive tests (see ZeroPath’s enhancements).

---

## 3. OWASP Benchmark

**Best for:** Standardized SAST/DAST/IAST evaluation, CWE-mapped test cases.

| | |
|---|---|
| **Project** | https://owasp.org/www-project-benchmark |
| **Java** | https://github.com/OWASP-Benchmark/BenchmarkJava |
| **Python** | OWASP Benchmark for Python v0.1 (v1.0 planned 2026) |

- **Java (v1.2):** ~2,740 test cases, 11 categories (SQLi, XSS, Command Injection, Path Traversal, Weak Crypto, etc.). Each case = one CWE, true positive or false positive; runnable servlets.
- **Python:** Early version available; good for aligning with your Python/FastAPI scanning.
- Use for: accuracy, coverage, and speed metrics of your scanner.

---

## 4. OWASP WebGoat

**Best for:** Learning + sanity-checking SAST on classic server-side flaws.

| | |
|---|---|
| **Repo** | https://github.com/WebGoat/WebGoat (e.g. 8.x) |
| **Stack** | Java (Java 11), Spring |

- Deliberately insecure app with lessons on server-side flaws.
- Run: standalone JAR, Docker, or from source.
- Use the **source** as SAST input to see how many exercises’ underlying vulns you find.

---

## 5. Other useful repos

| Name | Repo / link | Notes |
|------|----------------|------|
| **SAST-Benchmark** | https://github.com/vulnerable-code/SAST-Benchmark | Compare multiple SAST tools. |
| **Perdiga SAST benchmark** | https://github.com/perdiga/sast-benchmark | Platform to evaluate SAST tools. |
| **Legion SAST benchmark suite** | https://github.com/legion-sec/sast-benchmark-suite | Multi-language (C#, C++, Go, Node, PHP). |
| **Application Security Toolkit** | https://github.com/wehr-to/application-security-toolkit | Python (Flask, FastAPI) + Node.js; OWASP Top 10, Bandit/Semgrep/ESLint demos. |
| **Vulnerable Node/Express app** | https://github.com/samoylenko/vulnerable-app-nodejs-express | Small Node/Express app with known vulns. |
| **CVE-Bench** | (e.g. arxiv 2503.17332) | Real CVEs; evaluates exploit ability in sandbox; more DAST/agent-oriented. |

---

## Suggested workflow for SentinAI

1. **Quick smoke:** Run on **Juice Shop** source (clone repo, point scanner at root). Check for SQLi, XSS, auth issues.
2. **Structured benchmark:** Run on **XBOW** validation-benchmarks (Python/PHP apps). Compare to published XBOW results (detection rate, false positive rate).
3. **Standard score:** If you add Java support, run **OWASP Benchmark** Java and compute score; for Python-only, use **OWASP Benchmark Python** when v1.0 is out.
4. **In-repo baseline:** Keep using `vulnerable-server`, `vulnerable-server-bank`, and the 40+ ground-truth list in `temp/VULNERABILITIES.md` for recall/precision tracking.

---

## One-line clone & run (examples)

```bash
# Juice Shop (Node)
git clone https://github.com/juice-shop/juice-shop.git && cd juice-shop && npm ci && npm start

# XBOW (Python/PHP – run in isolated env)
git clone https://github.com/xbow-engineering/validation-benchmarks.git
```

Then point SentinAI at the cloned repo (e.g. upload as project or `scan-dir`) and compare findings to expected vulns/challenges.
