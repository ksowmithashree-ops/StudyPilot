from flask import Blueprint, jsonify, request

from config import PLAN_HORIZON_DAYS, USER_ID
from services.planner import generate_plan, optimize_schedule

bp = Blueprint("planner", __name__)


@bp.post("/api/planner/generate")
def generate():
    data = request.get_json(silent=True) or {}
    days = int(data.get("days") or PLAN_HORIZON_DAYS)
    try:
        result = generate_plan(USER_ID, days=days)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 422
    return jsonify(result)


@bp.post("/api/planner/optimize")
def optimize():
    result = optimize_schedule(USER_ID)
    return jsonify(result)
