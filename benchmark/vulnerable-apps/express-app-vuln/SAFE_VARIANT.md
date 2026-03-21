# Safe variant – how to fix each vulnerability

1. **SQL Injection** – Use parameterized statements only (e.g. `db.prepare("SELECT ... WHERE id = ?").get(id)`). Never interpolate user input into SQL strings.
2. **Command Injection** – Do not pass user input to `execSync`/`exec`. Remove or replace with allowlisted operations; if shell is required, use strict allowlists and avoid user-controlled command strings.
3. **IDOR** – Verify the authenticated user is allowed to access the resource (e.g. profile belongs to current user or user is admin). Check ownership/role before returning or updating.
4. **Weak auth/session** – Use strong secret from env, httpOnly secure cookies, proper session store. Use bcrypt/argon2 for passwords; do not use MD5. Enforce admin via role from session/DB.
5. **Hardcoded secret** – Load SECRET and ADMIN_KEY from environment or secret manager. Never commit secrets to source.
6. **Insecure file upload / path traversal** – Validate file type and size; save with server-generated names. For file read, resolve path with `path.resolve` and ensure result is under `UPLOAD_DIR` (e.g. `fullPath.startsWith(resolvedUploadDir)`).
7. **XSS** – Do not reflect user input into HTML. Use encoding/templating; return JSON for API and let client escape. Set Content-Type and avoid concatenating user input into HTML.
8. **Unsafe deserialization / eval** – Do not use `eval()` on user input. Do not use `eval` or `Function` to parse request body. Use `JSON.parse` only for JSON; reject other formats.

## Toggle / branch strategy

- `main`: vulnerable code for benchmarking.
- `safe`: branch with the above fixes applied.
