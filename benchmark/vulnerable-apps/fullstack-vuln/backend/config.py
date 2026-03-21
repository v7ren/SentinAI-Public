import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = Path(__file__).resolve().parent

SECRET_KEY = "fullstack_prod_secret_key_8f3a2b1c_do_not_use"
SESSION_COOKIE_NAME = "fs_session"
SESSION_COOKIE_HTTPONLY = False
SESSION_COOKIE_SECURE = False

DATABASE_PATH = BACKEND_DIR / "data" / "app.db"
UPLOAD_DIR = BACKEND_DIR / "data" / "uploads"
EXPORT_DIR = BACKEND_DIR / "data" / "exports"

ADMIN_API_KEY = "fullstack_admin_apikey_9x7y2z"
INTERNAL_SERVICE_TOKEN = "internal_svc_token_12345"
DB_CONNECTION_STRING = "sqlite:///" + str(DATABASE_PATH)

for d in (DATABASE_PATH.parent, UPLOAD_DIR, EXPORT_DIR):
    d.mkdir(parents=True, exist_ok=True)
