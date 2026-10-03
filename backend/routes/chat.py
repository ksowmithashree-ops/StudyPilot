from datetime import date

from flask import Blueprint, jsonify, request

from config import USER_ID
from models import list_deadlines, list_sessions
from services.gemini import generate_text, gemini_available
from services.planner import scored_topics
from services.readiness import readiness_for_deadlines

bp = Blueprint("chat", __name__)


def fallback_answer(message, context):
    text = (message or "").lower()
    today = context.get("today_topics") or []
    top = context.get("top_priorities") or []
    readiness = context.get("readiness") or []
    if "today" in text or "what should i study" in text:
        if today:
            names = ", ".join(t["topic_name"] for t in today[:3])
            return f"Today, focus on {names}. Those sessions already fit your available study time."
        if top:
            lead = top[0]
            return (
                f"Generate a plan if you haven't yet. Highest priority is {lead['topic']} "
                f"({lead['subject']}) because of weak progress and a nearby deadline."
            )
        return "Add subjects and an exam deadline, then generate an AI plan."
    if "ready" in text or "readiness" in text or "dbms" in text:
        if readiness:
            exam = readiness[0]
            return (
                f"{exam['title']} readiness is {exam['readiness']}%. "
                "Raise it by completing Normalization and other low-progress DBMS topics."
            )
        return "No exams on the calendar yet."
    if "overdue" in text or "missed" in text:
        return "Check notifications for missed tasks. Missed sessions are rescheduled into the next free slot automatically."
    if top:
        return f"Start with {top[0]['topic']}. It currently has the highest priority score in your planner."
    return "I can help with today's plan, exam readiness, and missed-task rescheduling."


@bp.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "message is required"}), 400
    today = date.today().isoformat()
    sessions = [s for s in list_sessions(USER_ID, today, today) if s["status"] == "planned"]
    scores = scored_topics(USER_ID, date.today())[:3]
    deadlines = list_deadlines(USER_ID)
    readiness = readiness_for_deadlines(USER_ID, deadlines)
    context = {
        "today_topics": [{"topic_name": s["topic_name"], "minutes": s["planned_minutes"]} for s in sessions],
        "top_priorities": [
            {"topic": i["topic"]["name"], "subject": i["topic"].get("subject_name"), "score": i["score"]}
            for i in scores
        ],
        "readiness": readiness,
        "next_exam": next((d for d in deadlines if d["type"] == "exam"), None),
    }
    prompt = (
        "You are StudyPilot, a concise study coach. Answer in 2-4 sentences. "
        f"Student question: {message}\nContext JSON: {context}"
    )
    ai = generate_text(prompt) if gemini_available() else None
    reply = ai or fallback_answer(message, context)
    return jsonify({"reply": reply, "used_gemini": bool(ai), "context": context})
