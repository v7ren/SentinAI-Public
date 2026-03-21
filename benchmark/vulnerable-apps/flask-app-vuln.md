# flask-app-vuln – Vulnerability locations and exploit steps

This document describes where each intentional vulnerability lives in the `flask-app-vuln` project and how to reproduce the insecure behavior. **Do not deploy this app publicly.**

---

## 1. SQL Injection (CWE-89)

- **Location:** `flask-app-vuln/app.py` – multiple routes that build SQL via string formatting.
  - `register()`: INSERT with `username`, `email`, `role` concatenated.
  - `login()`: SELECT with `username` in WHERE.
  - `get_profile(profile_id)`: SELECT with `profile_id` in WHERE.
  - `create_profile()`: INSERT with `display_name`, `bio`.
  - `update_profile(profile_id)`: UPDATE with `profile_id`, `display_name`, `bio`.
  - `search()`: SELECT with `q` in LIKE.
- **Example (auth bypass):**
  ```bash
  curl -X POST http://localhost:5001/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin\" OR \"1\"=\"1","password":"x"}'
  ```
- **Expected insecure behavior:** Login may succeed without correct password; data may be leaked or modified via crafted input in other endpoints.

---

## 2. Command Injection (CWE-78)

- **Location:** `flask-app-vuln/app.py`, function `run_cmd()` – POST `/api/run`. User-controlled `cmd` is passed to `subprocess.getoutput(cmd)`.
- **Example:**
  ```bash
  curl -X POST http://localhost:5001/api/run \
    -H "Content-Type: application/json" \
    -d '{"cmd":"id; cat /etc/passwd"}'
  ```
- **Expected insecure behavior:** Arbitrary shell commands run with the process privileges.

---

## 3. Broken Access Control / IDOR (CWE-639)

- **Location:** `flask-app-vuln/app.py`, function `get_profile(profile_id)` – GET `/api/profile/<profile_id>`. No check that the requester owns this profile or is admin.
- **Example:**
  ```bash
  curl http://localhost:5001/api/profile/1
  ```
- **Expected insecure behavior:** Any caller can read any profile by ID without authentication or authorization.

---

## 4. Weak auth/session handling (CWE-287 / CWE-384)

- **Location:** `flask-app-vuln/app.py` – weak session and auth design: predictable `SECRET_KEY`, MD5 for passwords, session not tied to robust verification. Admin route protected only by a single shared API key (see also CWE-798).
- **Example:** Omit session cookie or use a guessed/default secret; or use SQLi in login to bypass (see SQLi section).
- **Expected insecure behavior:** Session hijack or auth bypass possible; admin protection is a single shared key.

---

## 5. Hardcoded secret/credential (CWE-798)

- **Location:** `flask-app-vuln/app.py` top-level – `API_KEY_ADMIN`, `DB_API_KEY`, and `app.config["SECRET_KEY"]` are hardcoded in source.
- **Example:**
  ```bash
  curl -H "X-API-Key: admin_api_key_12345" http://localhost:5001/api/admin/users
  ```
- **Expected insecure behavior:** Anyone with source or leaked build can impersonate admin or compromise session signing.

---

## 6. Insecure file upload / path traversal (CWE-434 / CWE-22)

- **Upload:** `flask-app-vuln/app.py`, function `upload()` – POST `/api/upload`. Filename from client is used as-is; no type/size check. Allows overwriting and arbitrary extension.
- **Path traversal:** `flask-app-vuln/app.py`, function `read_file()` – GET `/api/file?name=...`. `name` is joined with upload folder without resolving or checking that the result stays under the folder.
- **Example (path traversal):**
  ```bash
  curl "http://localhost:5001/api/file?name=../../../etc/passwd"
  ```
- **Expected insecure behavior:** Reading files outside uploads directory; upload of executable or overwrite of critical files.

---

## 7. XSS (CWE-79)

- **Location:** `flask-app-vuln/app.py`, function `echo()` – GET `/api/echo?msg=...`. `msg` is reflected into HTML with no escaping.
- **Example:**
  ```bash
  curl "http://localhost:5001/api/echo?msg=<script>alert(1)</script>"
  ```
- **Expected insecure behavior:** Response contains unescaped script; if viewed in a browser, script runs.

---

## 8. Unsafe deserialization / eval-like sink (CWE-502 / CWE-94)

- **Pickle:** `flask-app-vuln/app.py`, function `config_load()` – POST `/api/config/load`. Raw body is passed to `pickle.loads()`.
- **Eval:** `flask-app-vuln/app.py`, function `do_eval()` – POST `/api/eval`. User-supplied `expr` is passed to `eval()`.
- **Example (eval):**
  ```bash
  curl -X POST http://localhost:5001/api/eval \
    -H "Content-Type: application/json" \
    -d '{"expr":"__import__(\"os\").system(\"id\")"}'
  ```
- **Example (pickle):** Send a serialized payload (e.g. from a pickle RCE generator) in the body of POST `/api/config/load`.
- **Expected insecure behavior:** Remote code execution.

---

**Summary:** All vulnerabilities are in `flask-app-vuln/app.py`. Use the examples above in an isolated environment only. Fixes are described in the project's `SAFE_VARIANT.md`.
