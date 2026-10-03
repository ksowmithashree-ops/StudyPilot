from flask import Blueprint, jsonify, request

from config import USER_ID
from models import create_subject, delete_subject, get_subject, list_subjects, update_subject

bp = Blueprint("subjects", __name__)


@bp.get("/api/subjects")
def get_subjects():
    return jsonify(list_subjects(USER_ID))


@bp.post("/api/subjects")
def post_subject():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Name is required"}), 400
    importance = int(data.get("importance") or 3)
    color = data.get("color") or "#6366f1"
    return jsonify(create_subject(USER_ID, name, color, importance)), 201


@bp.patch("/api/subjects/<int:subject_id>")
def patch_subject(subject_id):
    if not get_subject(subject_id, USER_ID):
        return jsonify({"error": "Subject not found"}), 404
    data = request.get_json(silent=True) or {}
    return jsonify(update_subject(subject_id, data))


@bp.delete("/api/subjects/<int:subject_id>")
def remove_subject(subject_id):
    if not get_subject(subject_id, USER_ID):
        return jsonify({"error": "Subject not found"}), 404
    delete_subject(subject_id)
    return jsonify({"ok": True})
