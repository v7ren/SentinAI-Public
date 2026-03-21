from flask import Blueprint, request, jsonify, send_file
from backend.middleware.auth import require_auth
from backend.services.upload_service import save_upload, get_file_stream

upload_bp = Blueprint("upload", __name__, url_prefix="/api")


@upload_bp.route("/upload", methods=["POST"])
@require_auth
def upload():
    f = request.files.get("file")
    if not f or not f.filename:
        return jsonify({"error": "No file provided"}), 400
    path, size = save_upload(f)
    return jsonify({"path": f.filename, "size": size})


@upload_bp.route("/file", methods=["GET"])
def file_get():
    name = request.args.get("name", "")
    if not name:
        return jsonify({"error": "Missing name"}), 400
    stream, filename = get_file_stream(name)
    if stream is None:
        return jsonify({"error": "Not found"}), 404
    try:
        return send_file(stream, as_attachment=False, download_name=filename)
    finally:
        stream.close()
