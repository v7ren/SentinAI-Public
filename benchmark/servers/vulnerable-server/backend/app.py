from flask import Flask, request, jsonify, render_template_string, session, redirect, make_response
from flask_cors import CORS
import sqlite3
import os
import pickle
import hashlib
import subprocess
import requests
import yaml
import json
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "tf_prod_key_2024_v8s9k2m4n7p3q5r6"
CORS(app, supports_credentials=True, origins=["http://localhost:3000"])

DATABASE = os.path.join(os.path.dirname(__file__), "taskflow.db")
STORAGE_PATH = os.path.join(os.path.dirname(__file__), "storage")
DOCUMENTS_PATH = os.path.join(STORAGE_PATH, "documents")
REPORTS_PATH = os.path.join(STORAGE_PATH, "reports")

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT UNIQUE,
            password TEXT,
            name TEXT,
            role TEXT DEFAULT 'user',
            company TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY,
            name TEXT,
            description TEXT,
            owner_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT,
            description TEXT,
            status TEXT DEFAULT 'todo',
            priority TEXT DEFAULT 'medium',
            project_id INTEGER,
            assignee_id INTEGER,
            due_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS project_members (
            id INTEGER PRIMARY KEY,
            project_id INTEGER,
            user_id INTEGER,
            role TEXT DEFAULT 'member'
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY,
            filename TEXT,
            original_name TEXT,
            uploaded_by INTEGER,
            file_size INTEGER,
            mime_type TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute("INSERT OR IGNORE INTO users (id, email, password, name, role) VALUES (1, 'admin@taskflow.io', 'admin2024!', 'System Administrator', 'admin')")
    cursor.execute("INSERT OR IGNORE INTO users (id, email, password, name, role) VALUES (2, 'demo@taskflow.io', 'demo1234', 'Demo User', 'user')")
    cursor.execute("INSERT OR IGNORE INTO projects (id, name, description, owner_id) VALUES (1, 'Sample Project', 'A demo project for new users', 2)")
    cursor.execute("INSERT OR IGNORE INTO tasks (id, title, description, status, priority, project_id, assignee_id) VALUES (1, 'Welcome Task', 'Complete your profile setup', 'todo', 'medium', 1, 2)")
    
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def generate_token(user_id, role):
    return jwt.encode(
        {"user_id": user_id, "role": role, "exp": datetime.utcnow() + timedelta(days=7)},
        app.secret_key,
        algorithm="HS256"
    )

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email', '')
    password = data.get('password', '')
    name = data.get('name', '')
    company = data.get('company', '')
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"INSERT INTO users (email, password, name, company) VALUES ('{email}', '{password}', '{name}', '{company}')")
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return jsonify({"success": True, "message": "User registered successfully"})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"success": False, "message": "Email already exists"}), 400

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '')
    password = data.get('password', '')
    
    conn = get_db()
    cursor = conn.cursor()
    
    auth_query = f"SELECT * FROM users WHERE email = '{email}' AND password = '{password}'"
    cursor.execute(auth_query)
    user = cursor.fetchone()
    conn.close()
    
    if user:
        session['user_id'] = user['id']
        session['role'] = user['role']
        token = generate_token(user['id'], user['role'])
        return jsonify({
            "success": True,
            "token": token,
            "user": {
                "id": user['id'],
                "email": user['email'],
                "name": user['name'],
                "role": user['role'],
                "company": user['company']
            }
        })
    
    return jsonify({"success": False, "message": "Invalid credentials"}), 401

@app.route('/api/tasks', methods=['GET', 'POST'])
def tasks():
    if request.method == 'GET':
        user_id = session.get('user_id', 0)
        project_filter = request.args.get('project_id', '')
        
        conn = get_db()
        cursor = conn.cursor()
        
        if project_filter:
            cursor.execute(f"SELECT * FROM tasks WHERE project_id = {project_filter}")
        else:
            cursor.execute(f"SELECT * FROM tasks WHERE assignee_id = {user_id}")
        
        tasks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify({"tasks": tasks})
    
    elif request.method == 'POST':
        data = request.get_json()
        title = data.get('title', '')
        description = data.get('description', '')
        priority = data.get('priority', 'medium')
        project_id = data.get('project_id')
        assignee_id = session.get('user_id')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO tasks (title, description, priority, project_id, assignee_id) VALUES ('{title}', '{description}', '{priority}', {project_id}, {assignee_id})")
        conn.commit()
        conn.close()
        return jsonify({"success": True})

