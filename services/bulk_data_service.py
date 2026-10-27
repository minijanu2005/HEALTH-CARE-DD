"""Generate and import fictional bulk dataset for demos (college presentation)."""

from __future__ import annotations

import csv
import io
import random
from datetime import date, datetime, timedelta, timezone
from typing import Any

from config import get_settings
from database import next_sequence
from models.constants import AppointmentStatus, Collection, Role
from utils.facility_meta import stamp_new_document
from utils.validators import ValidationError, optional_email, optional_phone, parse_date, require_non_empty

FIRST = [
    "Aarav", "Priya", "Rohan", "Ananya", "Vikram", "Neha", "Arjun", "Kavya", "Ishaan", "Meera",
    "Aditya", "Sana", "Dev", "Lina", "Omar", "Elena", "Noah", "Mia", "Ethan", "Zara",
]
LAST = [
    "Sharma", "Patel", "Singh", "Khan", "Reddy", "Gupta", "Das", "Mehta", "Roy", "Nair",
    "Johnson", "Williams", "Brown", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin",
]
SPECIALTIES = [
    "General Practice", "Cardiology", "Pediatrics", "Orthopedics", "Dermatology",
    "Neurology", "Gynecology", "ENT", "Oncology", "Psychiatry",
]
DIAGNOSES = [
    "Seasonal allergy (fictional)", "Hypertension follow-up (fictional)", "Routine wellness (fictional)",
    "Migraine assessment (fictional)", "Type 2 diabetes review (fictional)", "Anxiety check-in (fictional)",
]
GENDERS = ["Female", "Male", "Non-binary", "Prefer not to say"]


def _rand_dob() -> str:
    start = date(1955, 1, 1)
    end = date(2010, 12, 31)
    days = (end - start).days
    return (start + timedelta(days=random.randint(0, days))).isoformat()


def _format_patient_id(seq: int) -> str:
    return f"PAT-{seq:05d}"


def _format_doctor_id(seq: int) -> str:
    return f"DOC-{seq:03d}"


def _format_apt_id(seq: int) -> str:
    return f"APT-{seq:05d}"


def _format_rec_id(seq: int) -> str:
    return f"REC-{seq:05d}"


def count_active_patients(db: Any) -> int:
    return db[Collection.PATIENTS].count_documents({"active": {"$ne": False}})


