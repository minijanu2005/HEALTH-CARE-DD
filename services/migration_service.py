"""Non-destructive schema enrichment for existing MongoDB data."""

from __future__ import annotations

from typing import Any

from config import get_settings
from models.constants import Collection


def apply_safe_migrations(db: Any) -> None:
    """
    Add facility/version fields to existing documents without dropping data.
    """
    settings = get_settings()
    defaults = {
        "facility_id": settings.facility_id,
        "source_facility_id": settings.facility_id,
        "version": 1,
        "active": True,
    }
    for collection in (
        Collection.PATIENTS,
        Collection.DOCTORS,
        Collection.APPOINTMENTS,
        Collection.MEDICAL_RECORDS,
    ):
        db[collection].update_many(
            {"facility_id": {"$exists": False}},
            {"$set": defaults},
        )
