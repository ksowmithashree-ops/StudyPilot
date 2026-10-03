from datetime import date, timedelta

from models import get_user, list_topics
from services.planner import generate_plan, pack_horizon, scored_topics, weekday_budget
from services.readiness import priority_score, remaining_minutes


def test_normalization_outranks_sql(demo_db):
    today = date.today()
    scored = scored_topics(1, today)
    names = [item["topic"]["name"] for item in scored]
    assert names.index("Normalization") < names.index("SQL")
    assert names.index("Normalization") < names.index("ER Model")


def test_plan_never_exceeds_budget(demo_db):
    result = generate_plan(1, today=date.today(), days=7)
    user = get_user(1)
    by_day = {}
    for session in result["sessions"]:
        by_day.setdefault(session["date"], 0)
        by_day[session["date"]] += session["planned_minutes"]
    for day_str, minutes in by_day.items():
        budget = weekday_budget(user, date.fromisoformat(day_str))
        assert minutes <= budget


def test_normalization_scheduled_early(demo_db):
    result = generate_plan(1, today=date.today(), days=7)
    today = date.today().isoformat()
    today_topics = [s["topic_name"] for s in result["sessions"] if s["date"] == today]
    assert "Normalization" in today_topics
    assert today_topics[0] == "Normalization"


def test_priority_formula_gap_and_deadline():
    today = date.today()
    weak = {"progress_pct": 18, "difficulty": 5, "subject_importance": 5, "estimated_minutes": 180}
    strong = {"progress_pct": 70, "difficulty": 2, "subject_importance": 5, "estimated_minutes": 90}
    deadline = {"due_date": (today + timedelta(days=5)).isoformat(), "priority": 5}
    assert priority_score(weak, deadline, today) > priority_score(strong, deadline, today)
    assert remaining_minutes(weak) > remaining_minutes(strong)
