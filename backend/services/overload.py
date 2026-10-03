def cap_day_sessions(sessions, day_str, budget):
    day_items = [s for s in sessions if s["date"] == day_str]
    others = [s for s in sessions if s["date"] != day_str]
    day_items.sort(key=lambda s: (-(s.get("priority_score") or 0), s.get("start_time") or ""))
    kept = []
    used = 0
    for session in day_items:
        minutes = session["planned_minutes"]
        if used >= budget:
            continue
        if used + minutes > budget:
            minutes = budget - used
            if minutes < 15:
                continue
            session = {**session, "planned_minutes": minutes}
            start = session.get("start_time") or "09:00"
            hours, mins = map(int, start.split(":"))
            total = hours * 60 + mins + minutes
            session["end_time"] = f"{total // 60:02d}:{total % 60:02d}"
        kept.append(session)
        used += session["planned_minutes"]
    kept.sort(key=lambda s: s.get("start_time") or "")
    return others + kept


def day_overloaded(sessions, user, day):
    from services.timeutil import weekday_budget

    day_str = day.isoformat()
    used = sum(s["planned_minutes"] for s in sessions if s["date"] == day_str)
    return used > weekday_budget(user, day)
