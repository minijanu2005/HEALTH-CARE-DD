"""Aggregates for dashboard charts and summaries."""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Any

from models.constants import AppointmentStatus, Collection


def _today_bounds() -> tuple[datetime, datetime]:
    today = date.today()
    start = datetime.combine(today, time.min)
    end = datetime.combine(today, time.max)
    return start, end


def get_dashboard_stats(db: Any) -> dict[str, int]:
    start, end = _today_bounds()
    return {
        "patients": db[Collection.PATIENTS].count_documents({"active": {"$ne": False}}),
        "doctors": db[Collection.DOCTORS].count_documents({"active": True}),
        "appointments": db[Collection.APPOINTMENTS].count_documents({}),
        "records": db[Collection.MEDICAL_RECORDS].count_documents({}),
        "scheduled": db[Collection.APPOINTMENTS].count_documents(
            {"status": AppointmentStatus.SCHEDULED}
        ),
        "pending": db[Collection.APPOINTMENTS].count_documents(
            {"status": AppointmentStatus.SCHEDULED}
        ),
        "completed": db[Collection.APPOINTMENTS].count_documents(
            {"status": AppointmentStatus.COMPLETED}
        ),
        "cancelled": db[Collection.APPOINTMENTS].count_documents(
            {"status": AppointmentStatus.CANCELLED}
        ),
        "today": db[Collection.APPOINTMENTS].count_documents(
            {"appointment_datetime": {"$gte": start, "$lte": end}}
        ),
    }


def appointments_by_status(db: Any) -> dict[str, int]:
    pipeline = [{"$group": {"_id": "$status", "count": {"$sum": 1}}}]
    rows = db[Collection.APPOINTMENTS].aggregate(pipeline)
    return {str(row["_id"]): int(row["count"]) for row in rows}


def queue_status_distribution(db: Any) -> dict[str, int]:
    """Maps appointment statuses to queue-style labels for pie charts."""
    raw = appointments_by_status(db)
    return {
        "Waiting (Scheduled)": raw.get(AppointmentStatus.SCHEDULED, 0),
        "Completed": raw.get(AppointmentStatus.COMPLETED, 0),
        "Cancelled": raw.get(AppointmentStatus.CANCELLED, 0),
        "No-show": raw.get(AppointmentStatus.NO_SHOW, 0),
    }


def appointments_monthly(db: Any) -> list[dict[str, Any]]:
    pipeline = [
        {
            "$group": {
                "_id": {
                    "month": {"$dateToString": {"format": "%Y-%m", "date": "$appointment_datetime"}},
                    "status": "$status",
                },
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"_id.month": 1}},
    ]
    rows = list(db[Collection.APPOINTMENTS].aggregate(pipeline))
    out: list[dict[str, Any]] = []
    for r in rows:
        out.append(
            {
                "month": r["_id"]["month"],
                "status": str(r["_id"]["status"]),
                "count": int(r["count"]),
            }
        )
    return out


def doctor_appointment_share(db: Any, limit: int = 5) -> list[dict[str, Any]]:
    pipeline = [
        {"$group": {"_id": "$doctor_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit},
    ]
    result = []
    for row in db[Collection.APPOINTMENTS].aggregate(pipeline):
        doc = db[Collection.DOCTORS].find_one({"doctor_id": row["_id"]})
        result.append(
            {
                "doctor": doc["full_name"] if doc else row["_id"],
                "appointments": int(row["count"]),
            }
        )
    return result


def patient_registration_trend(db: Any) -> list[dict[str, Any]]:
    pipeline = [
        {
            "$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"_id": 1}},
    ]
    try:
        return [{"date": r["_id"], "registrations": r["count"]} for r in db[Collection.PATIENTS].aggregate(pipeline)]
    except Exception:
        return []


def recent_patients(db: Any, limit: int = 8) -> list[dict[str, Any]]:
    return list(
        db[Collection.PATIENTS]
        .find({"active": {"$ne": False}})
        .sort("created_at", -1)
        .limit(limit)
    )


def todays_appointments(db: Any, limit: int = 20) -> list[dict[str, Any]]:
    start, end = _today_bounds()
    return list(
        db[Collection.APPOINTMENTS]
        .find({"appointment_datetime": {"$gte": start, "$lte": end}})
        .sort("appointment_datetime", 1)
        .limit(limit)
    )


def upcoming_appointments(db: Any, limit: int = 8) -> list[dict[str, Any]]:
    now = datetime.combine(date.today(), time.min)
    return list(
        db[Collection.APPOINTMENTS]
        .find({"appointment_datetime": {"$gte": now}, "status": AppointmentStatus.SCHEDULED})
        .sort("appointment_datetime", 1)
        .limit(limit)
    )


def recent_medical_records(db: Any, limit: int = 8) -> list[dict[str, Any]]:
    return list(db[Collection.MEDICAL_RECORDS].find().sort("created_at", -1).limit(limit))


def recent_audit_logs(db: Any, limit: int = 8) -> list[dict[str, Any]]:
    return list(db[Collection.AUDIT_LOGS].find().sort("timestamp", -1).limit(limit))
