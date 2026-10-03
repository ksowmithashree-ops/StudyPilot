from datetime import datetime

from config import USER_ID
from models import create_notification


def notify(type_, title, body, related_session_id=None, user_id=USER_ID):
    created_at = datetime.now().replace(microsecond=0).isoformat()
    return create_notification(user_id, type_, title, body, related_session_id, created_at)
