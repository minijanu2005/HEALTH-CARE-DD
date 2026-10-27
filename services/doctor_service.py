"""Doctor directory management."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from database import next_sequence
from models.constants import Collection
from permissions import PermissionDenied, can_manage_doctors
from utils.audit import log_audit
from utils.facility_meta import bump_version, stamp_new_document
from utils.validators import ValidationError, optional_email, optional_phone, require_non_empty


def _format_doctor_id(seq: int) -> str:
    return f"DOC-{seq:03d}"


def create_doctor(
    db: Any,
    *,
    actor: dict[str, str],
    full_name: str,
    specialty: str,
    phone: str | None = None,
    email: str | None = None,
) -> dict[str, Any]:
    if not can_manage_doctors(actor["role"]):
        raise PermissionDenied("Only administrators can add doctors.")
    seq = next_sequence(db, "doctor")
    doctor_id = _format_doctor_id(seq)
    doc = stamp_new_document(
        {
            "doctor_id": doctor_id,
            "full_name": require_non_empty(full_name, "full_name"),
            "specialty": require_non_empty(specialty, "specialty"),
            "phone": optional_phone(phone),
            "email": optional_email(email),
        }
    )
    db[Collection.DOCTORS].insert_one(doc)
    log_audit(
        db,
        actor_username=actor["username"],
        actor_role=actor["role"],
        action="create_doctor",
        entity_type="doctor",
        entity_id=doctor_id,
    )
    return doc


def update_doctor(
    db: Any,
    *,
    actor: dict[str, str],
    doctor_id: str,
    full_name: str | None = None,
    specialty: str | None = None,
    phone: str | None = None,
    email: str | None = None,
) -> dict[str, Any]:
    if not can_manage_doctors(actor["role"]):
        raise PermissionDenied("Only administrators can edit doctors.")
    existing = db[Collection.DOCTORS].find_one({"doctor_id": doctor_id})
    if not existing:
        raise ValidationError("Doctor not found.")
    updates = bump_version(existing)
    if full_name is not None:
        updates["full_name"] = require_non_empty(full_name, "full_name")
    if specialty is not None:
        updates["specialty"] = require_non_empty(specialty, "specialty")
    if phone is not None:
        updates["phone"] = optional_phone(phone)
    if email is not None:
        updates["email"] = optional_email(email)
    db[Collection.DOCTORS].update_one({"doctor_id": doctor_id}, {"$set": updates})
    log_audit(
        db,
        actor_username=actor["username"],
        actor_role=actor["role"],
        action="update_doctor",
        entity_type="doctor",
        entity_id=doctor_id,
    )
    return db[Collection.DOCTORS].find_one({"doctor_id": doctor_id})  # type: ignore


def set_doctor_active(db: Any, *, actor: dict[str, str], doctor_id: str, active: bool) -> None:
    if not can_manage_doctors(actor["role"]):
        raise PermissionDenied("Only administrators can change doctor status.")
    existing = db[Collection.DOCTORS].find_one({"doctor_id": doctor_id})
    if not existing:
        raise ValidationError("Doctor not found.")
    updates = bump_version(existing)
    updates["active"] = active
    db[Collection.DOCTORS].update_one({"doctor_id": doctor_id}, {"$set": updates})
    log_audit(
        db,
        actor_username=actor["username"],
        actor_role=actor["role"],
        action="doctor_activate" if active else "doctor_deactivate",
        entity_type="doctor",
        entity_id=doctor_id,
    )


def list_doctors(
    db: Any,
    *,
    active_only: bool = True,
    specialty: str | None = None,
    query: str = "",
) -> list[dict[str, Any]]:
    mongo_query: dict[str, Any] = {}
    if active_only:
        mongo_query["active"] = True
    if specialty:
        mongo_query["specialty"] = specialty
    q = query.strip()
    if q:
        regex = {"$regex": q, "$options": "i"}
        mongo_query["$or"] = [{"full_name": regex}, {"doctor_id": regex}, {"specialty": regex}]
    return list(db[Collection.DOCTORS].find(mongo_query).sort("full_name", 1))


def get_doctor(db: Any, doctor_id: str) -> dict[str, Any] | None:
    return db[Collection.DOCTORS].find_one({"doctor_id": doctor_id, "active": {"$ne": False}})


def count_doctors(db: Any) -> int:
    return db[Collection.DOCTORS].count_documents({"active": True})


def doctor_appointment_count(db: Any, doctor_id: str) -> int:
    return db[Collection.APPOINTMENTS].count_documents({"doctor_id": doctor_id})