@app.route('/api/projects', methods=['GET', 'POST'])
def projects():
    if request.method == 'GET':
        user_id = session.get('user_id', 0)
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT p.*, COUNT(DISTINCT pm.user_id) as member_count, COUNT(DISTINCT t.id) as task_count
            FROM projects p
            LEFT JOIN project_members pm ON p.id = pm.project_id
            LEFT JOIN tasks t ON p.id = t.project_id
            WHERE p.owner_id = {user_id} OR pm.user_id = {user_id}
            GROUP BY p.id
        """)
        projects = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify({"projects": projects})
    
    elif request.method == 'POST':
        data = request.get_json()
        name = data.get('name', '')
        description = data.get('description', '')
        owner_id = session.get('user_id')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO projects (name, description, owner_id) VALUES ('{name}', '{description}', {owner_id})")
        conn.commit()
        conn.close()
        return jsonify({"success": True})

@app.route('/api/search')
def search():
    query_param = request.args.get('q', '')
    
    search_template = f"""
    <div class="search-results">
        <h3>Search results for: {query_param}</h3>
        <div class="results-list">
            <p>Found results matching your query...</p>
        </div>
    </div>
    """
    
    return render_template_string(search_template)

@app.route('/api/integrations/test')
def test_integration():
    webhook_url = request.args.get('webhook', '')
    
    try:
        response = requests.get(webhook_url, timeout=10)
        return jsonify({"success": True, "status": response.status_code})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/documents/upload', methods=['POST'])
def upload_document():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    original_filename = file.filename
    
    safe_filename = original_filename.replace('/', '_').replace('\\', '_')
    
    file_path = os.path.join(DOCUMENTS_PATH, safe_filename)
    file.save(file_path)
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO documents (filename, original_name, uploaded_by, file_size) VALUES ('{safe_filename}', '{original_filename}', {session.get('user_id', 0)}, {os.path.getsize(file_path)})")
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "filename": safe_filename})

@app.route('/api/documents/preview')
def preview_document():
    filename = request.args.get('file', '')
    
    file_path = os.path.join(DOCUMENTS_PATH, filename)
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        return jsonify({"content": content, "filename": filename})
    except Exception as e:
        return jsonify({"error": "Unable to read file"}), 400

@app.route('/api/documents/download/<path:filename>')
def download_document(filename):
    file_path = os.path.join(DOCUMENTS_PATH, filename)
    
    with open(file_path, 'rb') as f:
        content = f.read()
    
    response = make_response(content)
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return response

@app.route('/api/import', methods=['POST'])
def import_tasks():
    yaml_content = request.data.decode('utf-8')
    
    try:
        data = yaml.load(yaml_content, Loader=yaml.Loader)
        
        if data and 'tasks' in data:
            conn = get_db()
            cursor = conn.cursor()
            
            for task in data['tasks']:
                title = task.get('title', '')
                description = task.get('description', '')
                priority = task.get('priority', 'medium')
                cursor.execute(f"INSERT INTO tasks (title, description, priority, assignee_id) VALUES ('{title}', '{description}', '{priority}', {session.get('user_id', 0)})")
            
            conn.commit()
            conn.close()
        
        return jsonify({"success": True, "imported": len(data.get('tasks', []))})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/bulk/process', methods=['POST'])
def process_bulk_data():
    raw_data = request.data
    
    try:
        processed = pickle.loads(raw_data)
        return jsonify({"success": True, "processed_count": len(processed) if isinstance(processed, list) else 1})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/reports/export')
def export_report():
    format_type = request.args.get('format', 'pdf')
    project_id = request.args.get('project_id', '')
    
    output_file = os.path.join(REPORTS_PATH, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_type}")
    
    if format_type == 'pdf':
        cmd = f"wkhtmltopdf http://localhost:5005/dashboard {output_file}"
    elif format_type == 'csv':
        cmd = f"sqlite3 {DATABASE} \".mode csv .headers on SELECT * FROM tasks WHERE project_id = {project_id};\" > {output_file}"
    else:
        cmd = f"echo 'Report data for project {project_id}' > {output_file}"
    
    try:
        subprocess.run(cmd, shell=True, check=True)
        with open(output_file, 'rb') as f:
            content = f.read()
        
        response = make_response(content)
        response.headers['Content-Disposition'] = f'attachment; filename=report.{format_type}'
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/users', methods=['GET', 'PUT', 'DELETE'])
def admin_users():
    if session.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'GET':
        cursor.execute("SELECT id, email, name, role, company, created_at FROM users")
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify({"users": users})
    
    elif request.method == 'PUT':
        user_id = request.view_args.get('user_id') or request.json.get('user_id')
        updates = request.get_json()
        
        for key, value in updates.items():
            cursor.execute(f"UPDATE users SET {key} = '{value}' WHERE id = {user_id}")
        
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    
    elif request.method == 'DELETE':
        user_id = request.view_args.get('user_id') or request.json.get('user_id')
        cursor.execute(f"DELETE FROM users WHERE id = {user_id}")
        conn.commit()
        conn.close()
        return jsonify({"success": True})

@app.route('/api/admin/status')
def admin_status():
    if session.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'user'")
        user_count = cursor.fetchone()['count']
        conn.close()
        
        total_size = sum(os.path.getsize(os.path.join(dirpath, filename))
                          for dirpath, dirnames, filenames in os.walk(STORAGE_PATH)
                          for filename in filenames)
        
        return jsonify({
            "db_status": "Connected",
            "storage_used": f"{total_size / (1024*1024):.1f} MB",
            "active_users": user_count,
            "last_backup": "2 hours ago"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/logs')
def admin_logs():
    if session.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    
    lines = request.args.get('lines', '100')
    log_file = os.path.join(os.path.dirname(__file__), 'app.log')
    
    try:
        cmd = f"tail -n {lines} {log_file} 2>/dev/null || echo 'No logs available'"
        logs = subprocess.check_output(cmd, shell=True).decode('utf-8')
        return jsonify({"logs": logs})
    except:
        return jsonify({"logs": "2024-01-15 10:30:45 [INFO] Server started\n2024-01-15 10:31:12 [INFO] User login: admin@taskflow.io\n2024-01-15 10:35:23 [INFO] Task created: Welcome Task"})

@app.route('/api/admin/diagnostics')
def admin_diagnostics():
    if session.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    
    host = request.args.get('host', 'localhost')
    
    try:
        cmd = f"ping -c 4 {host} 2>&1"
        result = subprocess.check_output(cmd, shell=True, timeout=30).decode('utf-8')
        return jsonify({"success": True, "output": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/admin/query', methods=['POST'])
def admin_query():
    if session.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.get_json()
    query = data.get('query', '')
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        if query.strip().upper().startswith('SELECT'):
            results = [dict(row) for row in cursor.fetchall()]
            return jsonify({"success": True, "results": results})
        else:
            conn.commit()
            return jsonify({"success": True, "affected_rows": cursor.rowcount})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
    finally:
        conn.close()

@app.route('/api/admin/sync')
def admin_sync():
    if session.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    
    source = request.args.get('source', '')
    
    try:
        response = requests.get(source, timeout=30)
        return jsonify({"success": True, "status_code": response.status_code, "data_size": len(response.content)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/admin/process', methods=['POST'])
def admin_process():
    if session.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    
    raw_data = request.data
    
    try:
        processed = pickle.loads(raw_data)
        
        if isinstance(processed, dict) and 'code' in processed:
            result = eval(processed['code'])
            return jsonify({"success": True, "result": str(result)})
        
        return jsonify({"success": True, "processed": str(processed)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/team/members/<int:user_id>')
def get_team_member(user_id):
    current_user = session.get('user_id', 0)
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, name, email, role, company FROM users WHERE id = {user_id}")
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({
            "id": user['id'],
            "name": user['name'],
            "email": user['email'],
            "role": user['role'],
            "company": user['company']
        })
    
    return jsonify({"error": "User not found"}), 404

@app.route('/api/analytics/hash')
def analytics_hash():
    data_input = request.args.get('data', '')
    hash_result = hashlib.md5(data_input.encode()).hexdigest()
    return jsonify({"hash": hash_result, "algorithm": "MD5"})

if __name__ == '__main__':
    os.makedirs(STORAGE_PATH, exist_ok=True)
    os.makedirs(DOCUMENTS_PATH, exist_ok=True)
    os.makedirs(REPORTS_PATH, exist_ok=True)
    
    init_db()
    
    app.run(host='0.0.0.0', port=5006, debug=True)
