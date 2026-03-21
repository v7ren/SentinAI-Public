from flask import Blueprint, request, jsonify, session
from backend.middleware.auth import require_auth
from backend.services.profile_service import get_profile, get_my_profiles, create_profile, update_profile

profile_bp = Blueprint("profile", __name__, url_prefix="/api/profile")


@profile_bp.route("/<profile_id>", methods=["GET"])
def get_one(profile_id):
    result = get_profile(profile_id)
    if not result:
        return jsonify({"error": "Profile not found"}), 404
    return jsonify(result)


@profile_bp.route("", methods=["GET"])
@require_auth
def list_mine():
    uid = session["user_id"]
    profiles = get_my_profiles(uid)
    return jsonify(profiles)


@profile_bp.route("", methods=["POST"])
@require_auth
def create():
    data = request.get_json() or {}
    display_name = data.get("display_name", "")
    bio = data.get("bio", "")
    uid = session["user_id"]
    pid = create_profile(uid, display_name, bio)
    return jsonify({"id": pid})


@profile_bp.route("/<profile_id>", methods=["PUT"])
@require_auth
def update(profile_id):
    data = request.get_json() or {}
    display_name = data.get("display_name", "")
    bio = data.get("bio", "")
    update_profile(profile_id, display_name, bio)
    return jsonify({"ok": True})
