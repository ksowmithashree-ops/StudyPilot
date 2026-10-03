from flask import Blueprint, jsonify

from seed import seed_demo

bp = Blueprint("demo", __name__)


@bp.post("/api/demo/reset")
def reset_demo():
    result = seed_demo()
    return jsonify(result)
