"""Facility and versioning metadata for distributed sync."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from config import get_settings


def stamp_new_document(extra: dict[str, Any] | None = None) -> dict[str, Any]:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    base = {
        "facility_id": settings.facility_id,
        "source_facility_id": settings.facility_id,
        "version": 1,
        "created_at": now,
        "updated_at": now,
        "active": True,
    }
    if extra:
        base.update(extra)
    return base


def bump_version(existing: dict[str, Any]) -> dict[str, Any]:
    settings = get_settings()
    return {
        "version": int(existing.get("version", 1)) + 1,
        "updated_at": datetime.now(timezone.utc),
        "source_facility_id": settings.facility_id,
    }
