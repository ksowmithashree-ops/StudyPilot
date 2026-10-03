from datetime import date, timedelta

from models import list_sessions
from services.planner import generate_plan
from services.rescheduler import reschedule_missed


def test_miss_moves_to_future_day(demo_db):
    today = date.today()
    generate_plan(1, today=today, days=7)
    today_sessions = [
        s
        for s in list_sessions(1, today.isoformat(), today.isoformat(), statuses=["planned"])
        if s["topic_name"] == "Normalization"
    ]
    assert today_sessions
    original = today_sessions[0]
    result = reschedule_missed(original["id"], 1, today=today)
    assert result["missed"]["status"] == "missed"
    moved = result["rescheduled"]
    assert moved is not None
    assert moved["date"] > today.isoformat()
    assert moved["status"] == "planned"
    assert moved["topic_name"] == "Normalization"
