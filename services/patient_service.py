"""Patient registration and management."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from database import next_sequence
from models.constants import Collection
from permissions import PermissionDenied, can_delete_patient, can_edit_patient
from services.sync_service import queue_entity_sync
from utils.audit import log_audit
from utils.facility_meta import bump_version, stamp_new_document
from utils.validators import (
    ValidationError,
    optional_email,
    optional_phone,
    parse_date,
    require_non_empty,
)


def _format_patient_id(seq: int) -> str:
    return f"PAT-{seq:05d}"


def _serialize_patient(doc: dict[str, Any]) -> dict[str, Any]:
    out = dict(doc)
    if "_id" in out:
        out["_id"] = str(out["_id"])
    for key in ("created_at", "updated_at"):
        if key in out and hasattr(out[key], "isoformat"):
            out[key] = out[key].isoformat()
    return out


def create_patient(
    db: Any,
    *,
    actor: dict[str, str],
    full_name: str,
    date_of_birth: str,
    gender: str,
    phone: str | None = None,
    email: str | None = None,
    address: str | None = None,
) -> dict[str, Any]:
    if not can_edit_patient(actor["role"]):
        raise PermissionDenied("You cannot register patients.")
    name = require_non_empty(full_name, "full_name")
    dob = parse_date(date_of_birth, "date_of_birth")
    gender_clean = require_non_empty(gender, "gender")
    seq = next_sequence(db, "patient")
    patient_id = _format_patient_id(seq)
    doc = stamp_new_document(
        {
            "patient_id": patient_id,
            "full_name": name,
            "date_of_birth": dob.isoformat(),
            "gender": gender_clean,
            "phone": optional_phone(phone),
            "email": optional_email(email),
            "address": (address or "").strip() or None,
        }
    )
    db[Collection.PATIENTS].insert_one(doc)
    log_audit(
        db,
        actor_username=actor["username"],
        actor_role=actor["role"],
        action="create_patient",
        entity_type="patient",
        entity_id=patient_id,
    )
    queue_entity_sync(
        db,
        entity_type="patient",
        entity_id=patient_id,
        payload=_serialize_patient(doc),
    )
    return doc


def get_patient(db: Any, patient_id: str) -> dict[str, Any] | None:
    return db[Collection.PATIENTS].find_one({"patient_id": patient_id, "active": {"$ne": False}})


def list_patients(
    db: Any,
    *,
    query: str = "",
    active_only: bool = True,
    skip: int = 0,
    limit: int = 50,
) -> list[dict[str, Any]]:
    mongo_query: dict[str, Any] = {}
    if active_only:
        mongo_query["active"] = {"$ne": False}
    q = query.strip()
    if q:
        if q.upper().startswith("PAT-"):
            mongo_query["patient_id"] = q.upper()
        else:
            regex = {"$regex": q, "$options": "i"}
            mongo_query["$or"] = [{"full_name": regex}, {"patient_id": regex}]
    return list(
        db[Collection.PATIENTS].find(mongo_query).sort("full_name", 1).skip(skip).limit(limit)
    )


def search_patients(db: Any, query: str, limit: int = 50) -> list[dict[str, Any]]:
    return list_patients(db, query=query, limit=limit)


def update_patient(
    db: Any,
    *,
    actor: dict[str, str],
    patient_id: str,
    full_name: str | None = None,
    date_of_birth: str | None = None,
    gender: str | None = None,
    phone: str | None = None,
    email: str | None = None,
    address: str | None = None,
) -> dict[str, Any]:
    if not can_edit_patient(actor["role"]):
        raise PermissionDenied("You cannot update patients.")
    existing = db[Collection.PATIENTS].find_one({"patient_id": patient_id})
    if not existing:
        raise ValidationError("Patient not found.")
    updates: dict[str, Any] = bump_version(existing)
    if full_name is not None:
        updates["full_name"] = require_non_empty(full_name, "full_name")
    if date_of_birth is not None:
        updates["date_of_birth"] = parse_date(date_of_birth, "date_of_birth").isoformat()
    if gender is not None:
        updates["gender"] = require_non_empty(gender, "gender")
    if phone is not None:
        updates["phone"] = optional_phone(phone)
    if email is not None:
        updates["email"] = optional_email(email)
    if address is not None:
        updates["address"] = address.strip() or None

    db[Collection.PATIENTS].update_one({"patient_id": patient_id}, {"$set": updates})
    log_audit(
        db,
        actor_username=actor["username"],
        actor_role=actor["role"],
        action="update_patient",
        entity_type="patient",
        entity_id=patient_id,
        details={"fields": list(updates.keys())},
    )
    updated = get_patient(db, patient_id) or existing | updates
    queue_entity_sync(
        db,
        entity_type="patient",
        entity_id=patient_id,
        payload=_serialize_patient(updated),
    )
    return updated  # type: ignore[return-value]


def deactivate_patient(db: Any, *, actor: dict[str, str], patient_id: str) -> None:
    if not can_edit_patient(actor["role"]):
        raise PermissionDenied("You cannot deactivate patients.")
    existing = db[Collection.PATIENTS].find_one({"patient_id": patient_id})
    if not existing:
        raise ValidationError("Patient not found.")
    updates = bump_version(existing)
    updates["active"] = False
    db[Collection.PATIENTS].update_one({"patient_id": patient_id}, {"$set": updates})
    log_audit(
        db,
        actor_username=actor["username"],
        actor_role=actor["role"],
        action="deactivate_patient",
        entity_type="patient",
        entity_id=patient_id,
    )


def delete_patient(db: Any, *, actor: dict[str, str], patient_id: str) -> None:
    if not can_delete_patient(actor["role"]):
        raise PermissionDenied("Only administrators can delete patients.")
    result = db[Collection.PATIENTS].delete_one({"patient_id": patient_id})
    if result.deleted_count == 0:
        raise ValidationError("Patient not found.")
    log_audit(
        db,
        actor_username=actor["username"],
        actor_role=actor["role"],
        action="delete_patient",
        entity_type="patient",
        entity_id=patient_id,
    )


def count_patients(db: Any, active_only: bool = True) -> int:
    q: dict[str, Any] = {}
    if active_only:
        q["active"] = {"$ne": False}
    return db[Collection.PATIENTS].count_documents(q)
