"""
SAST-Test-Server - Intentionally vulnerable API for LLM-powered SAST benchmarking.
WARNING: DO NOT use in production. Contains deliberate security flaws.
"""

import os
import re
import sqlite3
import subprocess
import pickle
import yaml
import hashlib
import zipfile
import tempfile
import csv
import io
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Optional

import jwt
import requests
from fastapi import FastAPI, Request, Query, Form, File, UploadFile, Header, Depends, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse, PlainTextResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import Template
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager

# ============ CONFIG (VULNERABLE) ============
SECRET_KEY = "sast_test_secret_key_do_not_use_in_prod_2024"
JWT_ALGORITHM = "HS256"
DATABASE_PATH = Path(__file__).parent / "sast_test.db"
UPLOAD_DIR = Path(__file__).parent / "uploads"
EXPORT_DIR = Path(__file__).parent / "exports"
UPLOAD_DIR.mkdir(exist_ok=True)
EXPORT_DIR.mkdir(exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    # shutdown if needed


app = FastAPI(title="SAST Test API", description="Intentional vulns for scanner testing", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ DB HELPERS ============
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
            role TEXT DEFAULT 'user',
            api_key TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            product TEXT,
            quantity INTEGER,
            total REAL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY,
            action TEXT,
            user_id INTEGER,
            details TEXT,
            ip TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute(
        "INSERT OR IGNORE INTO users (id, username, password, email, role) VALUES (1, 'admin', ?, 'admin@test.com', 'admin')",
        (hashlib.md5(b"Admin123!").hexdigest(),),
    )
    conn.commit()
    conn.close()


# ============ AUTH (WEAK) ============
def sign_jwt(user_id: int, role: str) -> str:
    return jwt.encode(
        {"sub": str(user_id), "role": role, "exp": datetime.utcnow() + timedelta(days=7)},
        SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


def decode_jwt(token: str, algo: Optional[str] = None) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[algo or JWT_ALGORITHM])


# ============ ROUTES WITH VULNERABILITIES ============

@app.post("/api/auth/register")
async def register(request: Request):
    """VULN: Mass assignment + SQLi + MD5."""
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
    return {"id": uid, "token": sign_jwt(uid, role)}


@app.post("/api/auth/login")
async def login(request: Request):
    """VULN: SQLi auth bypass."""
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
    return {"token": sign_jwt(row["id"], row["role"]), "user": dict(row)}


@app.get("/api/users/{user_id}")
async def get_user(user_id: str, request: Request):
    """VULN: IDOR + SQLi."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"SELECT id, username, email, role, api_key FROM users WHERE id = '{user_id}'")
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, "User not found")
    return dict(row)


@app.get("/api/orders")
async def list_orders(order_id: Optional[str] = Query(None), request: Request = None):
    """VULN: SQLi via query param."""
    conn = get_db()
    cur = conn.cursor()
    if order_id:
        cur.execute(f"SELECT * FROM orders WHERE id = '{order_id}'")
    else:
        cur.execute("SELECT * FROM orders")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.post("/api/orders")
async def create_order(request: Request):
    """VULN: SQLi in INSERT + mass assignment."""
    data = await request.json()
    user_id = data.get("user_id", 1)
    product = data.get("product", "")
    quantity = int(data.get("quantity", 1))
    total = float(data.get("total", 0))
    notes = data.get("notes", "")
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        f"INSERT INTO orders (user_id, product, quantity, total, notes) VALUES ({user_id}, '{product}', {quantity}, {total}, '{notes}')"
    )
    conn.commit()
    oid = cur.lastrowid
    conn.close()
    return {"order_id": oid}


@app.get("/api/search")
async def search(q: str = Query(...)):
    """VULN: SQLi in search."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM orders WHERE product LIKE '%{q}%' OR notes LIKE '%{q}%'")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.post("/api/report/generate")
async def generate_report(request: Request):
    """VULN: SSTI (Jinja2)."""
    data = await request.json()
    template_str = data.get("template", "Report for {{ title }}")
    title = data.get("title", "Default")
    try:
        t = Template(template_str)
        out = t.render(title=title, date=datetime.utcnow())
        return {"report": out}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/config/import")
async def import_config(request: Request):
    """VULN: Insecure deserialization (pickle)."""
    body = await request.body()
    try:
        config = pickle.loads(body)
        return {"config": str(config)}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


@app.post("/api/config/yaml")
async def load_yaml(request: Request):
    """VULN: YAML deserialization (unsafe load)."""
    data = await request.json()
    yaml_str = data.get("yaml", "{}")
    try:
        obj = yaml.load(yaml_str, Loader=yaml.Loader)
        return {"parsed": obj}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


@app.get("/api/logs")
async def get_logs(file: str = Query("app.log")):
    """VULN: Command injection."""
    path = f"/var/log/sast_test/{file}"
    try:
        out = subprocess.check_output(f"cat {path}", shell=True)
        return PlainTextResponse(out.decode())
    except Exception as e:
        return PlainTextResponse("No logs", status_code=404)


@app.get("/api/ping")
async def ping(host: str = Query("127.0.0.1")):
    """VULN: Command injection (ping)."""
    try:
        out = subprocess.check_output(f"ping -c 2 {host}", shell=True, timeout=5)
        return PlainTextResponse(out.decode())
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


@app.get("/api/fetch")
async def fetch_url(url: str = Query(...)):
    """VULN: SSRF."""
    try:
        r = requests.get(url, timeout=10)
        return {"status": r.status_code, "content": r.text[:2000]}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


@app.get("/api/redirect")
async def redirect_me(redirect_url: str = Query(...)):
    """VULN: Open redirect."""
    return RedirectResponse(redirect_url, status_code=302)


@app.get("/api/file/read")
async def read_file(path: str = Query(...)):
    """VULN: Path traversal - user path joined with base, no validation."""
    base = Path(__file__).parent / "uploads"
    full = base / path
    try:
        return FileResponse(full)
    except Exception:
        raise HTTPException(404)


@app.post("/api/file/upload")
async def upload_file(file: UploadFile = File(...)):
    """VULN: Unrestricted upload (no type/size check)."""
    dest = UPLOAD_DIR / file.filename
    content = await file.read()
    dest.write_bytes(content)
    return {"path": str(dest), "size": len(content)}


@app.post("/api/export/zip")
async def export_zip(file: UploadFile = File(...)):
    """VULN: Zip slip."""
    zip_path = UPLOAD_DIR / (file.filename or "upload.zip")
    content = await file.read()
    zip_path.write_bytes(content)
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(EXPORT_DIR)
    zip_path.unlink(missing_ok=True)
    return {"extracted_to": str(EXPORT_DIR)}


@app.get("/api/export/csv")
async def export_csv(order_ids: str = Query(...)):
    """VULN: SQLi + CSV formula injection."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM orders WHERE id IN ({order_ids})")
    rows = cur.fetchall()
    conn.close()
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["ID", "User", "Product", "Quantity", "Total", "Notes"])
    for r in rows:
        w.writerow([r["id"], r["user_id"], r["product"], r["quantity"], r["total"], r["notes"]])
    return PlainTextResponse(
        buf.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=export.csv"},
    )


@app.post("/api/payment/xml")
async def payment_xml(request: Request):
    """VULN: XXE."""
    body = await request.body()
    try:
        root = ET.fromstring(body)
        card = root.find(".//card_number")
        amount = root.find(".//amount")
        return {"card_last4": (card.text or "")[-4:], "amount": amount.text if amount is not None else None}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


@app.post("/api/token/decode")
async def token_decode(request: Request):
    """VULN: JWT algorithm confusion (user-controlled algo)."""
    data = await request.json()
    token = data.get("token", "")
    algo = data.get("algorithm", "HS256")
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[algo])
        return {"decoded": decoded}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


@app.get("/api/debug/env")
async def debug_env():
    """VULN: Information disclosure."""
    return {
        "env": dict(os.environ),
        "secret_key": SECRET_KEY,
        "cwd": os.getcwd(),
    }


@app.get("/api/validate/regex")
async def validate_regex(pattern: str = Query(...), text: str = Query("")):
    """VULN: ReDoS (catastrophic backtracking)."""
    try:
        m = re.match(pattern, text)
        return {"match": m is not None}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


@app.get("/api/ldap/search")
async def ldap_search(username: str = Query(...)):
    """VULN: LDAP injection (filter built from user input)."""
    try:
        import ldap
        conn = ldap.initialize("ldap://localhost")
        conn.simple_bind_s("cn=admin,dc=test,dc=com", "admin")
        filter_str = f"(uid={username})"
        results = conn.search_s("ou=users,dc=test,dc=com", ldap.SCOPE_SUBTREE, filter_str)
        conn.unbind()
        return {"results": str(results)}
    except ImportError:
        return {"results": f"(uid={username}) - ldap not installed"}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


@app.get("/api/audit")
async def audit(request: Request, x_forwarded_host: Optional[str] = Header(None)):
    """VULN: Host header injection in response."""
    host = request.headers.get("host", "localhost")
    base = x_forwarded_host or host
    return {"audit_url": f"http://{base}/admin/audit", "message": "OK"}


if __name__ == "__main__":
    init_db()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5008)
