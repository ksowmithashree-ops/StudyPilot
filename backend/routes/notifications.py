from flask import Blueprint, jsonify, request

from config import USER_ID
from models import list_notifications, mark_notifications_read

bp = Blueprint("notifications", __name__)


@bp.get("/api/notifications")
def get_notifications():
    unread = request.args.get("unread") == "1"
    items = list_notifications(USER_ID, unread_only=unread)
    return jsonify({"items": items, "unread": sum(1 for n in items if not n["read"])})


@bp.patch("/api/notifications")
def patch_notifications():
    data = request.get_json(silent=True) or {}
    mark_notifications_read(USER_ID, data.get("ids"))
    items = list_notifications(USER_ID)
    return jsonify({"items": items, "unread": sum(1 for n in items if not n["read"])})
