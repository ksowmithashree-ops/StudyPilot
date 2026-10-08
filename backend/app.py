import sys
from pathlib import Path

# Make sure Python can find backend modules on Vercel
sys.path.insert(0, str(Path(__file__).resolve().parent))

from flask import Flask, jsonify
from flask_cors import CORS

from database import init_db
from models import get_user
from seed import seed_demo

from routes.subjects import bp as subjects_bp
from routes.topics import bp as topics_bp
from routes.tasks import bp as tasks_bp
from routes.deadlines import bp as deadlines_bp
from routes.planner import bp as planner_bp
from routes.progress import bp as progress_bp
from routes.notifications import bp as notifications_bp
from routes.chat import bp as chat_bp
from routes.demo import bp as demo_bp

from config import USER_ID


def create_app():
    app = Flask(__name__)

    # Allow frontend to communicate with backend
    CORS(
        app,
        resources={
            r"/*": {
                "origins": [
                    "https://study-pilot-4hju.vercel.app",
                    "https://studypilot-frontend-one.vercel.app",
                    "https://studypilot-frontend-git-main-ksowmithashree-ops.vercel.app",
                    "https://studypilot-frontend-fh1owfdgt-ksowmithashree-ops.vercel.app",
                    "http://localhost:5173",
                ]
            }
        },
        methods=[
            "GET",
            "POST",
            "PATCH",
            "DELETE",
            "OPTIONS",
        ],
        allow_headers=[
            "Content-Type",
            "Authorization",
        ],
    )

    # Initialize database
    init_db()

    # Create demo data if user does not exist
    if not get_user(USER_ID):
        seed_demo()

    # Register routes
    for blueprint in (
        subjects_bp,
        topics_bp,
        tasks_bp,
        deadlines_bp,
        planner_bp,
        progress_bp,
        notifications_bp,
        chat_bp,
        demo_bp,
    ):
        app.register_blueprint(blueprint)

    @app.get("/api/health")
    def health():
        return jsonify({"ok": True})

    @app.errorhandler(404)
    def not_found(_e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(_e):
        return jsonify({"error": "Server error"}), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )