"""
Training app for SAST benchmarking. Education/testing only.
"""

import os
import sqlite3
import subprocess
import pickle
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, request, jsonify, send_file, session, redirect, make_response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config["SECRET_KEY"] = "flask_bench_secret_do_not_use_2024"
app.config["UPLOAD_FOLDER"] = Path(__file__).parent / "uploads"
app.config["DATABASE"] = Path(__file__).parent / "app.db"

API_KEY_ADMIN = "admin_api_key_12345"
DB_API_KEY = "db_internal_key_67890"

app.config["UPLOAD_FOLDER"].mkdir(exist_ok=True)


def get_db():
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            display_name TEXT,
            bio TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute(
        "INSERT OR IGNORE INTO users (id, username, password, email, role) VALUES (1, 'admin', ?, 'admin@test.com', 'admin')",
        (hashlib.md5(b"Admin123!").hexdigest(),),
    )
    conn.commit()
    conn.close()


def require_auth(f):
    @wraps(f)
    def inner(*args, **kwargs):
        uid = session.get("user_id")
        if uid is None:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return inner


@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username", "")
    password = data.get("password", "")
    email = data.get("email", "")
    role = data.get("role", "user")
    conn = get_db()
    cur = conn.cursor()
    pw_hash = hashlib.md5(password.encode()).hexdigest()
    cur.execute(
        f"INSERT INTO users (username, password, email, role) VALUES ('{username}', '{pw_hash}', '{email}', '{role}')"
    )
    conn.commit()
    uid = cur.lastrowid
    conn.close()
    session["user_id"] = uid
    session["role"] = role
    return jsonify({"id": uid, "role": role})


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username", "")
    password = data.get("password", "")
    pw_hash = hashlib.md5(password.encode()).hexdigest()
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM users WHERE username = '{username}' AND password = '{pw_hash}'")
    row = cur.fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Invalid credentials"}), 401
    session["user_id"] = row["id"]
    session["role"] = row["role"]
    return jsonify({"id": row["id"], "role": row["role"]})


@app.route("/api/profile/<profile_id>", methods=["GET"])
def get_profile(profile_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"SELECT p.*, u.username FROM profiles p JOIN users u ON p.user_id = u.id WHERE p.id = '{profile_id}'")
    row = cur.fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Not found"}), 404
    return jsonify(dict(row))


@app.route("/api/profile", methods=["POST"])
@require_auth
def create_profile():
    data = request.get_json() or {}
    display_name = data.get("display_name", "")
    bio = data.get("bio", "")
    uid = session["user_id"]
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        f"INSERT INTO profiles (user_id, display_name, bio) VALUES ({uid}, '{display_name}', '{bio}')"
    )
    conn.commit()
    pid = cur.lastrowid
    conn.close()
    return jsonify({"id": pid})


@app.route("/api/profile/<profile_id>", methods=["PUT"])
@require_auth
def update_profile(profile_id):
    data = request.get_json() or {}
    display_name = data.get("display_name", "")
    bio = data.get("bio", "")
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"UPDATE profiles SET display_name = '{display_name}', bio = '{bio}' WHERE id = '{profile_id}'")
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


@app.route("/api/search", methods=["GET"])
def search():
    q = request.args.get("q", "")
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM profiles WHERE display_name LIKE '%{q}%' OR bio LIKE '%{q}%'")
    rows = cur.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/upload", methods=["POST"])
@require_auth
def upload():
    f = request.files.get("file")
    if not f:
        return jsonify({"error": "No file"}), 400
    path = app.config["UPLOAD_FOLDER"] / f.filename
    f.save(str(path))
    return jsonify({"path": f.filename, "size": os.path.getsize(path)})


@app.route("/api/file", methods=["GET"])
def read_file():
    name = request.args.get("name", "")
    base = app.config["UPLOAD_FOLDER"]
    full = base.joinpath(name)
    if not full.exists():
        return jsonify({"error": "Not found"}), 404
    return send_file(full, as_attachment=False, download_name=name)


@app.route("/api/run", methods=["POST"])
def run_cmd():
    data = request.get_json() or {}
    cmd = data.get("cmd", "id")
    out = subprocess.getoutput(cmd)
    return jsonify({"output": out})


@app.route("/api/admin/users", methods=["GET"])
def admin_users():
    key = request.headers.get("X-API-Key") or request.args.get("api_key", "")
    if key != API_KEY_ADMIN:
        return jsonify({"error": "Forbidden"}), 403
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, username, email, role FROM users")
    rows = cur.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/config/load", methods=["POST"])
def config_load():
    raw = request.get_data()
    try:
        obj = pickle.loads(raw)
        return jsonify({"config": str(obj)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/eval", methods=["POST"])
def do_eval():
    data = request.get_json() or {}
    expr = data.get("expr", "1+1")
    try:
        result = eval(expr)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/echo", methods=["GET"])
def echo():
    msg = request.args.get("msg", "")
    return make_response(f"<html><body>Message: {msg}</body></html>", 200, {"Content-Type": "text/html"})


@app.route("/")
def index():
    return """
    <html><head><title>Flask Benchmark</title></head>
    <body>
    <div style="background:#f00;color:#fff;padding:8px;">WARNING: This app is for SAST benchmarking only. Do not deploy publicly.</div>
    <p>API: /api/auth/login, /api/profile, /api/search, /api/upload, /api/admin/users</p>
    </body></html>
    """


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5001, debug=True)
