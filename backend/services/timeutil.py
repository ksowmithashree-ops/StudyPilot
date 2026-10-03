import json


def add_minutes(hhmm, minutes):
    hours, mins = map(int, hhmm.split(":"))
    total = hours * 60 + mins + minutes
    total = max(0, total)
    return f"{total // 60:02d}:{total % 60:02d}"


def weekday_budget(user, day):
    default = user["daily_available_minutes"]
    raw = user.get("week_availability_json")
    if not raw:
        return default
    try:
        data = json.loads(raw)
        key = str(day.weekday())
        if key in data:
            return int(data[key])
        names = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        return int(data.get(names[day.weekday()], default))
    except (TypeError, ValueError):
        return default
