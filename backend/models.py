from database import db, row_to_dict, rows_to_list


def get_user(user_id):
    with db() as conn:
        return row_to_dict(conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone())


def update_user(user_id, fields):
    allowed = {"name", "daily_available_minutes", "week_availability_json"}
    sets = []
    values = []
    for key, value in fields.items():
        if key in allowed:
            sets.append(f"{key} = ?")
            values.append(value)
    if not sets:
        return get_user(user_id)
    values.append(user_id)
    with db() as conn:
        conn.execute(f"UPDATE users SET {', '.join(sets)} WHERE id = ?", values)
    return get_user(user_id)


def list_subjects(user_id):
    with db() as conn:
        return rows_to_list(
            conn.execute("SELECT * FROM subjects WHERE user_id = ? ORDER BY name", (user_id,)).fetchall()
        )


def get_subject(subject_id, user_id=None):
    sql = "SELECT * FROM subjects WHERE id = ?"
    args = [subject_id]
    if user_id is not None:
        sql += " AND user_id = ?"
        args.append(user_id)
    with db() as conn:
        return row_to_dict(conn.execute(sql, args).fetchone())


def create_subject(user_id, name, color="#6366f1", importance=3):
    with db() as conn:
        cur = conn.execute(
            "INSERT INTO subjects (user_id, name, color, importance) VALUES (?, ?, ?, ?)",
            (user_id, name, color, importance),
        )
        subject_id = cur.lastrowid
    return get_subject(subject_id)


def update_subject(subject_id, fields):
    allowed = {"name", "color", "importance"}
    sets = []
    values = []
    for key, value in fields.items():
        if key in allowed:
            sets.append(f"{key} = ?")
            values.append(value)
    if sets:
        values.append(subject_id)
        with db() as conn:
            conn.execute(f"UPDATE subjects SET {', '.join(sets)} WHERE id = ?", values)
    return get_subject(subject_id)


def delete_subject(subject_id):
    with db() as conn:
        conn.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))


def list_topics(subject_id=None, user_id=None):
    with db() as conn:
        if subject_id is not None:
            return rows_to_list(
                conn.execute(
                    "SELECT t.*, s.name AS subject_name, s.color AS subject_color, s.importance AS subject_importance "
                    "FROM topics t JOIN subjects s ON s.id = t.subject_id WHERE t.subject_id = ? ORDER BY t.name",
                    (subject_id,),
                ).fetchall()
            )
        return rows_to_list(
            conn.execute(
                "SELECT t.*, s.name AS subject_name, s.color AS subject_color, s.importance AS subject_importance "
                "FROM topics t JOIN subjects s ON s.id = t.subject_id WHERE s.user_id = ? ORDER BY s.name, t.name",
                (user_id,),
            ).fetchall()
        )


def get_topic(topic_id):
    with db() as conn:
        return row_to_dict(
            conn.execute(
                "SELECT t.*, s.name AS subject_name, s.color AS subject_color, s.importance AS subject_importance, s.user_id "
                "FROM topics t JOIN subjects s ON s.id = t.subject_id WHERE t.id = ?",
                (topic_id,),
            ).fetchone()
        )


def create_topic(subject_id, name, difficulty=3, progress_pct=0, estimated_minutes=120):
    with db() as conn:
        cur = conn.execute(
            "INSERT INTO topics (subject_id, name, difficulty, progress_pct, estimated_minutes) VALUES (?, ?, ?, ?, ?)",
            (subject_id, name, difficulty, progress_pct, estimated_minutes),
        )
        topic_id = cur.lastrowid
    return get_topic(topic_id)


def update_topic(topic_id, fields):
    allowed = {
        "name",
        "difficulty",
        "progress_pct",
        "estimated_minutes",
        "revision_count",
        "last_studied_at",
    }
    sets = []
    values = []
    for key, value in fields.items():
        if key in allowed:
            sets.append(f"{key} = ?")
            values.append(value)
    if sets:
        values.append(topic_id)
        with db() as conn:
            conn.execute(f"UPDATE topics SET {', '.join(sets)} WHERE id = ?", values)
    return get_topic(topic_id)


