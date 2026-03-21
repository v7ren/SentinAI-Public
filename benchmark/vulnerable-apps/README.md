# Vulnerable benchmark apps

**WARNING: All apps in this folder are deliberately vulnerable and for SAST benchmarking / education only. Do not deploy any of them publicly.**

## Contents

About **6** intentionally vulnerable training apps: 5 minimal API-only apps and 1 **production-style full-stack** app with frontend and multiple connected Python files for context-rich SAST testing.

| Project              | Stack        | Port | Vulnerability map (one level up)   |
|----------------------|-------------|------|-------------------------------------|
| `flask-app-vuln`     | Python/Flask | 5001 | [flask-app-vuln.md](./flask-app-vuln.md)   |
| `express-app-vuln`   | Node/Express| 5002 | [express-app-vuln.md](./express-app-vuln.md) |
| `fastapi-app-vuln`   | Python/FastAPI | 5003 | [fastapi-app-vuln.md](./fastapi-app-vuln.md) |
| `django-app-vuln`    | Python/Django | 5004 | [django-app-vuln.md](./django-app-vuln.md)  |
| `go-gin-vuln`       | Go/Gin      | 5005 | [go-gin-vuln.md](./go-gin-vuln.md)         |
| **`fullstack-vuln`** | **Flask + React** | **5010 + 5173** | [fullstack-vuln.md](./fullstack-vuln.md) – **multi-file backend, production-like UI** |

## Vulnerability map (per app)

Each app has a **single markdown file in this directory** (`benchmark/vulnerable-apps` root) named **`<project-folder>.md`** (e.g. `flask-app-vuln.md`). That file describes:

- Exact vulnerable endpoint/function
- Exploitable request example (e.g. curl)
- Expected insecure behavior

The vulnerable code itself **does not** contain comments that indicate where the vulnerability is.

## Per-app docs

Inside each project folder you will find:

- **README.md** – Warning, folder tree, how to run, pointer to the root-level `<name>.md`
- **SAFE_VARIANT.md** – How to fix each vulnerability and a toggle/branch strategy for comparing vulnerable vs fixed

## Running

From repo root:

```bash
# Flask
cd benchmark/vulnerable-apps/flask-app-vuln && pip install -r requirements.txt && python app.py

# Express
cd benchmark/vulnerable-apps/express-app-vuln && npm install && npm start

# FastAPI
cd benchmark/vulnerable-apps/fastapi-app-vuln && pip install -r requirements.txt && python main.py

# Django
cd benchmark/vulnerable-apps/django-app-vuln && pip install -r requirements.txt && python manage.py migrate && python manage.py runserver 0.0.0.0:5004

# Go
cd benchmark/vulnerable-apps/go-gin-vuln && go mod tidy && go run main.go

# Fullstack (production-like: Flask backend + React frontend, multiple Python files)
cd benchmark/vulnerable-apps/fullstack-vuln && pip install -r backend/requirements.txt && python run_backend.py
# In another terminal: cd benchmark/vulnerable-apps/fullstack-vuln/frontend && npm install && npm run dev
# Backend: http://localhost:5010  |  Frontend: http://localhost:5173
```

## Warning

These applications must **never** be deployed publicly. Use only in isolated test environments for SAST tool benchmarking and security training.
