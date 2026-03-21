from backend.config import ADMIN_API_KEY
from backend.database import get_connection
from backend.models.user import list_users


def get_all_users(api_key):
    if api_key != ADMIN_API_KEY:
        return None
    conn = get_connection()
    try:
        return list_users(conn)
    finally:
        conn.close()
