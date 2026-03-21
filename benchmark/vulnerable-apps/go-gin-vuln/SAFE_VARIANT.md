# Safe variant – how to fix each vulnerability

1. **SQL Injection** – Use parameterized queries only (e.g. `db.Exec("INSERT ... VALUES (?,?,?)", a, b, c)`). Never build SQL with fmt.Sprintf from user input.
2. **Command Injection** – Do not pass user input to `exec.Command("sh", "-c", ...)`. Remove the endpoint or use strict allowlists; avoid shell and user-controlled command strings.
3. **IDOR** – Verify the authenticated user may access the resource (profile belongs to user or user is admin). Check ownership before returning or updating.
4. **Weak auth/session** – Strong secret from env, secure cookie flags, bcrypt/argon2 for passwords. Enforce admin via role from session/DB.
5. **Hardcoded secret** – Load secretKey and adminAPIKey from environment.
6. **Insecure file upload / path traversal** – Validate file type/size; save with server-generated names. For file read, resolve path with filepath.Clean and ensure result is under uploadDir (e.g. filepath.HasPrefix or similar check).
7. **XSS** – Do not reflect user input into HTML. Use templating with escaping or return JSON; set Content-Type.
8. **Unsafe deserialization / eval-like** – Do not use `gob.Decode` on untrusted request body; do not pass user input into shell commands (doEval/runCmd). Use JSON decoding only; remove or replace eval-like endpoints.

## Toggle / branch strategy

- `main`: vulnerable code for benchmarking.
- `safe`: branch with the above fixes.
