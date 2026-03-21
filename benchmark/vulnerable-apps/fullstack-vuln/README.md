# fullstack-vuln

**WARNING: For education and SAST benchmarking only. This application contains intentional security vulnerabilities. Do not deploy publicly or expose to the internet.**

Production-style full-stack app (Python Flask backend + React frontend) with **multiple connected Python modules** and a realistic UI for testing custom SAST tools. Context-rich: vulnerabilities span config, database layer, models, services, and routes so that finding them requires cross-file data-flow analysis.

## Folder tree

```
fullstack-vuln/
├── backend/
│   ├── app.py              # Flask app, blueprints
│   ├── config.py           # Settings, secrets
│   ├── database.py         # DB connection, query helpers
│   ├── models/
│   │   ├── user.py         # User CRUD, raw SQL
│   │   └── profile.py      # Profile CRUD, raw SQL
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── profile_service.py
│   │   ├── search_service.py
│   │   ├── upload_service.py
│   │   ├── admin_service.py
│   │   ├── util_runner.py
│   │   └── config_loader.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── profile.py
│   │   ├── search.py
│   │   ├── upload.py
│   │   ├── admin.py
│   │   └── tools.py
│   ├── middleware/
│   │   └── auth.py
│   ├── requirements.txt
│   └── data/               # DB + uploads (created at runtime)
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── Layout.jsx
│   │   ├── api.js
│   │   ├── pages/
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Profiles.jsx
│   │   │   ├── ProfileEdit.jsx
│   │   │   ├── Search.jsx
│   │   │   ├── Upload.jsx
│   │   │   └── Admin.jsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── run_backend.py
├── README.md
├── SAFE_VARIANT.md
└── (vulnerability map: ../fullstack-vuln.md in `benchmark/vulnerable-apps` root)
```

## Features

- **Auth:** Register, login, logout, session; weak hashing and role in registration.
- **Profile CRUD:** Create, read, update profiles; get by ID without ownership check.
- **Search:** Full-text search over profiles (query flows to SQL).
- **File upload:** Upload and download files; path from client used as-is.
- **Admin:** List users with API key (hardcoded in config).
- **Tools (API only):** Run command, load config (pickle), eval expression, echo (reflected in HTML).

## Run

From repo root (or from `benchmark/vulnerable-apps/fullstack-vuln`):

```bash
cd benchmark/vulnerable-apps/fullstack-vuln

# Backend (Python 3.8+)
pip install -r backend/requirements.txt
python run_backend.py
# Or: PYTHONPATH=. python backend/app.py
# Backend: http://localhost:5010

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
# Frontend: http://localhost:5173 (proxies /api to backend)
```

For production-like serve: build frontend (`npm run build`), then run backend only; it serves `frontend/dist` at `/`.

## Compare vulnerable vs fixed

Use the `safe` branch or follow `SAFE_VARIANT.md`. Exact vulnerability locations and data flow are documented in `../fullstack-vuln.md` in the `benchmark/vulnerable-apps` root.

## Warning

This app must **never** be deployed publicly. Use only in isolated test environments for SAST tool evaluation.
