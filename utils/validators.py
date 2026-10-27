"""Input validation helpers used by services (backend enforcement)."""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^[\d\s+\-()]{7,20}$")


class ValidationError(ValueError):
    """Raised when user input fails validation."""


def require_non_empty(value: str | None, field: str) -> str:
    if value is None or not str(value).strip():
        raise ValidationError(f"{field} is required.")
    return str(value).strip()


def optional_email(value: str | None) -> str | None:
    if value is None or not str(value).strip():
        return None
    email = str(value).strip()
    if not EMAIL_RE.match(email):
        raise ValidationError("Invalid email format.")
    return email


def optional_phone(value: str | None) -> str | None:
    if value is None or not str(value).strip():
        return None
    phone = str(value).strip()
    if not PHONE_RE.match(phone):
        raise ValidationError("Invalid phone number format.")
    return phone


def parse_date(value: str | date | datetime | None, field: str) -> date:
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValidationError(f"{field} is required.")
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value).strip())
    except ValueError as exc:
        raise ValidationError(f"{field} must be YYYY-MM-DD.") from exc


def parse_future_appointment(value: str | datetime, field: str = "appointment_datetime") -> datetime:
    if isinstance(value, datetime):
        dt = value
    else:
        raw = str(value).strip()
        try:
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValidationError(f"{field} must be ISO datetime.") from exc
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)
    return dt


def clean_dict(data: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in data.items() if v is not None}
