from datetime import date, timedelta

from config import (
    MAX_CHUNK,
    MIN_CHUNK,
    PLAN_HORIZON_DAYS,
    SESSION_GAP_MINUTES,
    SESSION_START,
    USER_ID,
)
from models import (
    create_session,
    delete_planned_sessions,
    get_user,
    list_deadlines,
    list_sessions,
    list_topics,
    recent_misses_for_topic,
)
from services.gemini import generate_text
from services.notifications import notify
from services.overload import cap_day_sessions, day_overloaded
from services.readiness import nearest_deadline_for_topic, priority_score, remaining_minutes
from services.timeutil import add_minutes, weekday_budget


def scored_topics(user_id, today, deadlines=None, topics=None):
    deadlines = deadlines if deadlines is not None else list_deadlines(user_id)
    topics = topics if topics is not None else list_topics(user_id=user_id)
    since = (today - timedelta(days=3)).isoformat()
    scored = []
    for topic in topics:
        if remaining_minutes(topic) <= 0:
            continue
        deadline = nearest_deadline_for_topic(topic, deadlines, today)
        missed = recent_misses_for_topic(topic["id"], since) > 0
        score = priority_score(topic, deadline, today, missed)
        scored.append(
            {
                "topic": topic,
                "deadline": deadline,
                "score": round(score, 4),
                "remaining": remaining_minutes(topic),
            }
        )
    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored


def pack_horizon(scored, user, today, days=PLAN_HORIZON_DAYS):
    remaining = {item["topic"]["id"]: item["remaining"] for item in scored}
    lookup = {item["topic"]["id"]: item for item in scored}
    plan = []
    overflow = False
    demand = sum(remaining.values())
    supply = sum(weekday_budget(user, today + timedelta(days=i)) for i in range(days))
    if demand > supply:
        overflow = True

    for offset in range(days):
        day = today + timedelta(days=offset)
        budget = weekday_budget(user, day)
        used = 0
        cursor = SESSION_START
        for item in scored:
            topic = item["topic"]
            left = remaining[topic["id"]]
            if left <= 0 or used >= budget:
                continue
            while left > 0 and used < budget:
                chunk = min(MAX_CHUNK, left, budget - used)
                if chunk < MIN_CHUNK and budget - used < MIN_CHUNK:
                    break
                if chunk < MIN_CHUNK:
                    chunk = min(left, budget - used)
                if chunk <= 0:
                    break
                session = {
                    "topic_id": topic["id"],
                    "topic_name": topic["name"],
                    "subject_name": topic.get("subject_name"),
                    "deadline_id": item["deadline"]["id"] if item["deadline"] else None,
                    "date": day.isoformat(),
                    "start_time": cursor,
                    "end_time": add_minutes(cursor, chunk),
                    "planned_minutes": chunk,
                    "priority_score": item["score"],
                    "notes": _session_note(topic, item["deadline"], item["score"]),
                }
                plan.append(session)
                used += chunk
                left -= chunk
                remaining[topic["id"]] = left
                cursor = add_minutes(cursor, chunk + SESSION_GAP_MINUTES)
        plan = cap_day_sessions(plan, day.isoformat(), budget)
    return plan, overflow, lookup


def _session_note(topic, deadline, score):
    bits = [f"Priority {score:.2f}"]
    if deadline:
        bits.append(f"for {deadline['title']}")
    bits.append(f"{topic.get('progress_pct', 0)}% complete")
    return " · ".join(bits)


def maybe_refine_with_gemini(plan, scored, user, today):
    if not plan:
        return plan, False
    payload = {
        "available_minutes_per_day": user["daily_available_minutes"],
        "today": today.isoformat(),
        "sessions": plan,
        "instruction": (
            "You may reorder sessions within each day and tweak notes. "
            "Do not change dates unless necessary. Never exceed available minutes for a day. "
            "Keep the same topics. Return JSON {\"sessions\": [...]} with the same fields."
        ),
    }
    result = generate_text(
        "Return only JSON. Refine this study plan for a student.\n" + str(payload),
        json_mode=True,
    )
    if not result:
        return plan, False
    sessions = result.get("sessions") if isinstance(result, dict) else result
    if not isinstance(sessions, list) or not sessions:
        return plan, False
    required = {"topic_id", "date", "planned_minutes"}
    cleaned = []
    for session in sessions:
        if not required.issubset(session.keys()):
            return plan, False
        minutes = int(session["planned_minutes"])
        start = session.get("start_time") or SESSION_START
        cleaned.append(
            {
                "topic_id": int(session["topic_id"]),
                "topic_name": session.get("topic_name"),
                "subject_name": session.get("subject_name"),
                "deadline_id": session.get("deadline_id"),
                "date": session["date"][:10],
                "start_time": start,
                "end_time": session.get("end_time") or add_minutes(start, minutes),
                "planned_minutes": minutes,
                "priority_score": float(session.get("priority_score") or 0),
                "notes": session.get("notes"),
            }
        )
    by_day = {}
    for session in cleaned:
        by_day.setdefault(session["date"], 0)
        by_day[session["date"]] += session["planned_minutes"]
        day = date.fromisoformat(session["date"])
        if by_day[session["date"]] > weekday_budget(user, day):
            return plan, False
    return cleaned, True


