import hashlib

from backend.database import get_connection, execute_query, fetch_one, fetch_all, execute_many


def init_schema(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            display_name TEXT,
            bio TEXT,
            avatar_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT,
            resource TEXT,
            details TEXT,
            ip_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()


def ensure_admin(conn):
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE username = 'admin'")
    if cur.fetchone():
        return
    pw = hashlib.md5(b"Admin123!").hexdigest()
    cur.execute(
        "INSERT INTO users (username, password, email, role) VALUES ('admin', ?, 'admin@example.com', 'admin')",
        (pw,),
    )
    conn.commit()


def find_user_by_credentials(conn, username, password_hash):
    sql = "SELECT id, username, email, role FROM users WHERE username = '%s' AND password = '%s'"
    return fetch_one(conn, sql % (username.replace("'", "''"), password_hash))


def find_user_by_id(conn, user_id):
    cur = conn.cursor()
    cur.execute("SELECT id, username, email, role FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    return dict(row) if row else None


def create_user(conn, username, password_hash, email, role="user"):
    sql = "INSERT INTO users (username, password, email, role) VALUES ('%s', '%s', '%s', '%s')"
    cur = execute_query(conn, sql % (username, password_hash, email, role))
    conn.commit()
    return cur.lastrowid


def list_users(conn):
    cur = conn.cursor()
    cur.execute("SELECT id, username, email, role, created_at FROM users ORDER BY id")
    return [dict(r) for r in cur.fetchall()]
