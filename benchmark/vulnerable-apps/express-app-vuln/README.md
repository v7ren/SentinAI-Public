# express-app-vuln

**WARNING: For education and SAST benchmarking only. This application contains intentional security vulnerabilities. Do not deploy publicly or expose to the internet.**

## Folder tree

```
express-app-vuln/
├── server.js
├── package.json
├── README.md
├── SAFE_VARIANT.md
├── uploads/     (created at runtime)
└── data.db      (created at runtime)
```

## Features

- Auth: register, login (cookie-based)
- Profile CRUD
- File upload and download
- Search
- Admin route: list users (X-API-Key)

## Run

```bash
cd benchmark/vulnerable-apps/express-app-vuln
npm install
npm start
```

API base: `http://localhost:5002`

## Compare vulnerable vs fixed

Use the `safe` branch or follow `SAFE_VARIANT.md`. Exact vulnerability locations and exploit steps: see `../express-app-vuln.md` in the `benchmark/vulnerable-apps` root.

## Warning

This app must never be deployed publicly. Use only in isolated test environments for SAST tool evaluation.
