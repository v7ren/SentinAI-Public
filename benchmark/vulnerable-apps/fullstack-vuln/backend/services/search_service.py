from backend.database import get_connection
from backend.models.profile import search_profiles


def search(query):
    conn = get_connection()
    try:
        return search_profiles(conn, query)
    finally:
        conn.close()
