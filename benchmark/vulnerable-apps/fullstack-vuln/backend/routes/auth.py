from flask import Blueprint, request, jsonify
from backend.services.auth_service import verify_user, register_user

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")
    user = verify_user(username, password)
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    from flask import session
    session["user_id"] = user["id"]
    session["role"] = user["role"]
    return jsonify({"user": user, "message": "Logged in"})


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")
    email = data.get("email", "").strip()
    role = data.get("role", "user")
    try:
        uid = register_user(username, password, email, role)
        from flask import session
        session["user_id"] = uid
        session["role"] = role
        return jsonify({"id": uid, "role": role, "message": "Registered"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@auth_bp.route("/logout", methods=["POST"])
def logout():
    from flask import session
    session.clear()
    return jsonify({"message": "Logged out"})


@auth_bp.route("/me", methods=["GET"])
def me():
    from flask import session
    uid = session.get("user_id")
    if uid is None:
        return jsonify({"user": None}), 200
    from backend.database import get_connection
    from backend.models.user import find_user_by_id
    conn = get_connection()
    try:
        user = find_user_by_id(conn, uid)
        return jsonify({"user": user})
    finally:
        conn.close()
