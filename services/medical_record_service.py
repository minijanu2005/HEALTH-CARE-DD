"""Medical records (fictional clinical data)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from database import next_sequence
from models.constants import Collection
from permissions import PermissionDenied, can_create_medical_record, can_view_medical_records
from services.patient_service import get_patient
from utils.audit import log_audit
from utils.facility_meta import stamp_new_document
from utils.validators import ValidationError, parse_date, require_non_empty


def _format_record_id(seq: int) -> str:
    return f"REC-{seq:05d}"


def create_medical_record(
    db: Any,
    *,
    actor: dict[str, str],
    patient_id: str,
    doctor_id: str,
    diagnosis: str,
    prescription: str,
    visit_notes: str,
    visit_date: str | None = None,
    medical_history: str | None = None,
) -> dict[str, Any]:
    if not can_create_medical_record(actor["role"]):
        raise PermissionDenied("You cannot create medical records.")
    if not get_patient(db, patient_id):
        raise ValidationError("Patient not found.")
    seq = next_sequence(db, "medical_record")
    record_id = _format_record_id(seq)
    vdate = parse_date(visit_date or datetime.now(timezone.utc).date().isoformat(), "visit_date")
    doc = stamp_new_document(
        {
            "record_id": record_id,
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "visit_date": vdate.isoformat(),
            "diagnosis": require_non_empty(diagnosis, "diagnosis"),
            "prescription": require_non_empty(prescription, "prescription"),
            "visit_notes": require_non_empty(visit_notes, "visit_notes"),
            "medical_history": (medical_history or "").strip() or None,
            "created_by": actor["username"],
        }
    )
    db[Collection.MEDICAL_RECORDS].insert_one(doc)
    log_audit(
        db,
        actor_username=actor["username"],
        actor_role=actor["role"],
        action="create_medical_record",
        entity_type="medical_record",
        entity_id=record_id,
        details={"patient_id": patient_id, "doctor_id": doctor_id},
    )
    return doc


def list_records(
    db: Any,
    *,
    actor: dict[str, str],
    patient_id: str | None = None,
    doctor_id: str | None = None,
    query: str = "",
    limit: int = 50,
) -> list[dict[str, Any]]:
    if not can_view_medical_records(actor["role"]):
        raise PermissionDenied("You cannot view medical records.")
    mongo_query: dict[str, Any] = {}
    if patient_id:
        mongo_query["patient_id"] = patient_id.strip().upper()
    if doctor_id:
        mongo_query["doctor_id"] = doctor_id.strip().upper()
    q = query.strip()
    if q:
        regex = {"$regex": q, "$options": "i"}
        mongo_query["$or"] = [{"diagnosis": regex}, {"record_id": regex}, {"patient_id": regex}]
    return list(db[Collection.MEDICAL_RECORDS].find(mongo_query).sort("visit_date", -1).limit(limit))


def list_records_for_patient(db: Any, *, actor: dict[str, str], patient_id: str) -> list[dict[str, Any]]:
    return list_records(db, actor=actor, patient_id=patient_id)


def get_record(db: Any, *, actor: dict[str, str], record_id: str) -> dict[str, Any] | None:
    if not can_view_medical_records(actor["role"]):
        raise PermissionDenied("You cannot view medical records.")
    rec = db[Collection.MEDICAL_RECORDS].find_one({"record_id": record_id})
    if rec:
        log_audit(
            db,
            actor_username=actor["username"],
            actor_role=actor["role"],
            action="view_medical_record",
            entity_type="medical_record",
            entity_id=record_id,
        )
    return rec
