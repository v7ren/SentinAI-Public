import os
import subprocess
import pickle
import hashlib
from pathlib import Path
from django.conf import settings
from django.http import JsonResponse, HttpResponse, FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import connection
from django.core.files.storage import default_storage
from app.models import User, Profile

UPLOAD_DIR = Path(settings.BASE_DIR) / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


def _get_user_id(request):
    return request.session.get("user_id")


@csrf_exempt
@require_http_methods(["POST"])
def register(request):
    import json
    data = json.loads(request.body or "{}")
    username = data.get("username", "")
    password = data.get("password", "")
    email = data.get("email", "")
    role = data.get("role", "user")
    pw_hash = hashlib.md5(password.encode()).hexdigest()
    with connection.cursor() as cur:
        cur.execute(
            f"INSERT INTO app_user (username, password, email, role) VALUES ('{username}', '{pw_hash}', '{email}', '{role}')"
        )
        cur.execute("SELECT last_insert_rowid()")
        row = cur.fetchone()
        uid = row[0]
    request.session["user_id"] = uid
    request.session["role"] = role
    return JsonResponse({"id": uid, "role": role})


@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    import json
    data = json.loads(request.body or "{}")
    username = data.get("username", "")
    password = data.get("password", "")
    pw_hash = hashlib.md5(password.encode()).hexdigest()
    with connection.cursor() as cur:
        cur.execute(f"SELECT id, username, role FROM app_user WHERE username = '{username}' AND password = '{pw_hash}'")
        row = cur.fetchone()
    if not row:
        return JsonResponse({"error": "Invalid credentials"}, status=401)
    request.session["user_id"] = row[0]
    request.session["role"] = row[2]
    return JsonResponse({"id": row[0], "role": row[2]})


@require_http_methods(["GET"])
def get_profile(request, profile_id):
    with connection.cursor() as cur:
        cur.execute(
            f"SELECT p.id, p.user_id, p.display_name, p.bio, u.username FROM app_profile p JOIN app_user u ON p.user_id = u.id WHERE p.id = '{profile_id}'"
        )
        row = cur.fetchone()
    if not row:
        return JsonResponse({"error": "Not found"}, status=404)
    return JsonResponse({"id": row[0], "user_id": row[1], "display_name": row[2], "bio": row[3], "username": row[4]})


@csrf_exempt
@require_http_methods(["POST"])
def create_profile(request):
    uid = _get_user_id(request)
    if uid is None:
        return JsonResponse({"error": "Unauthorized"}, status=401)
    import json
    data = json.loads(request.body or "{}")
    display_name = data.get("display_name", "")
    bio = data.get("bio", "")
    with connection.cursor() as cur:
        cur.execute(f"INSERT INTO app_profile (user_id, display_name, bio) VALUES ({uid}, '{display_name}', '{bio}')")
        cur.execute("SELECT last_insert_rowid()")
        pid = cur.fetchone()[0]
    return JsonResponse({"id": pid})


@csrf_exempt
@require_http_methods(["POST"])
def update_profile(request, profile_id):
    uid = _get_user_id(request)
    if uid is None:
        return JsonResponse({"error": "Unauthorized"}, status=401)
    import json
    data = json.loads(request.body or "{}")
    display_name = data.get("display_name", "")
    bio = data.get("bio", "")
    with connection.cursor() as cur:
        cur.execute(f"UPDATE app_profile SET display_name = '{display_name}', bio = '{bio}' WHERE id = '{profile_id}'")
    return JsonResponse({"ok": True})


@require_http_methods(["GET"])
def search(request):
    q = request.GET.get("q", "")
    with connection.cursor() as cur:
        cur.execute(f"SELECT id, user_id, display_name, bio FROM app_profile WHERE display_name LIKE '%{q}%' OR bio LIKE '%{q}%'")
        rows = cur.fetchall()
    return JsonResponse([{"id": r[0], "user_id": r[1], "display_name": r[2], "bio": r[3]} for r in rows], safe=False)


@csrf_exempt
@require_http_methods(["POST"])
def upload(request):
    uid = _get_user_id(request)
    if uid is None:
        return JsonResponse({"error": "Unauthorized"}, status=401)
    f = request.FILES.get("file")
    if not f:
        return JsonResponse({"error": "No file"}, status=400)
    path = UPLOAD_DIR / f.name
    with open(path, "wb") as out:
        for chunk in f.chunks():
            out.write(chunk)
    return JsonResponse({"path": f.name, "size": path.stat().st_size})


@require_http_methods(["GET"])
def read_file(request):
    name = request.GET.get("name", "")
    full = UPLOAD_DIR / name
    if not full.exists():
        return JsonResponse({"error": "Not found"}, status=404)
    return FileResponse(open(full, "rb"))


@csrf_exempt
@require_http_methods(["POST"])
def run_cmd(request):
    import json
    data = json.loads(request.body or "{}")
    cmd = data.get("cmd", "id")
    out = subprocess.getoutput(cmd)
    return JsonResponse({"output": out})


@require_http_methods(["GET"])
def admin_users(request):
    key = request.headers.get("X-Api-Key") or request.GET.get("api_key", "")
    if key != getattr(settings, "ADMIN_API_KEY", "django_admin_key_123"):
        return JsonResponse({"error": "Forbidden"}, status=403)
    with connection.cursor() as cur:
        cur.execute("SELECT id, username, email, role FROM app_user")
        rows = cur.fetchall()
    return JsonResponse([{"id": r[0], "username": r[1], "email": r[2], "role": r[3]} for r in rows], safe=False)


@csrf_exempt
@require_http_methods(["POST"])
def config_load(request):
    try:
        obj = pickle.loads(request.body)
        return JsonResponse({"config": str(obj)})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def do_eval(request):
    import json
    data = json.loads(request.body or "{}")
    expr = data.get("expr", "1+1")
    try:
        result = eval(expr)
        return JsonResponse({"result": result})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@require_http_methods(["GET"])
def echo(request):
    msg = request.GET.get("msg", "")
    return HttpResponse("<html><body>Message: " + msg + "</body></html>", content_type="text/html")


@require_http_methods(["GET"])
def index(request):
    return HttpResponse(
        """
    <html><head><title>Django Benchmark</title></head>
    <body>
    <div style="background:#f00;color:#fff;padding:8px;">WARNING: This app is for SAST benchmarking only. Do not deploy publicly.</div>
    <p>API: /api/auth/login, /api/profile, /api/search, /api/upload, /api/admin/users</p>
    </body></html>
    """,
        content_type="text/html",
    )
