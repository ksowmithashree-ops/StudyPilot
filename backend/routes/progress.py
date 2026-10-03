from datetime import date, timedelta

from flask import Blueprint, jsonify, request

from config import USER_ID
from models import (
    get_user,
    list_deadlines,
    list_progress_logs,
    list_sessions,
    list_subjects,
    list_topics,
    update_user,
)
from services.gemini import gemini_available
from services.planner import scored_topics, weekday_budget
from services.readiness import readiness_for_deadlines

bp = Blueprint("progress", __name__)


@bp.get("/api/dashboard")
def dashboard():
    today = date.today().isoformat()
    user = get_user(USER_ID)
    sessions = list_sessions(USER_ID, from_date=today, to_date=today)
    planned = [s for s in sessions if s["status"] == "planned"]
    completed = [s for s in sessions if s["status"] == "completed"]
    missed = [s for s in sessions if s["status"] == "missed"]
    planned_minutes = sum(s["planned_minutes"] for s in planned + completed)
    completed_minutes = sum(s["planned_minutes"] for s in completed)
    deadlines = list_deadlines(USER_ID)
    upcoming = [d for d in deadlines if d["due_date"] >= today][:6]
    readiness = readiness_for_deadlines(USER_ID, deadlines)
    available = weekday_budget(user, date.today())
    overload = planned_minutes > available
    scores = scored_topics(USER_ID, date.today())
    return jsonify(
        {
            "user": {
                "name": user["name"],
                "daily_available_minutes": user["daily_available_minutes"],
                "gemini_enabled": gemini_available(),
            },
            "today": today,
            "today_plan": sessions,
            "stats": {
                "planned_minutes": planned_minutes,
                "completed_minutes": completed_minutes,
                "available_minutes": available,
                "completed_tasks": len(completed),
                "pending_tasks": len(planned),
                "missed_tasks": len(missed),
            },
            "overload": overload,
            "deadlines": upcoming,
            "readiness": readiness,
            "top_priorities": [
                {
                    "topic": item["topic"]["name"],
                    "subject": item["topic"].get("subject_name"),
                    "score": item["score"],
                    "progress_pct": item["topic"].get("progress_pct"),
                    "remaining_minutes": item["remaining"],
                }
                for item in scores[:4]
            ],
        }
    )


@bp.get("/api/progress")
def progress():
    today = date.today()
    start = today - timedelta(days=13)
    logs = {row["date"]: row for row in list_progress_logs(USER_ID, start.isoformat(), today.isoformat())}
    hours = []
    tasks = []
    for i in range(14):
        day = (start + timedelta(days=i)).isoformat()
        row = logs.get(day, {"minutes_studied": 0, "tasks_completed": 0})
        hours.append({"date": day, "hours": round(row["minutes_studied"] / 60, 2)})
        tasks.append({"date": day, "completed": row["tasks_completed"]})
    subjects = []
    for subject in list_subjects(USER_ID):
        topics = list_topics(subject_id=subject["id"])
        avg = round(sum(t["progress_pct"] for t in topics) / len(topics), 1) if topics else 0
        subjects.append(
            {
                "id": subject["id"],
                "name": subject["name"],
                "color": subject["color"],
                "progress": avg,
                "topics": len(topics),
            }
        )
    return jsonify({"hours": hours, "tasks": tasks, "subjects": subjects})


@bp.get("/api/readiness")
def readiness():
    deadlines = list_deadlines(USER_ID)
    return jsonify(readiness_for_deadlines(USER_ID, deadlines))


@bp.get("/api/settings")
def get_settings():
    user = get_user(USER_ID)
    return jsonify(
        {
            "name": user["name"],
            "daily_available_minutes": user["daily_available_minutes"],
            "week_availability_json": user.get("week_availability_json"),
            "gemini_enabled": gemini_available(),
        }
    )


@bp.patch("/api/settings")
def patch_settings():
    data = request.get_json(silent=True) or {}
    fields = {}
    if "name" in data:
        fields["name"] = str(data["name"]).strip() or "Alex"
    if "daily_available_minutes" in data:
        fields["daily_available_minutes"] = max(30, int(data["daily_available_minutes"]))
    if "week_availability_json" in data:
        fields["week_availability_json"] = data["week_availability_json"]
    user = update_user(USER_ID, fields)
    return jsonify(
        {
            "name": user["name"],
            "daily_available_minutes": user["daily_available_minutes"],
            "week_availability_json": user.get("week_availability_json"),
            "gemini_enabled": gemini_available(),
        }
    )
