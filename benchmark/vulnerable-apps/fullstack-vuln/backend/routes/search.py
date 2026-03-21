from flask import Blueprint, request, jsonify
from backend.services.search_service import search

search_bp = Blueprint("search", __name__, url_prefix="/api/search")


@search_bp.route("", methods=["GET"])
def do_search():
    q = request.args.get("q", "")
    results = search(q)
    return jsonify(results)
