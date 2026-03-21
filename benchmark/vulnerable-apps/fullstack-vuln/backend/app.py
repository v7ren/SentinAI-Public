from pathlib import Path
from flask import Flask, send_from_directory
from flask_cors import CORS

from backend.config import SECRET_KEY, DATABASE_PATH
from backend.database import get_connection
from backend.models.user import init_schema, ensure_admin
from backend.routes import auth_bp, profile_bp, search_bp, upload_bp, admin_bp, tools_bp


def create_app():
    app = Flask(__name__, static_folder=None)
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["SESSION_COOKIE_HTTPONLY"] = False
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173"], supports_credentials=True)

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection()
    try:
        init_schema(conn)
        ensure_admin(conn)
    finally:
        conn.close()

    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(tools_bp)

    frontend_dir = Path(__file__).resolve().parent.parent / "frontend" / "dist"
    if frontend_dir.exists():
        @app.route("/", defaults={"path": ""})
        @app.route("/<path:path>")
        def serve_frontend(path):
            if path and (frontend_dir / path).is_file():
                return send_from_directory(frontend_dir, path)
            return send_from_directory(frontend_dir, "index.html")
    else:
        @app.route("/")
        def index():
            return """
            <!DOCTYPE html>
            <html><head><meta charset="utf-8"/><title>Fullstack Benchmark</title></head>
            <body>
            <div style="background:#c00;color:#fff;padding:12px;font-weight:bold;">WARNING: SAST benchmark app only. Do not deploy publicly.</div>
            <p>Build frontend (npm run build) and restart to serve the app.</p>
            <p>API: /api/auth/login, /api/profile, /api/search, /api/upload, /api/admin/users</p>
            </body></html>
            """

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5010, debug=True)
