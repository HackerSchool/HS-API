from datetime import date, datetime


def is_valid_datestring(v: str) -> bool:
    """Validate strings in format YYYY-MM-DD"""
    try:
        date.fromisoformat(v)
        return True
    except ValueError:
        return False


def is_valid_timestring(time_str: str):
    """Validate strings in format HH:MM"""
    try:
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False
