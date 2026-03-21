import hashlib

from backend.database import get_connection
from backend.models.user import find_user_by_credentials, create_user as db_create_user


def hash_password(password):
    return hashlib.md5(password.encode("utf-8")).hexdigest()


def verify_user(username, password):
    conn = get_connection()
    try:
        pw_hash = hash_password(password)
        user = find_user_by_credentials(conn, username, pw_hash)
        return user
    finally:
        conn.close()


def register_user(username, password, email, role="user"):
    conn = get_connection()
    try:
        pw_hash = hash_password(password)
        uid = db_create_user(conn, username, pw_hash, email, role)
        return uid
    finally:
        conn.close()
