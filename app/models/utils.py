from datetime import date

import bcrypt


def _hash_password(password) -> str:
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def _validate_date_string(date_string: str, field_name: str):
    """Validate and convert date string to datetime.date."""
    try:
        date.fromisoformat(date_string)
    except ValueError:
        raise ValueError(f"'{field_name}' must be a valid date in the format YYYY-MM-DD.")
