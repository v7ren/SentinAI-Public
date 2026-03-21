"""
SecureBank - Online Banking Platform
WARNING: This is an intentionally vulnerable application for SAST testing.
DO NOT use in production. DO NOT deploy with real financial data.
"""

from flask import Flask, request, jsonify, render_template_string, session, make_response, redirect
from flask_cors import CORS
try:
    from pymongo import MongoClient
    from bson.objectid import ObjectId
except ImportError:
    MongoClient = None
    ObjectId = None
from datetime import datetime, timedelta
import jwt
import hashlib
import xml.etree.ElementTree as ET
from xml.dom import minidom
import pickle
import base64
import re
import json
import os
import subprocess
import zipfile
import tempfile
import csv
import io
from ldap3 import Server, Connection, ALL
import requests
from jinja2 import Template

app = Flask(__name__)
app.secret_key = "SecureBank_Production_Key_2024_v1"
CORS(app, supports_credentials=True, origins=["http://localhost:3000"])

# MongoDB connection (for NoSQL injection demos) - optional, falls back to SQLite
MONGO_URI = "mongodb://localhost:27017/securebank"
try:
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=1000)
    mongo_client.admin.command('ping')
    db = mongo_client.securebank
    MONGO_AVAILABLE = True
except:
    mongo_client = None
    db = None
    MONGO_AVAILABLE = False

# SQLite for relational data
DATABASE = os.path.join(os.path.dirname(__file__), "securebank.db")

# File storage
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
STATEMENT_FOLDER = os.path.join(os.path.dirname(__file__), "statements")

LDAP_SERVER_URL = "localhost"
LDAP_BASE_DN = "ou=users,dc=securebank,dc=com"


