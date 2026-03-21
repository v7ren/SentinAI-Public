# Safe variant – how to fix each vulnerability

1. **SQL Injection** – Use Django ORM or parameterized `connection.cursor().execute(sql, [params])`. Never interpolate user input into SQL strings.
2. **Command Injection** – Do not pass user input to `subprocess.getoutput` or shell. Use allowlists or remove the endpoint.
3. **IDOR** – Verify the authenticated user may access the resource (profile belongs to user or user is admin). Check ownership in the view.
4. **Weak auth/session** – Strong SECRET_KEY from env, secure session config, bcrypt/argon2 for passwords. Enforce admin via role from session/DB.
5. **Hardcoded secret** – Load SECRET_KEY and ADMIN_API_KEY from environment.
6. **Insecure file upload / path traversal** – Validate file type/size; save with server-generated names. For file read, resolve path and ensure it is under UPLOAD_DIR.
7. **XSS** – Do not reflect user input into HTML. Use Django templates with auto-escaping or return JSON.
8. **Unsafe deserialization / eval** – Do not use `pickle.loads` on request body; do not use `eval()` on user input. Use JSON only.

## Toggle / branch strategy

- `main`: vulnerable code for benchmarking.
- `safe`: branch with the above fixes.
