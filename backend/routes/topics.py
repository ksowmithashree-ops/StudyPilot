from flask import Blueprint, jsonify, request

from config import USER_ID
from models import (
    create_topic,
    delete_topic,
    get_subject,
    get_topic,
    list_topics,
    update_topic,
)

bp = Blueprint("topics", __name__)


@bp.get("/api/subjects/<int:subject_id>/topics")
def get_topics(subject_id):
    if not get_subject(subject_id, USER_ID):
        return jsonify({"error": "Subject not found"}), 404
    return jsonify(list_topics(subject_id=subject_id))


@bp.get("/api/topics")
def get_all_topics():
    return jsonify(list_topics(user_id=USER_ID))


@bp.post("/api/subjects/<int:subject_id>/topics")
def post_topic(subject_id):
    if not get_subject(subject_id, USER_ID):
        return jsonify({"error": "Subject not found"}), 404
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Name is required"}), 400
    topic = create_topic(
        subject_id,
        name,
        int(data.get("difficulty") or 3),
        int(data.get("progress_pct") or 0),
        int(data.get("estimated_minutes") or 120),
    )
    return jsonify(topic), 201


@bp.patch("/api/topics/<int:topic_id>")
def patch_topic(topic_id):
    topic = get_topic(topic_id)
    if not topic or topic["user_id"] != USER_ID:
        return jsonify({"error": "Topic not found"}), 404
    data = request.get_json(silent=True) or {}
    return jsonify(update_topic(topic_id, data))


@bp.delete("/api/topics/<int:topic_id>")
def remove_topic(topic_id):
    topic = get_topic(topic_id)
    if not topic or topic["user_id"] != USER_ID:
        return jsonify({"error": "Topic not found"}), 404
    delete_topic(topic_id)
    return jsonify({"ok": True})
