from datetime import date, datetime, timedelta

from config import RESCHEDULE_HORIZON_DAYS, SESSION_GAP_MINUTES, SESSION_START, USER_ID
from models import (
    add_task_event,
    create_session,
    get_session,
    get_user,
    list_deadlines,
    list_sessions,
    update_session,
)
from services.notifications import notify
from services.timeutil import add_minutes, weekday_budget


def _used_on(user_id, day_str, statuses=None):
    statuses = statuses or ["planned", "completed"]
    sessions = list_sessions(user_id, from_date=day_str, to_date=day_str, statuses=statuses)
    return sum(s["planned_minutes"] for s in sessions), sessions


def _next_start(sessions):
    if not sessions:
        return SESSION_START
    last = max(sessions, key=lambda s: s["end_time"])
    return add_minutes(last["end_time"], SESSION_GAP_MINUTES)


def reschedule_missed(session_id, user_id=USER_ID, today=None):
    today = today or date.today()
    session = get_session(session_id)
    if not session or session["user_id"] != user_id:
        raise ValueError("Session not found")
    if session["status"] != "planned":
        raise ValueError("Only planned sessions can be marked missed")

    missed = update_session(session_id, {"status": "missed"})
    now = datetime.now().replace(microsecond=0).isoformat()
    add_task_event(session_id, "missed", session["date"], None, now)

    user = get_user(user_id)
    deadlines = list_deadlines(user_id)
    exam_mornings = {
        d["due_date"][:10]
        for d in deadlines
        if d["type"] == "exam"
    }
    needed = session["planned_minutes"]
    new_session = None
    leftover = needed

    for offset in range(1, RESCHEDULE_HORIZON_DAYS + 1):
        day = today + timedelta(days=offset)
        day_str = day.isoformat()
        if day_str in exam_mornings:
            continue
        used, existing = _used_on(user_id, day_str)
        budget = weekday_budget(user, day)
        free = budget - used
        if free < 15:
            continue
        chunk = min(leftover, free)
        start = _next_start(existing)
        created = create_session(
            {
                "user_id": user_id,
                "topic_id": session["topic_id"],
                "deadline_id": session.get("deadline_id"),
                "date": day_str,
                "start_time": start,
                "end_time": add_minutes(start, chunk),
                "planned_minutes": chunk,
                "status": "planned",
                "priority_score": (session.get("priority_score") or 0) + 0.1,
                "notes": f"Rescheduled from {session['date']} · {session.get('notes') or ''}".strip(" ·"),
            }
        )
        add_task_event(created["id"], "rescheduled", session["date"], day_str, now)
        leftover -= chunk
        if new_session is None:
            new_session = created
        if leftover <= 0:
            break

    if leftover > 0 and new_session is None:
        # Steal from the lowest-score future planned session.
        future = list_sessions(
            user_id,
            from_date=(today + timedelta(days=1)).isoformat(),
            to_date=(today + timedelta(days=RESCHEDULE_HORIZON_DAYS)).isoformat(),
            statuses=["planned"],
        )
        future.sort(key=lambda s: (s.get("priority_score") or 0, s["planned_minutes"]))
        if future:
            victim = future[0]
            stolen = min(victim["planned_minutes"], leftover)
            remaining = victim["planned_minutes"] - stolen
            if remaining >= 15:
                update_session(
                    victim["id"],
                    {
                        "planned_minutes": remaining,
                        "end_time": add_minutes(victim["start_time"], remaining),
                    },
                )
            else:
                update_session(victim["id"], {"status": "rescheduled"})
            start = victim["start_time"] if remaining < 15 else add_minutes(victim["end_time"], SESSION_GAP_MINUTES)
            new_session = create_session(
                {
                    "user_id": user_id,
                    "topic_id": session["topic_id"],
                    "deadline_id": session.get("deadline_id"),
                    "date": victim["date"],
                    "start_time": start,
                    "end_time": add_minutes(start, stolen),
                    "planned_minutes": stolen,
                    "status": "planned",
                    "priority_score": (session.get("priority_score") or 0) + 0.1,
                    "notes": f"Rescheduled from {session['date']} by reclaiming a lower-priority slot",
                }
            )
            leftover = 0
            notify(
                "overload",
                "Tight week — slot reclaimed",
                f"Moved {session['topic_name']} into a lower-priority session on {victim['date']}.",
                related_session_id=new_session["id"],
            )

    notify(
        "missed",
        f"Missed: {session['topic_name']}",
        f"The {session['planned_minutes']} min session on {session['date']} was marked missed.",
        related_session_id=session_id,
    )
    if new_session:
        notify(
            "rescheduled",
            f"{session['topic_name']} moved to {new_session['date']}",
            f"A {new_session['planned_minutes']} min slot was booked at {new_session['start_time']}.",
            related_session_id=new_session["id"],
        )
    else:
        notify(
            "overload",
            "Could not find a full reschedule slot",
            f"{session['topic_name']} is flagged missed. Increase available hours or optimize the plan.",
            related_session_id=session_id,
        )

    return {"missed": missed, "rescheduled": new_session}
