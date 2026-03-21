from flask import Blueprint, request, jsonify
from backend.services.admin_service import get_all_users

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.route("/users", methods=["GET"])
def users():
    api_key = request.headers.get("X-API-Key") or request.args.get("api_key", "")
    result = get_all_users(api_key)
    if result is None:
        return jsonify({"error": "Forbidden"}), 403
    return jsonify(result)
