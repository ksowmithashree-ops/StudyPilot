from datetime import date

from flask import Blueprint, jsonify, request

from config import USER_ID
from models import (
    bump_progress_log,
    get_session,
    list_sessions,
    update_session,
    update_topic,
    add_task_event,
    get_topic,
)
from services.rescheduler import reschedule_missed

bp = Blueprint("tasks", __name__)


@bp.get("/api/sessions")
def get_sessions():
    from_date = request.args.get("from")
    to_date = request.args.get("to")
    return jsonify(list_sessions(USER_ID, from_date, to_date))


@bp.post("/api/sessions/<int:session_id>/complete")
def complete_session(session_id):
    session = get_session(session_id)
    if not session or session["user_id"] != USER_ID:
        return jsonify({"error": "Session not found"}), 404
    if session["status"] != "planned":
        return jsonify({"error": "Only planned sessions can be completed"}), 400
    updated = update_session(session_id, {"status": "completed"})
    topic = get_topic(session["topic_id"])
    bump = min(12, max(6, session["planned_minutes"] // 15))
    new_progress = min(100, (topic["progress_pct"] or 0) + bump)
    update_topic(
        topic["id"],
        {
            "progress_pct": new_progress,
            "revision_count": (topic["revision_count"] or 0) + 1,
            "last_studied_at": date.today().isoformat(),
        },
    )
    bump_progress_log(USER_ID, session["date"], session["planned_minutes"], 1)
    add_task_event(session_id, "completed", session["date"], session["date"], f"{date.today().isoformat()}T12:00:00")
    session = get_session(session_id)
    session["topic_progress"] = new_progress
    return jsonify(session)


@bp.post("/api/sessions/<int:session_id>/miss")
def miss_session(session_id):
    try:
        result = reschedule_missed(session_id, USER_ID)
    except ValueError as exc:
        status = 404 if "not found" in str(exc).lower() else 400
        return jsonify({"error": str(exc)}), status
    return jsonify(result)
