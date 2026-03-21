# Safe variant – how to fix each vulnerability

1. **SQL Injection** – Use parameterized queries everywhere (e.g. `cur.execute("SELECT ... WHERE id = ?", (id,))`). Never build SQL with string formatting or concatenation from user input.
2. **Command Injection** – Do not pass user input into `subprocess`/shell. Use allowlists or avoid shell execution; if needed, use `subprocess.run(..., shell=False)` with a list of arguments and no user-controlled command string.
3. **IDOR** – Validate that the authenticated user is allowed to access the requested resource (e.g. profile belongs to current user or user has admin role). Check ownership before returning or updating.
4. **Weak auth/session** – Use strong session secret, HTTPS-only cookies, secure session storage. Prefer bcrypt/argon2 for passwords; do not use MD5. Enforce admin route with proper role check from session/DB, not a single shared API key if that key is hardcoded.
5. **Hardcoded secret** – Load secrets from environment or a secret manager. Remove hardcoded API keys and DB credentials from source.
6. **Insecure file upload / path traversal** – Validate file type and size; save with server-generated names. For file read, resolve path and ensure it stays under the intended directory (e.g. `os.path.realpath` and check prefix).
7. **XSS** – Do not reflect user input into HTML. Use proper templating with escaping, or return JSON and let the client escape. Set `Content-Type` and avoid rendering raw user input in HTML.
8. **Unsafe deserialization / eval** – Do not use `pickle.loads` on untrusted data; do not use `eval()` on user input. Use safe formats (e.g. JSON) and safe parsers.

## Toggle / branch strategy

- Keep a `main` branch with vulnerable code for benchmarking.
- Maintain a `safe` branch (or patch set) that applies the above fixes so scanners can be compared on vulnerable vs fixed code.
