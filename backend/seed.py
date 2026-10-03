from datetime import date, timedelta

from config import DEFAULT_AVAILABLE_MINUTES, USER_ID
from database import db, init_db
from models import wipe_user_data


def _iso(d):
    return d.isoformat()


def seed_demo(today=None):
    init_db()
    wipe_user_data(USER_ID)
    today = today or date.today()
    exam_day = today + timedelta(days=5)
    os_quiz = today + timedelta(days=10)
    web_due = today + timedelta(days=12)

    with db() as conn:
        conn.execute(
            "INSERT INTO users (id, name, daily_available_minutes, week_availability_json) VALUES (?, ?, ?, ?)",
            (USER_ID, "Alex", DEFAULT_AVAILABLE_MINUTES, None),
        )
        dbms_id = conn.execute(
            "INSERT INTO subjects (user_id, name, color, importance) VALUES (?, ?, ?, ?)",
            (USER_ID, "DBMS", "#6366f1", 5),
        ).lastrowid
        os_id = conn.execute(
            "INSERT INTO subjects (user_id, name, color, importance) VALUES (?, ?, ?, ?)",
            (USER_ID, "OS", "#8b5cf6", 3),
        ).lastrowid
        web_id = conn.execute(
            "INSERT INTO subjects (user_id, name, color, importance) VALUES (?, ?, ?, ?)",
            (USER_ID, "Web Dev", "#06b6d4", 4),
        ).lastrowid

        topics = [
            (dbms_id, "ER Model", 2, 70, 90, 1),
            (dbms_id, "SQL", 3, 55, 120, 1),
            (dbms_id, "Normalization", 5, 18, 180, 0),
            (dbms_id, "Transactions", 4, 40, 150, 0),
            (os_id, "Processes", 3, 60, 90, 1),
            (os_id, "Scheduling", 4, 35, 120, 0),
            (web_id, "React Components", 2, 75, 90, 1),
            (web_id, "REST APIs", 3, 45, 120, 0),
        ]
        for subject_id, name, difficulty, progress, minutes, revisions in topics:
            conn.execute(
                "INSERT INTO topics (subject_id, name, difficulty, progress_pct, estimated_minutes, revision_count) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (subject_id, name, difficulty, progress, minutes, revisions),
            )

        norm_id = conn.execute(
            "SELECT id FROM topics WHERE name = 'Normalization'"
        ).fetchone()[0]
        sched_id = conn.execute("SELECT id FROM topics WHERE name = 'Scheduling'").fetchone()[0]
        rest_id = conn.execute("SELECT id FROM topics WHERE name = 'REST APIs'").fetchone()[0]

        conn.execute(
            "INSERT INTO deadlines (user_id, subject_id, topic_id, type, title, due_date, priority) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (USER_ID, dbms_id, None, "exam", "DBMS Midterm", _iso(exam_day), 5),
        )
        conn.execute(
            "INSERT INTO deadlines (user_id, subject_id, topic_id, type, title, due_date, priority) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (USER_ID, os_id, sched_id, "quiz", "OS Scheduling Quiz", _iso(os_quiz), 3),
        )
        conn.execute(
            "INSERT INTO deadlines (user_id, subject_id, topic_id, type, title, due_date, priority) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (USER_ID, web_id, rest_id, "project", "Web API Project", _iso(web_due), 4),
        )

        yesterday = today - timedelta(days=1)
        conn.execute(
            "INSERT INTO progress_logs (user_id, date, minutes_studied, tasks_completed) VALUES (?, ?, ?, ?)",
            (USER_ID, _iso(yesterday), 90, 1),
        )
        conn.execute(
            "INSERT INTO progress_logs (user_id, date, minutes_studied, tasks_completed) VALUES (?, ?, ?, ?)",
            (USER_ID, _iso(today - timedelta(days=2)), 60, 1),
        )
        conn.execute(
            "INSERT INTO progress_logs (user_id, date, minutes_studied, tasks_completed) VALUES (?, ?, ?, ?)",
            (USER_ID, _iso(today - timedelta(days=3)), 45, 0),
        )

        # Keep the live generate step as the wow moment: no pre-filled future plan.
        conn.execute(
            "INSERT INTO notifications (user_id, type, title, body, read, created_at, related_session_id) "
            "VALUES (?, ?, ?, ?, 0, ?, NULL)",
            (
                USER_ID,
                "deadline",
                "DBMS exam in 5 days",
                "Normalization is only at 18%. Generate an AI plan to prioritize it before the midterm.",
                f"{_iso(today)}T08:00:00",
            ),
        )

    return {"ok": True, "user_id": USER_ID, "exam_date": _iso(exam_day), "normalization_topic_id": norm_id}
