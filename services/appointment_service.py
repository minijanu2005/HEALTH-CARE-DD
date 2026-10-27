"""Appointment scheduling and status updates."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from database import next_sequence
from models.constants import AppointmentStatus, Collection
from permissions import PermissionDenied, can_manage_appointments, can_update_appointment_status
from services.doctor_service import get_doctor
from services.patient_service import get_patient
from utils.audit import log_audit
from utils.validators import ValidationError, parse_future_appointment, require_non_empty


def _format_appointment_id(seq: int) -> str:
    return f"APT-{seq:05d}"


def _check_conflict(db: Any, doctor_id: str, appointment_datetime: datetime, exclude_id: str | None = None) -> None:
    query: dict[str, Any] = {
        "doctor_id": doctor_id,
        "appointment_datetime": appointment_datetime,
        "status": {"$ne": AppointmentStatus.CANCELLED},
    }
    if exclude_id:
        query["appointment_id"] = {"$ne": exclude_id}
    if db[Collection.APPOINTMENTS].find_one(query):
        raise ValidationError("Conflicting appointment exists for this doctor and time.")


def create_appointment(
    db: Any,
    *,
    actor: dict[str, str],
    patient_id: str,
    doctor_id: str,
    appointment_datetime: str,
    notes: str | None = None,
) -> dict[str, Any]:
    if not can_manage_appointments(actor["role"]):
        raise PermissionDenied("You cannot schedule appointments.")
    if not get_patient(db, patient_id):
        raise ValidationError("Patient not found.")
    if not get_doctor(db, doctor_id):
        raise ValidationError("Doctor not found.")
    dt = parse_future_appointment(appointment_datetime)
    _check_conflict(db, doctor_id, dt)
    seq = next_sequence(db, "appointment")
    appointment_id = _format_appointment_id(seq)
    doc = {
        "appointment_id": appointment_id,
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "appointment_datetime": dt,
        "status": AppointmentStatus.SCHEDULED,
        "notes": (notes or "").strip() or None,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    db[Collection.APPOINTMENTS].insert_one(doc)
    log_audit(
        db,
        actor_username=actor["username"],
        actor_role=actor["role"],
        action="create_appointment",
        entity_type="appointment",
        entity_id=appointment_id,
    )
    return doc


def update_appointment_status(
    db: Any,
    *,
    actor: dict[str, str],
    appointment_id: str,
    status: str,
) -> dict[str, Any]:
    if not can_update_appointment_status(actor["role"]):
        raise PermissionDenied("You cannot update appointment status.")
    try:
        status_enum = AppointmentStatus(status)
    except ValueError as exc:
        raise ValidationError("Invalid appointment status.") from exc
    existing = db[Collection.APPOINTMENTS].find_one({"appointment_id": appointment_id})
    if not existing:
        raise ValidationError("Appointment not found.")
    db[Collection.APPOINTMENTS].update_one(
        {"appointment_id": appointment_id},
        {"$set": {"status": status_enum, "updated_at": datetime.now(timezone.utc)}},
    )
    log_audit(
        db,
        actor_username=actor["username"],
        actor_role=actor["role"],
        action="update_appointment_status",
        entity_type="appointment",
        entity_id=appointment_id,
        details={"status": status_enum},
    )
    return db[Collection.APPOINTMENTS].find_one({"appointment_id": appointment_id})  # type: ignore


def search_appointments(
    db: Any,
    *,
    patient_id: str | None = None,
    doctor_id: str | None = None,
    status: str | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    query: dict[str, Any] = {}
    if patient_id:
        query["patient_id"] = patient_id.strip()
    if doctor_id:
        query["doctor_id"] = doctor_id.strip()
    if status:
        query["status"] = require_non_empty(status, "status")
    return list(
        db[Collection.APPOINTMENTS].find(query).sort("appointment_datetime", 1).limit(limit)
    )


def count_appointments(db: Any) -> int:
    return db[Collection.APPOINTMENTS].count_documents({})
