# fullstack-vuln – Vulnerability locations and exploit steps

This document describes where each intentional vulnerability lives in the **fullstack-vuln** project (multiple connected Python files + frontend) and how to reproduce the insecure behavior. Use it to evaluate custom SAST tools that must perform cross-file data-flow analysis. **Do not deploy this app publicly.**

---

## 1. SQL Injection (CWE-89)

- **Location (data flow):**
  - **Auth:** `routes/auth.py` → `services/auth_service.py` (`verify_user`, `register_user`) → `models/user.py` (`find_user_by_credentials`, `create_user`). Raw SQL built with `%` in `user.py`.
  - **Profile:** `routes/profile.py` → `services/profile_service.py` → `models/profile.py` (`get_profile_by_id`, `create_profile`, `update_profile`, `search_profiles`). String formatting used for `profile_id`, `display_name`, `bio`, `query`.
  - **Search:** `routes/search.py` → `services/search_service.py` → `models/profile.py` (`search_profiles`). Query interpolated into LIKE.
- **Vulnerable files:** `backend/models/user.py`, `backend/models/profile.py`.
- **Example (auth bypass):**
  ```bash
  curl -X POST http://localhost:5010/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"x\" OR \"1\"=\"1"}'
  ```
- **Expected insecure behavior:** Authentication bypass, data leakage, or modification via crafted inputs in login, register, profile, or search.

---

## 2. Command Injection (CWE-78)

- **Location:** `routes/tools.py` (`run`) → `services/util_runner.py` (`run_system_command`) → `subprocess.getoutput(cmd)`. User-controlled `cmd` flows from request body to shell.
- **Example:**
  ```bash
  curl -X POST http://localhost:5010/api/tools/run \
    -H "Content-Type: application/json" \
    -d '{"cmd":"id; cat /etc/passwd"}'
  ```
- **Expected insecure behavior:** Arbitrary shell commands executed with the process user.

---

## 3. Broken Access Control / IDOR (CWE-639)

- **Location:** `routes/profile.py` (`get_one(profile_id)`) → `services/profile_service.py` (`get_profile`) → `models/profile.py` (`get_profile_by_id`). No check that the requester owns the profile or is admin.
- **Example:**
  ```bash
  curl http://localhost:5010/api/profile/1
  ```
- **Expected insecure behavior:** Any caller can read any profile by ID without authentication or authorization.

---

## 4. Weak auth/session handling (CWE-287 / CWE-384)

- **Location:** `config.py` (predictable `SECRET_KEY`), `services/auth_service.py` (MD5 for passwords), `middleware/auth.py` (session only; no strict binding). Admin protection is a single shared API key in `config.py` used by `services/admin_service.py`.
- **Example:** Use SQLi in login to bypass; or capture/reuse session cookie.
- **Expected insecure behavior:** Session hijack or auth bypass; weak admin protection.

---

## 5. Hardcoded secret/credential (CWE-798)

- **Location:** `backend/config.py` – `SECRET_KEY`, `ADMIN_API_KEY`, `INTERNAL_SERVICE_TOKEN` (and optionally `DB_CONNECTION_STRING`) hardcoded in source.
- **Example:**
  ```bash
  curl -H "X-API-Key: fullstack_admin_apikey_9x7y2z" http://localhost:5010/api/admin/users
  ```
- **Expected insecure behavior:** Anyone with source or build can impersonate admin or forge sessions.

---

## 6. Insecure file upload / path traversal (CWE-434 / CWE-22)

- **Upload:** `routes/upload.py` → `services/upload_service.py` (`save_upload`). Client filename used as-is; no type or size check.
- **Path traversal:** `routes/upload.py` (`file_get`) → `services/upload_service.py` (`get_file_stream` → `resolve_file_path`). `name` is joined with `UPLOAD_DIR` via `base / relative_path` without resolving or ensuring the result stays under the upload directory.
- **Example (path traversal):**
  ```bash
  curl "http://localhost:5010/api/file?name=../../../etc/passwd"
  ```
- **Expected insecure behavior:** Reading files outside the uploads directory; upload of arbitrary or overwriting files.

---

## 7. XSS (CWE-79)

- **Location (backend):** `routes/tools.py` (`echo`) – GET `/api/tools/echo?msg=...`. `msg` is concatenated into an HTML response with no escaping.
- **Example:**
  ```bash
  curl "http://localhost:5010/api/tools/echo?msg=<script>alert(1)</script>"
  ```
- **Expected insecure behavior:** Reflected XSS when the response is viewed in a browser.

---

## 8. Unsafe deserialization / eval-like sink (CWE-502 / CWE-94)

- **Pickle:** `routes/tools.py` (`config_load`) → `services/config_loader.py` (`load_config_from_bytes`) → `pickle.loads(data)`. Raw request body is deserialized.
- **Eval:** `routes/tools.py` (`eval_route`) → `services/config_loader.py` (`evaluate_expression`) → `eval(expr)`. User-supplied `expr` is executed.
- **Example (eval):**
  ```bash
  curl -X POST http://localhost:5010/api/tools/eval \
    -H "Content-Type: application/json" \
    -d '{"expr":"__import__(\"os\").system(\"id\")"}'
  ```
- **Expected insecure behavior:** Remote code execution.

---

## Cross-file data flow (for SAST)

- **Request → Route → Service → Model/DB:** e.g. `GET /api/profile/<id>` → `profile.py` → `profile_service.get_profile(id)` → `profile.get_profile_by_id(conn, id)` → raw SQL in `profile.py`.
- **Request → Route → Service → subprocess/eval/pickle:** e.g. `POST /api/tools/run` → `tools.py` → `util_runner.run_system_command(cmd)` → `subprocess.getoutput(cmd)`.
- **Config → Service:** e.g. `config.ADMIN_API_KEY` → `admin_service.get_all_users(api_key)`.

**Summary:** Vulnerabilities are spread across `backend/config.py`, `backend/database.py`, `backend/models/user.py`, `backend/models/profile.py`, `backend/services/*.py`, and `backend/routes/*.py`. The frontend does not contain the intentional backend vulnerabilities; XSS is in the backend echo endpoint. Use only in an isolated environment. Fixes: see the project's `SAFE_VARIANT.md`.
