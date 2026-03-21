# Safe variant – how to fix each vulnerability

1. **SQL Injection** – Use parameterized queries only (e.g. `cur.execute("SELECT ... WHERE id = ?", (id,))`). Never build SQL from user input with string formatting.
2. **Command Injection** – Do not pass user input to `subprocess.getoutput` or shell. Use allowlists or avoid shell; if needed, use `subprocess.run` with a list and no user-controlled command string.
3. **IDOR** – Verify the authenticated user may access the resource (profile belongs to user or user is admin). Check ownership before returning or updating.
4. **Weak auth/session** – Strong JWT secret from env, short expiry, bcrypt/argon2 for passwords. Enforce admin via role from token/DB, not a single hardcoded key.
5. **Hardcoded secret** – Load SECRET_KEY and ADMIN_API_KEY from environment or secret manager.
6. **Insecure file upload / path traversal** – Validate file type/size; save with server-generated names. For file read, resolve path and ensure it is under UPLOAD_DIR (e.g. `Path.resolve()` and prefix check).
7. **XSS** – Do not reflect user input into HTML. Use templating with escaping or return JSON; set Content-Type appropriately.
8. **Unsafe deserialization / eval** – Do not use `pickle.loads` on untrusted data; do not use `eval()` on user input. Use JSON and safe parsers only.

## Toggle / branch strategy

- `main`: vulnerable code for benchmarking.
- `safe`: branch with the above fixes.
