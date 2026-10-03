from datetime import date, datetime, timedelta

from models import list_topics


def clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def remaining_minutes(topic):
    progress = clamp((topic.get("progress_pct") or 0) / 100.0)
    estimated = topic.get("estimated_minutes") or 0
    return max(0, int(round(estimated * (1 - progress))))


def days_until(due_date, today):
    if isinstance(due_date, str):
        due = date.fromisoformat(due_date[:10])
    else:
        due = due_date
    return (due - today).days


def nearest_deadline_for_topic(topic, deadlines, today):
    subject_id = topic["subject_id"]
    topic_id = topic["id"]
    candidates = [
        d
        for d in deadlines
        if d["subject_id"] == subject_id and days_until(d["due_date"], today) >= 0
    ]
    if not candidates:
        return None
    topic_specific = [d for d in candidates if d.get("topic_id") == topic_id]
    pool = topic_specific or candidates
    return min(pool, key=lambda d: (days_until(d["due_date"], today), -d.get("priority") or 0))


def priority_score(topic, deadline, today, missed_recently=False):
    if deadline:
        urgency = clamp(1 - days_until(deadline["due_date"], today) / 14.0)
    else:
        urgency = 0.15
    gap = 1 - clamp((topic.get("progress_pct") or 0) / 100.0)
    difficulty = (topic.get("difficulty") or 3) / 5.0
    importance = (topic.get("subject_importance") or 3) / 5.0
    missed_boost = 1.0 if missed_recently else 0.0
    time_fit = min(remaining_minutes(topic) / 60.0, 1.0)
    return (
        0.30 * urgency
        + 0.25 * gap
        + 0.15 * difficulty
        + 0.15 * importance
        + 0.10 * missed_boost
        + 0.05 * time_fit
    )


def exam_readiness(topics, exam_date, today):
    if not topics:
        return 0.0
    mastery = sum((t.get("progress_pct") or 0) for t in topics) / (100.0 * len(topics))
    revision = clamp(sum((t.get("revision_count") or 0) for t in topics) / len(topics) / 2.0)
    days_left = max(days_until(exam_date, today), 0)
    time_pressure = 1 - clamp(days_left / 14.0)
    return round(
        100
        * (
            0.55 * mastery
            + 0.25 * revision
            + 0.20 * (1 - time_pressure * (1 - mastery))
        ),
        1,
    )


def readiness_for_deadlines(user_id, deadlines, today=None):
    today = today or date.today()
    topics = list_topics(user_id=user_id)
    by_subject = {}
    for topic in topics:
        by_subject.setdefault(topic["subject_id"], []).append(topic)
    results = []
    for deadline in deadlines:
        if deadline["type"] != "exam":
            continue
        subject_topics = by_subject.get(deadline["subject_id"], [])
        score = exam_readiness(subject_topics, deadline["due_date"], today)
        results.append(
            {
                "deadline_id": deadline["id"],
                "title": deadline["title"],
                "subject_name": deadline.get("subject_name"),
                "due_date": deadline["due_date"],
                "days_left": days_until(deadline["due_date"], today),
                "readiness": score,
                "topic_count": len(subject_topics),
            }
        )
    return results
