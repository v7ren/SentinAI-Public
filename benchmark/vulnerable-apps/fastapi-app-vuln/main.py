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

from fastapi import FastAPI, Request, Query, File, UploadFile, Depends, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="FastAPI Benchmark")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

SECRET_KEY = "fastapi_bench_secret_2024"
ADMIN_API_KEY = "fastapi_admin_key_xyz"
DATABASE_PATH = Path(__file__).parent / "bench.db"
UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
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
            role TEXT DEFAULT 'user'
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            display_name TEXT,
            bio TEXT
        )
    """)
    cur.execute(
        "INSERT OR IGNORE INTO users (id, username, password, email, role) VALUES (1, 'admin', ?, 'admin@test.com', 'admin')",
        (hashlib.md5(b"Admin123!").hexdigest(),),
    )
    conn.commit()
    conn.close()


@app.on_event("startup")
def startup():
    init_db()


def get_current_user(request: Request):
    auth = request.headers.get("Authorization") or request.cookies.get("user_id")
    if auth and auth.startswith("Bearer "):
        token = auth[7:]
        try:
            import jwt
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return payload.get("sub"), payload.get("role")
        except Exception:
            pass
    return None, None


@app.post("/api/auth/register")
async def register(request: Request):
    data = await request.json()
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
    import jwt
    token = jwt.encode({"sub": str(uid), "role": role}, SECRET_KEY, algorithm="HS256")
    return {"id": uid, "token": token}


@app.post("/api/auth/login")
async def login(request: Request):
    data = await request.json()
    username = data.get("username", "")
    password = data.get("password", "")
    pw_hash = hashlib.md5(password.encode()).hexdigest()
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM users WHERE username = '{username}' AND password = '{pw_hash}'")
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(401, "Invalid credentials")
    import jwt
    token = jwt.encode({"sub": str(row["id"]), "role": row["role"]}, SECRET_KEY, algorithm="HS256")
    return {"token": token, "user": dict(row)}


@app.get("/api/profile/{profile_id}")
async def get_profile(profile_id: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"SELECT p.*, u.username FROM profiles p JOIN users u ON p.user_id = u.id WHERE p.id = '{profile_id}'")
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, "Not found")
    return dict(row)


@app.post("/api/profile")
async def create_profile(request: Request):
    uid, _ = get_current_user(request)
    if uid is None:
        raise HTTPException(401, "Unauthorized")
    data = await request.json()
    display_name = data.get("display_name", "")
    bio = data.get("bio", "")
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"INSERT INTO profiles (user_id, display_name, bio) VALUES ({uid}, '{display_name}', '{bio}')")
    conn.commit()
    pid = cur.lastrowid
    conn.close()
    return {"id": pid}


@app.put("/api/profile/{profile_id}")
async def update_profile(profile_id: str, request: Request):
    uid, _ = get_current_user(request)
    if uid is None:
        raise HTTPException(401, "Unauthorized")
    data = await request.json()
    display_name = data.get("display_name", "")
    bio = data.get("bio", "")
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"UPDATE profiles SET display_name = '{display_name}', bio = '{bio}' WHERE id = '{profile_id}'")
    conn.commit()
    conn.close()
    return {"ok": True}


@app.get("/api/search")
async def search(q: str = Query("")):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM profiles WHERE display_name LIKE '%{q}%' OR bio LIKE '%{q}%'")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.post("/api/upload")
async def upload(request: Request, file: UploadFile = File(...)):
    uid, _ = get_current_user(request)
    if uid is None:
        raise HTTPException(401, "Unauthorized")
    dest = UPLOAD_DIR / file.filename
    content = await file.read()
    dest.write_bytes(content)
    return {"path": file.filename, "size": len(content)}


@app.get("/api/file")
async def read_file(name: str = Query("")):
    full = UPLOAD_DIR / name
    if not full.exists():
        raise HTTPException(404, "Not found")
    return FileResponse(full)


@app.post("/api/run")
async def run_cmd(request: Request):
    data = await request.json()
    cmd = data.get("cmd", "id")
    out = subprocess.getoutput(cmd)
    return {"output": out}


@app.get("/api/admin/users")
async def admin_users(request: Request):
    key = request.headers.get("X-API-Key") or request.query_params.get("api_key", "")
    if key != ADMIN_API_KEY:
        raise HTTPException(403, "Forbidden")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, username, email, role FROM users")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.post("/api/config/load")
async def config_load(request: Request):
    body = await request.body()
    try:
        obj = pickle.loads(body)
        return {"config": str(obj)}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


@app.post("/api/eval")
async def do_eval(request: Request):
    data = await request.json()
    expr = data.get("expr", "1+1")
    try:
        result = eval(expr)
        return {"result": result}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


@app.get("/api/echo")
async def echo(msg: str = Query("")):
    return HTMLResponse("<html><body>Message: " + msg + "</body></html>")


@app.get("/")
async def index():
    return HTMLResponse("""
    <html><head><title>FastAPI Benchmark</title></head>
    <body>
    <div style="background:#f00;color:#fff;padding:8px;">WARNING: This app is for SAST benchmarking only. Do not deploy publicly.</div>
    <p>API: /api/auth/login, /api/profile, /api/search, /api/upload, /api/admin/users</p>
    </body></html>
    """)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5003)
