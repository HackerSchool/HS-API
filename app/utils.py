import re
import unicodedata

from datetime import date, datetime
from enum import Enum


class ProjectStateEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    UNDEFINED = "undefined"


def slugify(text):
    # GPT GENERATED!!
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")

    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)  # Remove punctuation/special chars
    text = re.sub(r"[\s_-]+", "-", text)  # Replace spaces/underscores with hyphens
    text = text.strip("-")  # Remove leading/trailing hyphens
    return text


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