def init_db():
    """Initialize database with demo data."""
    import sqlite3
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY,
            account_number TEXT UNIQUE,
            user_id TEXT,
            balance REAL DEFAULT 0.0,
            account_type TEXT DEFAULT 'checking',
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY,
            from_account TEXT,
            to_account TEXT,
            amount REAL,
            description TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT,
            phone TEXT,
            role TEXT DEFAULT 'customer',
            ssn TEXT,
            address TEXT,
            credit_score INTEGER,
            session_token TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY,
            card_number TEXT,
            cvv TEXT,
            expiry TEXT,
            user_id INTEGER,
            status TEXT DEFAULT 'active'
        )
    ''')

    # Seed data
    cursor.execute("INSERT OR IGNORE INTO users (id, username, password, email, role, ssn, credit_score) VALUES (1, 'admin', 'Admin123!', 'admin@securebank.com', 'admin', '123-45-6789', 850)")
    cursor.execute("INSERT OR IGNORE INTO users (id, username, password, email, role, ssn, credit_score) VALUES (2, 'john_doe', 'Password123', 'john@example.com', 'customer', '987-65-4321', 720)")
    cursor.execute("INSERT OR IGNORE INTO accounts (id, account_number, user_id, balance, account_type) VALUES (1, 'SB-1000001', '2', 50000.00, 'checking')")
    cursor.execute("INSERT OR IGNORE INTO accounts (id, account_number, user_id, balance, account_type) VALUES (2, 'SB-1000002', '2', 25000.00, 'savings')")
    cursor.execute("INSERT OR IGNORE INTO cards (id, card_number, cvv, expiry, user_id) VALUES (1, '4532-1234-5678-9012', '123', '12/25', 2)")

    conn.commit()
    conn.close()


def get_sqlite_db():
    import sqlite3
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def generate_jwt(user_id, role):
    """Generate JWT token with weak algorithm."""
    payload = {
        "user_id": user_id,
        "role": role,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(days=7),
        "admin": role == "admin"
    }
    # VULNERABILITY: Weak algorithm (None algorithm possible in some JWT libs)
    return jwt.encode(payload, app.secret_key, algorithm="HS256")


# ============ AUTHENTICATION ENDPOINTS ============

@app.route('/api/auth/register', methods=['POST'])
def register():
    """User registration - vulnerable to mass assignment."""
    data = request.get_json()

    # VULNERABILITY: Mass Assignment - accepts any fields from JSON
    user_data = data.copy()
    user_data['created_at'] = datetime.utcnow()

    # VULNERABILITY: Weak password hashing (MD5)
    if 'password' in user_data:
        user_data['password'] = hashlib.md5(user_data['password'].encode()).hexdigest()

    # Insert into MongoDB if available
    mongo_id = None
    if MONGO_AVAILABLE and db:
        try:
            result = db.users.insert_one(user_data)
            mongo_id = str(result.inserted_id)
        except:
            pass

    # Also create SQLite record for transactions
    conn = get_sqlite_db()
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO users (username, password, email, role) VALUES ('{data.get('username')}', '{hashlib.md5(data.get('password', '').encode()).hexdigest()}', '{data.get('email')}', '{data.get('role', 'customer')}')")
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()

    return jsonify({"success": True, "user_id": mongo_id or str(user_id)})


@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login - vulnerable to NoSQL injection."""
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')

    # VULNERABILITY: NoSQL Injection - direct string interpolation into query
    user = None
    if MONGO_AVAILABLE and db:
        try:
            query = {"username": username, "password": hashlib.md5(password.encode()).hexdigest()}
            user = db.users.find_one(query)
        except:
            pass

    # Fallback to SQLite if Mongo fails or unavailable
    if not user:
        conn = get_sqlite_db()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM users WHERE username = '{username}' AND password = '{hashlib.md5(password.encode()).hexdigest()}'")
        user = cursor.fetchone()
        conn.close()

    if user:
        # VULNERABILITY: Session fixation - accepts session ID from client
        import uuid
        session_id = data.get('session_id') or str(uuid.uuid4())

        if hasattr(user, '_id'):
            user_id = str(user['_id'])
            user_role = user.get('role', 'customer')
            user_email = user.get('email', '')
            user_name = user.get('username', '')
        else:
            user_id = str(user['id'])
            user_role = user['role']
            user_email = user['email']
            user_name = user['username']

        session['user_id'] = user_id
        session['role'] = user_role
        session['session_id'] = session_id

        token = generate_jwt(user_id, user_role)

        return jsonify({
            "success": True,
            "token": token,
            "session_id": session_id,
            "user": {
                "id": user_id,
                "username": user_name,
                "role": user_role,
                "email": user_email
            }
        })

    return jsonify({"success": False, "message": "Invalid credentials"}), 401


@app.route('/api/auth/ldap-login', methods=['POST'])
def ldap_login():
    """LDAP authentication - vulnerable to LDAP injection."""
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')

    try:
        # VULNERABILITY: LDAP Injection - unsanitized user input in filter
        ldap_filter = f"(uid={username})"

        server = Server(LDAP_SERVER_URL, get_info=ALL)
        user_dn = f"cn={username},{LDAP_BASE_DN}"

        conn = Connection(server, user=user_dn, password=password, auto_bind=True)
        conn.search(LDAP_BASE_DN, ldap_filter)

        result = conn.entries
        conn.unbind()

        return jsonify({"success": True, "user": str(result)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 401


# ============ ACCOUNT & BALANCE ENDPOINTS ============

@app.route('/api/account/balance')
def get_balance():
    """Get account balance - vulnerable to IDOR."""
    account_number = request.args.get('account', '')

    # VULNERABILITY: IDOR - no authorization check, direct object reference
    conn = get_sqlite_db()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM accounts WHERE account_number = '{account_number}'")
    account = cursor.fetchone()
    conn.close()

    if account:
        return jsonify({
            "account_number": account['account_number'],
            "balance": account['balance'],
            "type": account['account_type']
        })

    return jsonify({"error": "Account not found"}), 404


@app.route('/api/account/statement', methods=['POST'])
def generate_statement():
    """Generate account statement - vulnerable to SSTI and Zip Slip."""
    data = request.get_json()
    account_number = data.get('account_number', '')
    format_type = data.get('format', 'html')
    template_str = data.get('template', '')

    # VULNERABILITY: SSTI (Server-Side Template Injection)
    if template_str:
        try:
            template = Template(template_str)
            rendered = template.render(account_number=account_number, date=datetime.now())
            return jsonify({"statement": rendered})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # VULNERABILITY: Zip Slip - extracts zip without path validation
    if 'archive' in request.files:
        archive = request.files['archive']
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, 'upload.zip')
        archive.save(zip_path)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(STATEMENT_FOLDER)  # No path validation!

        return jsonify({"success": True, "extracted_to": STATEMENT_FOLDER})

    return jsonify({"statement": f"Statement for {account_number} generated"})


@app.route('/api/account/export')
def export_account_data():
    """Export account data - vulnerable to CSV Injection."""
    account_number = request.args.get('account', '')
    format_type = request.args.get('format', 'csv')

    conn = get_sqlite_db()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM transactions WHERE from_account = '{account_number}' OR to_account = '{account_number}'")
    transactions = cursor.fetchall()
    conn.close()

    # VULNERABILITY: CSV Injection - formulas not sanitized
    if format_type == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'From', 'To', 'Amount', 'Description'])

        for t in transactions:
            # VULNERABILITY: Direct user input into CSV (can inject =CMD formulas)
            writer.writerow([t['id'], t['from_account'], t['to_account'], t['amount'], t['description']])

        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=statement_{account_number}.csv'
        return response

    return jsonify({"transactions": [dict(t) for t in transactions]})


# ============ TRANSFER & TRANSACTIONS ============

@app.route('/api/transfer', methods=['POST'])
def transfer_money():
    """Money transfer - vulnerable to race condition and business logic flaw."""
    data = request.get_json()
    from_account = data.get('from_account', '')
    to_account = data.get('to_account', '')
    amount = float(data.get('amount', 0))
    description = data.get('description', '')

    conn = get_sqlite_db()
    cursor = conn.cursor()

    # VULNERABILITY: Race Condition - TOCTOU (Time-of-Check-Time-of-Use)
    # No locking, concurrent requests can overdraw
    cursor.execute(f"SELECT balance FROM accounts WHERE account_number = '{from_account}'")
    source = cursor.fetchone()

    if source and source['balance'] >= amount:
        # VULNERABILITY: Business Logic - doesn't verify from_account belongs to current user
        cursor.execute(f"UPDATE accounts SET balance = balance - {amount} WHERE account_number = '{from_account}'")
        cursor.execute(f"UPDATE accounts SET balance = balance + {amount} WHERE account_number = '{to_account}'")
        cursor.execute(f"INSERT INTO transactions (from_account, to_account, amount, description) VALUES ('{from_account}', '{to_account}', {amount}, '{description}')")
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": f"Transferred ${amount} to {to_account}"})

    conn.close()
    return jsonify({"success": False, "message": "Insufficient funds"}), 400


@app.route('/api/transfer/bulk', methods=['POST'])
def bulk_transfer():
    """Bulk money transfer - vulnerable to mass assignment."""
    data = request.get_json()

    # VULNERABILITY: Mass Assignment - processes all fields blindly
    for transfer in data.get('transfers', []):
        transfer_data = transfer.copy()
        transfer_data['status'] = 'pending'
        transfer_data['created_at'] = datetime.utcnow()

        # Insert into MongoDB without validation
        if MONGO_AVAILABLE and db:
            try:
                db.transactions.insert_one(transfer_data)
            except:
                pass

    return jsonify({"success": True, "message": "Bulk transfers queued"})


# ============ PAYMENT PROCESSING ============

@app.route('/api/payments/process', methods=['POST'])
def process_payment():
    """Process credit card payment - vulnerable to XXE."""
    content_type = request.headers.get('Content-Type', '')

    # VULNERABILITY: XXE (XML External Entity)
    if 'xml' in content_type:
        xml_data = request.data.decode('utf-8')

        try:
            # VULNERABILITY: No entity resolution disabled
            root = ET.fromstring(xml_data)

            card_number = root.find('.//card_number').text
            amount = root.find('.//amount').text

            return jsonify({
                "success": True,
                "card": card_number[-4:],  # Last 4 digits
                "amount": amount,
                "status": "approved"
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400

    # Regular JSON processing
    data = request.get_json()
    return jsonify({"success": True, "message": "Payment processed"})


@app.route('/api/payments/validate-card', methods=['POST'])
def validate_card():
    """Validate credit card - vulnerable to ReDoS."""
    data = request.get_json()
    card_number = data.get('card_number', '')

    # VULNERABILITY: ReDoS (Regular Expression Denial of Service)
    # Catastrophic backtracking pattern
    pattern = r"^(\d+)+$"

    if re.match(pattern, card_number.replace('-', '').replace(' ', '')):
        # Luhn algorithm check
        return jsonify({"valid": True, "card_type": "visa"})

    return jsonify({"valid": False})


# ============ ADMIN & INTERNAL ============

@app.route('/api/admin/users')
def admin_users():
    """Admin user listing - vulnerable to Host Header Injection."""
    host = request.headers.get('Host', '')
    x_forwarded_host = request.headers.get('X-Forwarded-Host', '')

    # VULNERABILITY: Host Header Injection - uses Host header for URL generation
    base_url = f"http://{x_forwarded_host or host}"

    if session.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 403

    users = []
    if MONGO_AVAILABLE and db:
        try:
            users = list(db.users.find({}, {'password': 0}))
        except:
            pass

    # Fallback to SQLite
    if not users:
        conn = get_sqlite_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, role, ssn, credit_score FROM users")
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()

    return jsonify({
        "users": users,
        "admin_panel_url": f"{base_url}/admin"
    })


@app.route('/api/admin/config', methods=['GET', 'POST'])
def admin_config():
    """Admin configuration - vulnerable to deserialization."""
    if session.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 403

    if request.method == 'POST':
        # VULNERABILITY: Insecure Deserialization - accepts pickled data
        config_data = request.data

        try:
            # Dangerous: unpickles user data directly
            config = pickle.loads(config_data)
            if MONGO_AVAILABLE and db:
                try:
                    db.config.update_one({"_id": "main"}, {"$set": config}, upsert=True)
                except:
                    pass
            return jsonify({"success": True, "config": config})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400

    # GET returns current config
    config = {}
    if MONGO_AVAILABLE and db:
        try:
            config = db.config.find_one({"_id": "main"}) or {}
        except:
            pass
    return jsonify({"config": config})


@app.route('/api/admin/logs')
def admin_logs():
    """View application logs - vulnerable to Log Injection and Command Injection."""
    if session.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 403

    # VULNERABILITY: Command Injection - unsanitized input in shell command
    date_filter = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    log_file = f"/var/log/securebank/{date_filter}.log"

    try:
        cmd = f"cat {log_file}"
        logs = subprocess.check_output(cmd, shell=True).decode('utf-8')
        return jsonify({"logs": logs})
    except Exception as e:
        return jsonify({"logs": "No logs available"})


@app.route('/api/admin/ping')
def admin_ping():
    """Network diagnostics - vulnerable to SSRF via HTTP wrapper."""
    if session.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 403

    target = request.args.get('target', 'localhost')

    # VULNERABILITY: SSRF - can access internal services via http://, file://, etc.
    if target.startswith('http'):
        try:
            resp = requests.get(target, timeout=10)
            return jsonify({
                "status_code": resp.status_code,
                "content": resp.text[:1000]
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    # VULNERABILITY: Command Injection in ping
    try:
        cmd = f"ping -c 4 {target}"
        result = subprocess.check_output(cmd, shell=True, timeout=30).decode('utf-8')
        return jsonify({"output": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ============ INFORMATION DISCLOSURE ============

@app.route('/api/debug/info')
def debug_info():
    """Debug endpoint - information disclosure."""
    # VULNERABILITY: Information Disclosure - exposes internal details
    return jsonify({
        "environment": os.environ,
        "app_config": {
            "secret_key": app.secret_key,
            "database": DATABASE,
            "mongo_uri": MONGO_URI,
            "upload_folder": UPLOAD_FOLDER
        },
        "python_version": os.sys.version,
        "server_time": str(datetime.utcnow())
    })


@app.route('/api/error')
def trigger_error():
    """Trigger error - vulnerable to verbose error disclosure."""
    error_type = request.args.get('type', 'value')

    try:
        if error_type == 'zero':
            1 / 0
        elif error_type == 'key':
            {}['nonexistent_key']
        elif error_type == 'index':
            [][1]
        elif error_type == 'type':
            "string" + 123
        else:
            raise ValueError(f"Unknown error type: {error_type}")
    except Exception as e:
        # VULNERABILITY: Verbose error disclosure
        import traceback
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc(),
            "type": type(e).__name__,
            "args": e.args
        }), 500


# ============ FILE OPERATIONS ============

@app.route('/api/documents/upload', methods=['POST'])
def upload_document():
    """File upload - vulnerable to unrestricted file upload."""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    filename = file.filename

    # VULNERABILITY: Unrestricted File Upload - no extension/mimetype validation
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    return jsonify({
        "success": True,
        "filename": filename,
        "path": file_path,
        "size": os.path.getsize(file_path)
    })


@app.route('/api/documents/view/<path:filename>')
def view_document(filename):
    """View uploaded document - vulnerable to path traversal."""
    # VULNERABILITY: Path Traversal - no path sanitization
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    try:
        with open(file_path, 'r') as f:
            content = f.read()
        return jsonify({"filename": filename, "content": content})
    except Exception as e:
        return jsonify({"error": str(e)}), 404


@app.route('/api/documents/download/<path:filename>')
def download_document(filename):
    """Download document - vulnerable to path traversal."""
    # VULNERABILITY: Path Traversal
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    try:
        with open(file_path, 'rb') as f:
            content = f.read()

        response = make_response(content)
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 404


# ============ REDIRECT & URL ============

@app.route('/api/redirect')
def redirect_user():
    """Redirect endpoint - vulnerable to open redirect."""
    url = request.args.get('url', '/dashboard')

    # VULNERABILITY: Open Redirect - no validation of target URL
    return redirect(url, code=302)


@app.route('/api/proxy')
def proxy_request():
    """Proxy endpoint - vulnerable to SSRF."""
    target = request.args.get('target', '')

    if not target:
        return jsonify({"error": "No target specified"}), 400

    # VULNERABILITY: SSRF - can access internal resources
    try:
        resp = requests.get(target, timeout=30)
        return jsonify({
            "status": resp.status_code,
            "headers": dict(resp.headers),
            "content": resp.text[:5000]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ============ CACHE & CORS ============

@app.route('/api/public/rates')
def exchange_rates():
    """Public exchange rates - vulnerable to cache poisoning."""
    # VULNERABILITY: Web Cache Poisoning - uses unkeyed header in response
    x_country = request.headers.get('X-Country', 'US')

    rates = {
        "USD": 1.0,
        "EUR": 0.85,
        "GBP": 0.73,
        "JPY": 110.0
    }

    response = jsonify({
        "rates": rates,
        "country": x_country,
        "timestamp": str(datetime.utcnow())
    })

    # VULNERABILITY: Overly permissive CORS
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Cache-Control'] = 'public, max-age=3600'

    return response


@app.route('/api/user/profile', methods=['GET', 'PUT'])
def user_profile():
    """User profile - vulnerable to HTTP Parameter Pollution."""
    if request.method == 'GET':
        # VULNERABILITY: HTTP Parameter Pollution - uses first occurrence
        user_id = request.args.get('user_id', session.get('user_id'))

        # If request has ?user_id=123&user_id=admin, this might process both
        all_ids = request.args.getlist('user_id')
        if len(all_ids) > 1:
            # Some frameworks might merge these, causing unexpected behavior
            pass

        user = None
        if MONGO_AVAILABLE and db and ObjectId:
            try:
                user = db.users.find_one({"_id": ObjectId(user_id)})
            except:
                pass

        # Fallback to SQLite
        if not user:
            conn = get_sqlite_db()
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM users WHERE id = '{user_id}'")
            user = cursor.fetchone()
            conn.close()

            if user:
                return jsonify({
                    "id": user['id'],
                    "username": user['username'],
                    "email": user['email'],
                    "ssn": user['ssn'],  # VULNERABILITY: Sensitive data exposure
                    "credit_score": user['credit_score']
                })

        if user:
            return jsonify({
                "id": str(user['_id']) if hasattr(user, '_id') else user['id'],
                "username": user.get('username'),
                "email": user.get('email'),
                "ssn": user.get('ssn'),  # VULNERABILITY: Sensitive data exposure
                "credit_score": user.get('credit_score')
            })

        return jsonify({"error": "User not found"}), 404

    elif request.method == 'PUT':
        # VULNERABILITY: Mass Assignment on update
        update_data = request.get_json()
        user_id = session.get('user_id')

        if MONGO_AVAILABLE and db and ObjectId:
            try:
                db.users.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": update_data}  # Accepts any fields!
                )
            except:
                pass

        # Also update SQLite
        conn = get_sqlite_db()
        cursor = conn.cursor()
        for key, value in update_data.items():
            if key in ['username', 'email', 'ssn', 'credit_score', 'role']:
                cursor.execute(f"UPDATE users SET {key} = '{value}' WHERE id = '{user_id}'")
        conn.commit()
        conn.close()

        return jsonify({"success": True})


# ============ GRAPHQL (Simulated REST version) ============

@app.route('/api/graphql', methods=['POST'])
def graphql_endpoint():
    """GraphQL endpoint - vulnerable to injection."""
    data = request.get_json()
    query = data.get('query', '')

    # VULNERABILITY: GraphQL Injection - no query validation
    # Also allows introspection queries

    if 'query' in query.lower() or '__schema' in query or '__type' in query:
        # Simulate introspection response with sensitive data
        return jsonify({
            "data": {
                "__schema": {
                    "types": [
                        {"name": "User", "fields": ["id", "username", "password", "ssn", "credit_score"]},
                        {"name": "Account", "fields": ["id", "account_number", "balance", "user_id"]},
                        {"name": "Card", "fields": ["id", "card_number", "cvv", "expiry"]}
                    ]
                }
            }
        })

    # VULNERABILITY: No query depth limiting, no complexity analysis
    return jsonify({"data": {"result": "Query executed"}})


# ============ JWT MANIPULATION ============

@app.route('/api/token/decode', methods=['POST'])
def decode_token():
    """Decode JWT - vulnerable to algorithm confusion."""
    data = request.get_json()
    token = data.get('token', '')
    algorithm = data.get('algorithm', 'HS256')

    try:
        # VULNERABILITY: Accepts user-specified algorithm
        # Can use 'none' algorithm or RS256 confusion attack
        decoded = jwt.decode(token, app.secret_key, algorithms=[algorithm])
        return jsonify({"decoded": decoded})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/token/refresh')
def refresh_token():
    """Refresh JWT - no expiration check."""
    old_token = request.headers.get('Authorization', '').replace('Bearer ', '')

    try:
        # VULNERABILITY: No expiration verification
        decoded = jwt.decode(old_token, app.secret_key, options={"verify_exp": False})

        # Generate new token with extended expiry
        new_token = generate_jwt(decoded['user_id'], decoded['role'])

        return jsonify({"token": new_token})
    except Exception as e:
        return jsonify({"error": str(e)}), 401


if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(STATEMENT_FOLDER, exist_ok=True)
    init_db()
    app.run(host='0.0.0.0', port=5007, debug=True)