def persist_plan(user_id, plan):
    saved = []
    for session in plan:
        saved.append(
            create_session(
                {
                    "user_id": user_id,
                    "topic_id": session["topic_id"],
                    "deadline_id": session.get("deadline_id"),
                    "date": session["date"],
                    "start_time": session["start_time"],
                    "end_time": session["end_time"],
                    "planned_minutes": session["planned_minutes"],
                    "status": "planned",
                    "priority_score": session.get("priority_score") or 0,
                    "notes": session.get("notes"),
                }
            )
        )
    return saved


def generate_plan(user_id=USER_ID, today=None, days=PLAN_HORIZON_DAYS):
    today = today or date.today()
    user = get_user(user_id)
    if not user:
        raise ValueError("User not found")
    deadlines = list_deadlines(user_id)
    topics = list_topics(user_id=user_id)
    if not topics:
        raise ValueError("Add subjects and topics before generating a plan")
    scored = scored_topics(user_id, today, deadlines, topics)
    if not scored:
        raise ValueError("All topics are complete. Add new topics or lower progress to plan more work.")
    end = today + timedelta(days=days - 1)
    delete_planned_sessions(user_id, today.isoformat(), end.isoformat())
    plan, overflow, _lookup = pack_horizon(scored, user, today, days)
    plan, used_gemini = maybe_refine_with_gemini(plan, scored, user, today)
    saved = persist_plan(user_id, plan)
    if overflow or any(day_overloaded(saved, user, date.fromisoformat(s["date"])) for s in saved):
        notify(
            "overload",
            "Schedule optimized to fit your day",
            "Requested study time exceeded available hours. Lower-priority sessions were deferred or shortened.",
        )
    if saved:
        top = saved[0]
        notify(
            "deadline",
            "AI study plan ready",
            f"Today starts with {top['topic_name']} ({top['planned_minutes']} min). Plans stay within your daily study time.",
            related_session_id=top["id"],
        )
    return {
        "sessions": saved,
        "used_gemini": used_gemini,
        "overflow": overflow,
        "horizon_days": days,
        "top_priorities": [
            {
                "topic": item["topic"]["name"],
                "subject": item["topic"].get("subject_name"),
                "score": item["score"],
                "remaining_minutes": item["remaining"],
            }
            for item in scored[:5]
        ],
    }


def optimize_schedule(user_id=USER_ID, today=None, days=PLAN_HORIZON_DAYS):
    today = today or date.today()
    user = get_user(user_id)
    end = today + timedelta(days=days - 1)
    sessions = list_sessions(
        user_id,
        from_date=today.isoformat(),
        to_date=end.isoformat(),
        statuses=["planned"],
    )
    changed = False
    by_day = {}
    for session in sessions:
        by_day.setdefault(session["date"], []).append(session)
    kept = []
    for day_str, items in by_day.items():
        budget = weekday_budget(user, date.fromisoformat(day_str))
        capped = cap_day_sessions(items, day_str, budget)
        if len(capped) != len(items) or any(
            c["planned_minutes"] != i["planned_minutes"] for c, i in zip(capped, items[: len(capped)])
        ):
            changed = True
        kept.extend(capped)
    delete_planned_sessions(user_id, today.isoformat(), end.isoformat())
    saved = persist_plan(user_id, kept)
    if changed:
        notify(
            "overload",
            "Overload trimmed",
            "Sessions were shortened or dropped so each day fits your available study time.",
        )
    return {"sessions": saved, "changed": changed}