def delete_topic(topic_id):
    with db() as conn:
        conn.execute("DELETE FROM topics WHERE id = ?", (topic_id,))


def list_deadlines(user_id):
    with db() as conn:
        return rows_to_list(
            conn.execute(
                "SELECT d.*, s.name AS subject_name, s.color AS subject_color, t.name AS topic_name "
                "FROM deadlines d JOIN subjects s ON s.id = d.subject_id "
                "LEFT JOIN topics t ON t.id = d.topic_id "
                "WHERE d.user_id = ? ORDER BY d.due_date",
                (user_id,),
            ).fetchall()
        )


def get_deadline(deadline_id):
    with db() as conn:
        return row_to_dict(
            conn.execute(
                "SELECT d.*, s.name AS subject_name, s.color AS subject_color, t.name AS topic_name "
                "FROM deadlines d JOIN subjects s ON s.id = d.subject_id "
                "LEFT JOIN topics t ON t.id = d.topic_id WHERE d.id = ?",
                (deadline_id,),
            ).fetchone()
        )


def create_deadline(user_id, subject_id, title, due_date, type_="exam", topic_id=None, priority=3):
    with db() as conn:
        cur = conn.execute(
            "INSERT INTO deadlines (user_id, subject_id, topic_id, type, title, due_date, priority) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, subject_id, topic_id, type_, title, due_date, priority),
        )
        deadline_id = cur.lastrowid
    return get_deadline(deadline_id)


def update_deadline(deadline_id, fields):
    allowed = {"subject_id", "topic_id", "type", "title", "due_date", "priority"}
    sets = []
    values = []
    for key, value in fields.items():
        if key in allowed:
            sets.append(f"{key} = ?")
            values.append(value)
    if sets:
        values.append(deadline_id)
        with db() as conn:
            conn.execute(f"UPDATE deadlines SET {', '.join(sets)} WHERE id = ?", values)
    return get_deadline(deadline_id)


def delete_deadline(deadline_id):
    with db() as conn:
        conn.execute("DELETE FROM deadlines WHERE id = ?", (deadline_id,))


def list_sessions(user_id, from_date=None, to_date=None, statuses=None):
    sql = (
        "SELECT ss.*, t.name AS topic_name, s.name AS subject_name, s.color AS subject_color "
        "FROM study_sessions ss "
        "JOIN topics t ON t.id = ss.topic_id "
        "JOIN subjects s ON s.id = t.subject_id "
        "WHERE ss.user_id = ?"
    )
    args = [user_id]
    if from_date:
        sql += " AND ss.date >= ?"
        args.append(from_date)
    if to_date:
        sql += " AND ss.date <= ?"
        args.append(to_date)
    if statuses:
        placeholders = ",".join("?" * len(statuses))
        sql += f" AND ss.status IN ({placeholders})"
        args.extend(statuses)
    sql += " ORDER BY ss.date, ss.start_time"
    with db() as conn:
        return rows_to_list(conn.execute(sql, args).fetchall())


def get_session(session_id):
    with db() as conn:
        return row_to_dict(
            conn.execute(
                "SELECT ss.*, t.name AS topic_name, s.name AS subject_name, s.color AS subject_color "
                "FROM study_sessions ss "
                "JOIN topics t ON t.id = ss.topic_id "
                "JOIN subjects s ON s.id = t.subject_id "
                "WHERE ss.id = ?",
                (session_id,),
            ).fetchone()
        )


def create_session(payload):
    with db() as conn:
        cur = conn.execute(
            "INSERT INTO study_sessions "
            "(user_id, topic_id, deadline_id, date, start_time, end_time, planned_minutes, status, priority_score, notes) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                payload["user_id"],
                payload["topic_id"],
                payload.get("deadline_id"),
                payload["date"],
                payload["start_time"],
                payload["end_time"],
                payload["planned_minutes"],
                payload.get("status", "planned"),
                payload.get("priority_score", 0),
                payload.get("notes"),
            ),
        )
        session_id = cur.lastrowid
    return get_session(session_id)


