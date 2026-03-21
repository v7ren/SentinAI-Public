# SAST Test Server — Planted Vulnerabilities (Ground Truth)

Use this list to measure **recall** of your LLM-powered SAST: run the scanner on `vulnerable-server-sast-test` and check how many of the entries below it reports.

**Stack:** FastAPI (backend, port 5008) + React/Vite (frontend, port 3002). Different from vulnerable-server-bank (Flask + Next.js).

---

## Backend (`backend/main.py`)

| # | Vulnerability | Approx line | CWE | Pattern / trigger |
|---|---------------|-------------|-----|-------------------|
| 1 | SQL injection (register) | ~95 | CWE-89 | `f"INSERT INTO users ... '{username}', ... '{role}'"` |
| 2 | SQL injection (login) | ~108 | CWE-89 | `f"SELECT * FROM users WHERE username = '{username}' ..."` |
| 3 | SQL injection (get_user) | ~118 | CWE-89 | `f"SELECT ... WHERE id = '{user_id}'"` |
| 4 | SQL injection (list_orders) | ~128 | CWE-89 | `f"SELECT * FROM orders WHERE id = '{order_id}'"` |
| 5 | SQL injection (create_order) | ~145 | CWE-89 | `f"INSERT INTO orders ... '{product}', ... '{notes}'"` |
| 6 | SQL injection (search) | ~156 | CWE-89 | `f"SELECT ... WHERE product LIKE '%{q}%'"` |
| 7 | SQL injection (export_csv) | ~228 | CWE-89 | `f"SELECT * FROM orders WHERE id IN ({order_ids})"` |
| 8 | Mass assignment (register) | ~88 | CWE-915 | Accepts `role` from JSON |
| 9 | IDOR (get_user) | ~115 | CWE-639 | No check that requester owns `user_id` |
| 10 | Weak password hashing (MD5) | ~93, ~106 | CWE-327 | `hashlib.md5(password.encode()).hexdigest()` |
| 11 | Hardcoded secret | ~28 | CWE-798 | `SECRET_KEY = "sast_test_secret_key_..."` |
| 12 | SSTI (Jinja2) | ~166 | CWE-94 | `Template(template_str).render(...)` user input |
| 13 | Insecure deserialization (pickle) | ~178 | CWE-502 | `pickle.loads(body)` |
| 14 | Insecure deserialization (YAML) | ~188 | CWE-502 | `yaml.load(yaml_str, Loader=yaml.Loader)` |
| 15 | Command injection (logs) | ~198 | CWE-78 | `subprocess.check_output(f"cat {path}", shell=True)` |
| 16 | Command injection (ping) | ~207 | CWE-78 | `subprocess.check_output(f"ping -c 2 {host}", shell=True)` |
| 17 | SSRF | ~216 | CWE-918 | `requests.get(url)` user-controlled URL |
| 18 | Open redirect | ~224 | CWE-601 | `RedirectResponse(redirect_url)` no validation |
| 19 | Path traversal (read_file) | ~232 | CWE-22 | Path from query joined with base, resolve check can be bypassed if logic buggy |
| 20 | Unrestricted file upload | ~243 | CWE-434 | No extension/size validation, write `file.filename` |
| 21 | Zip slip | ~254 | CWE-22 | `z.extractall(EXPORT_DIR)` no path validation |
| 22 | CSV formula injection | ~264 | CWE-1236 | Row data written to CSV without sanitizing `=`, `+`, `-` |
| 23 | XXE | ~276 | CWE-611 | `ET.fromstring(body)` no entity disabling |
| 24 | JWT algorithm confusion | ~286 | CWE-327 | `jwt.decode(..., algorithms=[algo])` user-controlled `algo` |
| 25 | Information disclosure (debug) | ~296 | CWE-200 | Exposes `os.environ`, `SECRET_KEY` |
| 26 | ReDoS | ~306 | CWE-1333 | `re.match(pattern, text)` user-controlled regex |
| 27 | LDAP injection | ~316 | CWE-90 | `filter_str = f"(uid={username})"` |
| 28 | Host header injection | ~328 | CWE-644 | `base_url = f"http://{x_forwarded_host or host}"` in response |

---

## Frontend

| # | File | Vulnerability | Approx line | CWE | Pattern |
|---|------|---------------|-------------|-----|---------|
| 29 | `src/pages/Home.jsx` | DOM XSS (hash) | ~16 | CWE-79 | `el.innerHTML = decodeURIComponent(hash)` |
| 30 | `src/pages/Home.jsx` | Prototype pollution | ~24 | CWE-1321 | `{ ...defaults, ...parsed }` with URL `?config=` |
| 31 | `src/pages/Home.jsx` | postMessage + eval | ~36 | CWE-94 | `eval(event.data.code)` no origin check |
| 32 | `src/pages/Home.jsx` | Reflected XSS | ~58 | CWE-79 | `dangerouslySetInnerHTML={{ __html: \`...${banner}\` }}` |
| 33 | `src/pages/Login.jsx` | Plaintext credentials in localStorage | ~45 | CWE-312 | `localStorage.setItem('login_creds', JSON.stringify({ u, p }))` |
| 34 | `src/pages/Login.jsx` | Open redirect | ~48 | CWE-601 | `navigate(searchParams.get('next') || '/dashboard')` |
| 35 | `src/pages/Login.jsx` | Debug credential exposure | ~41 | CWE-200 | `setDebug(\`Logging in: ${username} / ${password}\`)` with `?debug=true` |
| 36 | `src/pages/Register.jsx` | Mass assignment (role) | ~28 | CWE-915 | `body: JSON.stringify(form)` includes `role` |
| 37 | `src/pages/Dashboard.jsx` | JWT in localStorage | ~26, ~44 | CWE-522 | `localStorage.getItem('token')`, token shown in UI |
| 38 | `src/pages/Dashboard.jsx` | Client-side JWT decode | ~32 | CWE-347 | `JSON.parse(atob(token.split('.')[1]))` no verify |
| 39 | `src/pages/Admin.jsx` | Triggers backend command injection | ~28, ~38 | — | Passes user input to `/api/ping`, `/api/logs` |
| 40 | `src/pages/Export.jsx` | Client-side open redirect | ~28 | CWE-601 | `window.location.href = redirectTo` |

---

## Summary

- **Backend:** 28 planted issues (SQLi, SSTI, pickle, YAML, command injection, SSRF, path traversal, zip slip, XXE, JWT, ReDoS, LDAP, host header, etc.).
- **Frontend:** 12+ planted issues (XSS, prototype pollution, eval/postMessage, localStorage credentials/token, open redirect, mass assignment, client-side JWT decode).
- **Total:** 40+ distinct vulnerability instances for recall/precision benchmarking.

Run your SAST on the repo and compare reported findings to this list. Track true positives, false negatives (missed), and false positives (reported but not in this list).
