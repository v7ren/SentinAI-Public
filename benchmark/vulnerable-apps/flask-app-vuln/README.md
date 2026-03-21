# flask-app-vuln

**WARNING: For education and SAST benchmarking only. This application contains intentional security vulnerabilities. Do not deploy publicly or expose to the internet.**

## Folder tree

```
flask-app-vuln/
├── app.py
├── requirements.txt
├── README.md
├── SAFE_VARIANT.md
└── uploads/          (created at runtime)
```

## Features (feature parity with secure app)

- Auth: register, login (session-based)
- Profile CRUD: create, read, update profile
- File upload and download
- Search (profiles)
- Admin route: list users (protected by API key)

## Run

```bash
cd benchmark/vulnerable-apps/flask-app-vuln
pip install -r requirements.txt
python app.py
```

API base: `http://localhost:5001`

## Compare vulnerable vs fixed

Use the `safe` branch or follow `SAFE_VARIANT.md` to apply fixes. No in-code markers for vulnerabilities; see `../flask-app-vuln.md` in the `benchmark/vulnerable-apps` root for exact locations and exploit steps.

## Warning

This app must never be deployed publicly. Use only in isolated test environments for SAST tool evaluation.
