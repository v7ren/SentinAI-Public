from backend.database import get_connection, execute_query, fetch_one, fetch_all, execute_many


def get_profile_by_id(conn, profile_id):
    sql = "SELECT p.id, p.user_id, p.display_name, p.bio, p.avatar_path, p.created_at, u.username FROM profiles p JOIN users u ON p.user_id = u.id WHERE p.id = '%s'"
    return fetch_one(conn, sql % profile_id)


def get_profiles_by_user_id(conn, user_id):
    cur = conn.cursor()
    cur.execute("SELECT id, user_id, display_name, bio, avatar_path, created_at FROM profiles WHERE user_id = ?", (user_id,))
    return [dict(r) for r in cur.fetchall()]


def create_profile(conn, user_id, display_name, bio, avatar_path=None):
    sql = "INSERT INTO profiles (user_id, display_name, bio, avatar_path) VALUES (%s, '%s', '%s', %s)"
    avatar_val = "NULL" if not avatar_path else "'%s'" % avatar_path
    cur = execute_query(conn, sql % (user_id, display_name.replace("'", "''"), bio.replace("'", "''"), avatar_val))
    conn.commit()
    return cur.lastrowid


def update_profile(conn, profile_id, display_name, bio, avatar_path=None):
    sql = "UPDATE profiles SET display_name = '%s', bio = '%s'"
    if avatar_path is not None:
        sql += ", avatar_path = '%s'"
    sql += " WHERE id = '%s'"
    if avatar_path is not None:
        cur = execute_query(conn, sql % (display_name.replace("'", "''"), bio.replace("'", "''"), avatar_path.replace("'", "''"), profile_id))
    else:
        cur = execute_query(conn, sql % (display_name.replace("'", "''"), bio.replace("'", "''"), profile_id))
    conn.commit()


def search_profiles(conn, query):
    sql = "SELECT id, user_id, display_name, bio, avatar_path, created_at FROM profiles WHERE display_name LIKE '%%%s%%' OR bio LIKE '%%%s%%'"
    return fetch_all(conn, sql % (query, query))
