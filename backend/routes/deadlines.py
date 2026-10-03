from flask import Blueprint, jsonify, request

from config import USER_ID
from models import (
    create_deadline,
    delete_deadline,
    get_deadline,
    get_subject,
    list_deadlines,
    update_deadline,
)

bp = Blueprint("deadlines", __name__)

ALLOWED_TYPES = {"exam", "assignment", "project", "quiz"}


@bp.get("/api/deadlines")
def get_deadlines():
    return jsonify(list_deadlines(USER_ID))


@bp.post("/api/deadlines")
def post_deadline():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    due_date = data.get("due_date")
    subject_id = data.get("subject_id")
    type_ = (data.get("type") or "exam").lower()
    if not title or not due_date or not subject_id:
        return jsonify({"error": "title, due_date, and subject_id are required"}), 400
    if type_ not in ALLOWED_TYPES:
        return jsonify({"error": "type must be exam, assignment, project, or quiz"}), 400
    if not get_subject(int(subject_id), USER_ID):
        return jsonify({"error": "Subject not found"}), 404
    deadline = create_deadline(
        USER_ID,
        int(subject_id),
        title,
        due_date[:10],
        type_,
        data.get("topic_id"),
        int(data.get("priority") or 3),
    )
    return jsonify(deadline), 201


@bp.patch("/api/deadlines/<int:deadline_id>")
def patch_deadline(deadline_id):
    if not get_deadline(deadline_id):
        return jsonify({"error": "Deadline not found"}), 404
    data = request.get_json(silent=True) or {}
    return jsonify(update_deadline(deadline_id, data))


@bp.delete("/api/deadlines/<int:deadline_id>")
def remove_deadline(deadline_id):
    if not get_deadline(deadline_id):
        return jsonify({"error": "Deadline not found"}), 404
    delete_deadline(deadline_id)
    return jsonify({"ok": True})