def generate_fictional_dataset(
    db: Any,
    *,
    target_patients: int = 50,
    actor: dict[str, str] | None = None,
) -> dict[str, int]:
    """
    Idempotent: only adds records until at least `target_patients` active patients exist.
    Does not delete existing data.
    """
    actor = actor or {"username": "admin", "role": Role.ADMINISTRATOR}
    settings = get_settings()
    stats = {"patients_added": 0, "doctors_added": 0, "appointments_added": 0, "records_added": 0}

    existing_patients = count_active_patients(db)
    doctor_count = db[Collection.DOCTORS].count_documents({"active": True})

    # Doctors — aim for at least 8
    while doctor_count < 8:
        seq = next_sequence(db, "doctor")
        doc = stamp_new_document(
            {
                "doctor_id": _format_doctor_id(seq),
                "full_name": f"Dr. {random.choice(FIRST)} {random.choice(LAST)}",
                "specialty": random.choice(SPECIALTIES),
                "phone": f"+1 555 {random.randint(1000,9999)}",
                "email": f"doctor{seq}@demo-clinic.test",
            }
        )
        db[Collection.DOCTORS].insert_one(doc)
        doctor_count += 1
        stats["doctors_added"] += 1

    doctors = list(db[Collection.DOCTORS].find({"active": True}))
    patients_to_add = max(0, target_patients - existing_patients)

    for _ in range(patients_to_add):
        seq = next_sequence(db, "patient")
        pid = _format_patient_id(seq)
        created = datetime.now(timezone.utc) - timedelta(days=random.randint(0, 180))
        doc = stamp_new_document(
            {
                "patient_id": pid,
                "full_name": f"{random.choice(FIRST)} {random.choice(LAST)}",
                "date_of_birth": _rand_dob(),
                "gender": random.choice(GENDERS),
                "phone": f"+1 555 {random.randint(1000,9999)}",
                "email": f"patient{seq}@example.test",
                "address": f"{random.randint(1,999)} Demo Avenue, {settings.facility_name}",
            }
        )
        doc["created_at"] = created
        doc["updated_at"] = created
        db[Collection.PATIENTS].insert_one(doc)
        stats["patients_added"] += 1

    all_patients = list(db[Collection.PATIENTS].find({"active": {"$ne": False}}))
    apt_count = db[Collection.APPOINTMENTS].count_documents({})
    target_apts = max(apt_count, len(all_patients) * 2)

    statuses = [
        AppointmentStatus.SCHEDULED,
        AppointmentStatus.COMPLETED,
        AppointmentStatus.CANCELLED,
        AppointmentStatus.NO_SHOW,
    ]
    while db[Collection.APPOINTMENTS].count_documents({}) < target_apts:
        seq = next_sequence(db, "appointment")
        patient = random.choice(all_patients)
        doctor = random.choice(doctors)
        days_offset = random.randint(-30, 45)
        hour = random.choice([9, 10, 11, 14, 15, 16, 17])
        appt_dt = datetime.combine(date.today(), datetime.min.time()) + timedelta(days=days_offset, hours=hour)
        status = random.choices(
            statuses,
            weights=[35, 45, 12, 8],
            k=1,
        )[0]
        if appt_dt.date() < date.today():
            status = random.choice([AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED, AppointmentStatus.NO_SHOW])
        doc = stamp_new_document(
            {
                "appointment_id": _format_apt_id(seq),
                "patient_id": patient["patient_id"],
                "doctor_id": doctor["doctor_id"],
                "appointment_datetime": appt_dt,
                "status": status,
                "notes": "Fictional visit — demo data",
            }
        )
        db[Collection.APPOINTMENTS].insert_one(doc)
        stats["appointments_added"] += 1

    rec_count = db[Collection.MEDICAL_RECORDS].count_documents({})
    target_recs = max(rec_count, int(len(all_patients) * 0.8))
    while db[Collection.MEDICAL_RECORDS].count_documents({}) < target_recs:
        seq = next_sequence(db, "medical_record")
        patient = random.choice(all_patients)
        doctor = random.choice(doctors)
        visit = date.today() - timedelta(days=random.randint(0, 120))
        doc = stamp_new_document(
            {
                "record_id": _format_rec_id(seq),
                "patient_id": patient["patient_id"],
                "doctor_id": doctor["doctor_id"],
                "visit_date": visit.isoformat(),
                "diagnosis": random.choice(DIAGNOSES),
                "prescription": "Demo prescription — not real medical advice",
                "visit_notes": "Fictional consultation notes for academic demo.",
                "medical_history": "Synthetic history for demonstration only.",
                "created_by": actor["username"],
            }
        )
        db[Collection.MEDICAL_RECORDS].insert_one(doc)
        stats["records_added"] += 1

    return stats


def import_patients_csv(
    db: Any,
    *,
    actor: dict[str, str],
    csv_text: str,
) -> dict[str, int]:
    if actor.get("role") not in {Role.ADMINISTRATOR, Role.RECEPTIONIST}:
        raise ValidationError("You do not have permission to import patients.")
    reader = csv.DictReader(io.StringIO(csv_text))
    if not reader.fieldnames or "full_name" not in reader.fieldnames:
        raise ValidationError("CSV must include a full_name column.")

    imported = 0
    skipped = 0
    for row in reader:
        try:
            name = require_non_empty(row.get("full_name"), "full_name")
            dob = parse_date(row.get("date_of_birth") or "1990-01-01", "date_of_birth")
            gender = require_non_empty(row.get("gender") or "Prefer not to say", "gender")
            seq = next_sequence(db, "patient")
            pid = _format_patient_id(seq)
            doc = stamp_new_document(
                {
                    "patient_id": pid,
                    "full_name": name,
                    "date_of_birth": dob.isoformat(),
                    "gender": gender,
                    "phone": optional_phone(row.get("phone")),
                    "email": optional_email(row.get("email")),
                    "address": (row.get("address") or "").strip() or None,
                }
            )
            db[Collection.PATIENTS].insert_one(doc)
            imported += 1
        except ValidationError:
            skipped += 1
    return {"imported": imported, "skipped": skipped}
