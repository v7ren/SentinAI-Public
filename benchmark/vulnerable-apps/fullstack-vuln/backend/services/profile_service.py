from backend.database import get_connection
from backend.models.profile import (
    get_profile_by_id,
    get_profiles_by_user_id,
    create_profile as db_create_profile,
    update_profile as db_update_profile,
)


def get_profile(profile_id):
    conn = get_connection()
    try:
        return get_profile_by_id(conn, profile_id)
    finally:
        conn.close()


def get_my_profiles(user_id):
    conn = get_connection()
    try:
        return get_profiles_by_user_id(conn, user_id)
    finally:
        conn.close()


def create_profile(user_id, display_name, bio, avatar_path=None):
    conn = get_connection()
    try:
        return db_create_profile(conn, user_id, display_name, bio, avatar_path)
    finally:
        conn.close()


def update_profile(profile_id, display_name, bio, avatar_path=None):
    conn = get_connection()
    try:
        db_update_profile(conn, profile_id, display_name, bio, avatar_path)
    finally:
        conn.close()