def update_session(session_id, fields):
    allowed = {
        "date",
        "start_time",
        "end_time",
        "planned_minutes",
        "status",
        "priority_score",
        "notes",
        "deadline_id",
    }
    sets = []
    values = []
    for key, value in fields.items():
        if key in allowed:
            sets.append(f"{key} = ?")
            values.append(value)
    if sets:
        values.append(session_id)
        with db() as conn:
            conn.execute(f"UPDATE study_sessions SET {', '.join(sets)} WHERE id = ?", values)
    return get_session(session_id)


def delete_planned_sessions(user_id, from_date, to_date):
    with db() as conn:
        conn.execute(
            "DELETE FROM study_sessions WHERE user_id = ? AND status = 'planned' AND date >= ? AND date <= ?",
            (user_id, from_date, to_date),
        )


def add_task_event(session_id, event, from_date=None, to_date=None, created_at=None):
    with db() as conn:
        conn.execute(
            "INSERT INTO task_events (session_id, event, from_date, to_date, created_at) VALUES (?, ?, ?, ?, ?)",
            (session_id, event, from_date, to_date, created_at),
        )


def recent_misses_for_topic(topic_id, since_date):
    with db() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS c FROM study_sessions "
            "WHERE topic_id = ? AND status = 'missed' AND date >= ?",
            (topic_id, since_date),
        ).fetchone()
        return row["c"] if row else 0


def bump_progress_log(user_id, date, minutes, tasks):
    with db() as conn:
        existing = conn.execute(
            "SELECT * FROM progress_logs WHERE user_id = ? AND date = ?",
            (user_id, date),
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE progress_logs SET minutes_studied = minutes_studied + ?, tasks_completed = tasks_completed + ? "
                "WHERE id = ?",
                (minutes, tasks, existing["id"]),
            )
        else:
            conn.execute(
                "INSERT INTO progress_logs (user_id, date, minutes_studied, tasks_completed) VALUES (?, ?, ?, ?)",
                (user_id, date, minutes, tasks),
            )


def list_progress_logs(user_id, from_date, to_date):
    with db() as conn:
        return rows_to_list(
            conn.execute(
                "SELECT * FROM progress_logs WHERE user_id = ? AND date >= ? AND date <= ? ORDER BY date",
                (user_id, from_date, to_date),
            ).fetchall()
        )


def list_notifications(user_id, unread_only=False):
    sql = "SELECT * FROM notifications WHERE user_id = ?"
    args = [user_id]
    if unread_only:
        sql += " AND read = 0"
    sql += " ORDER BY created_at DESC, id DESC"
    with db() as conn:
        return rows_to_list(conn.execute(sql, args).fetchall())


def create_notification(user_id, type_, title, body, related_session_id=None, created_at=None):
    with db() as conn:
        cur = conn.execute(
            "INSERT INTO notifications (user_id, type, title, body, read, created_at, related_session_id) "
            "VALUES (?, ?, ?, ?, 0, ?, ?)",
            (user_id, type_, title, body, created_at, related_session_id),
        )
        note_id = cur.lastrowid
    with db() as conn:
        return row_to_dict(conn.execute("SELECT * FROM notifications WHERE id = ?", (note_id,)).fetchone())


def mark_notifications_read(user_id, ids=None):
    with db() as conn:
        if ids:
            placeholders = ",".join("?" * len(ids))
            conn.execute(
                f"UPDATE notifications SET read = 1 WHERE user_id = ? AND id IN ({placeholders})",
                [user_id, *ids],
            )
        else:
            conn.execute("UPDATE notifications SET read = 1 WHERE user_id = ?", (user_id,))


def wipe_user_data(user_id):
    with db() as conn:
        conn.execute("DELETE FROM notifications WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM progress_logs WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM study_sessions WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM deadlines WHERE user_id = ?", (user_id,))
        conn.execute(
            "DELETE FROM topics WHERE subject_id IN (SELECT id FROM subjects WHERE user_id = ?)",
            (user_id,),
        )
        conn.execute("DELETE FROM subjects WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
