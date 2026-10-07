from flask import Blueprint, jsonify

from config import USER_ID
from models import get_user
from seed import seed_demo

bp = Blueprint("demo", __name__)


@bp.post("/api/demo/reset")
def reset_demo():
    try:
        # If demo data already exists, keep it.
        # This prevents the reset button from failing in production.
        user = get_user(USER_ID)

        if user:
            return jsonify({
                "ok": True,
                "message": "Demo data is already loaded.",
                "user_id": USER_ID
            })

        # If no demo user exists, create the demo data.
        result = seed_demo()

        return jsonify(result)

    except Exception as e:
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500