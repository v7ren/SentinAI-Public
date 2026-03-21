# django-app-vuln

**WARNING: For education and SAST benchmarking only. This application contains intentional security vulnerabilities. Do not deploy publicly or expose to the internet.**

## Folder tree

```
django-app-vuln/
├── manage.py
├── requirements.txt
├── README.md
├── SAFE_VARIANT.md
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── app/
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py
│   └── views.py
└── uploads/   (created at runtime)
```

## Features

- Auth: register, login (session)
- Profile CRUD
- File upload and download
- Search
- Admin route: list users (X-API-Key)

## Run

```bash
cd benchmark/vulnerable-apps/django-app-vuln
pip install -r requirements.txt
python manage.py migrate
python manage.py shell -c "
from app.models import User
import hashlib
h = hashlib.md5(b'Admin123!').hexdigest()
User.objects.get_or_create(username='admin', defaults={'password':h, 'email':'admin@test.com', 'role':'admin'})
"
python manage.py runserver 0.0.0.0:5004
```

API base: `http://localhost:5004`

## Compare vulnerable vs fixed

Use the `safe` branch or follow `SAFE_VARIANT.md`. Exact vulnerability locations and exploit steps: see `../django-app-vuln.md` in the `benchmark/vulnerable-apps` root.

## Warning

This app must never be deployed publicly. Use only in isolated test environments for SAST tool evaluation.
