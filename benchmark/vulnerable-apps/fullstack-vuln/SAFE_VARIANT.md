# Safe variant – how to fix each vulnerability

1. **SQL Injection** – Use parameterized queries everywhere. In `database.py`, pass params to `execute_query` and use `?` placeholders; in `models/user.py` and `models/profile.py`, never build SQL with `%` or format from user input.
2. **Command Injection** – Remove or replace the run endpoint; do not pass user input to `subprocess.getoutput` or any shell command.
3. **IDOR** – In `profile_service.get_profile` and routes that fetch by ID, verify the authenticated user owns the resource or has admin role before returning or updating.
4. **Weak auth/session** – Use a strong secret from environment; use bcrypt/argon2 for passwords; set httpOnly and secure cookie flags; enforce admin via role from DB/session, not a single shared API key.
5. **Hardcoded secret** – Load `SECRET_KEY`, `ADMIN_API_KEY`, and any tokens from environment or a secret manager.
6. **Insecure file upload / path traversal** – Validate file type and size; save with server-generated names. For file read, resolve path (e.g. `Path.resolve()`) and ensure the result is under the upload directory (e.g. `resolved.is_relative_to(upload_dir)`).
7. **XSS** – Do not reflect user input into HTML. In the echo endpoint, return plain text or JSON; if HTML is required, use proper escaping/templating. In the frontend, avoid `dangerouslySetInnerHTML` with user-controlled data.
8. **Unsafe deserialization / eval** – Do not use `pickle.loads` on request body; do not use `eval()` on user input. Use JSON and safe parsers only.

## Toggle / branch strategy

- `main`: vulnerable code for SAST benchmarking.
- `safe`: branch with the above fixes so scanners can compare vulnerable vs fixed.
