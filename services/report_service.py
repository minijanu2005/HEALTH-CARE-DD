"""Reporting and CSV export helpers."""

from __future__ import annotations

import csv
import io
from datetime import datetime
from typing import Any

from models.constants import AppointmentStatus, Collection


def patient_summary(db: Any) -> dict[str, int]:
    return {
        "total": db[Collection.PATIENTS].count_documents({}),
        "active": db[Collection.PATIENTS].count_documents({"active": {"$ne": False}}),
        "inactive": db[Collection.PATIENTS].count_documents({"active": False}),
    }


def appointment_summary(db: Any, start: datetime | None = None, end: datetime | None = None) -> dict[str, int]:
    query: dict[str, Any] = {}
    if start and end:
        query["appointment_datetime"] = {"$gte": start, "$lte": end}
    base = db[Collection.APPOINTMENTS].count_documents(query)
    by_status = {}
    for status in AppointmentStatus:
        q = dict(query)
        q["status"] = status
        by_status[status.value] = db[Collection.APPOINTMENTS].count_documents(q)
    return {"total": base, **by_status}


def doctor_workload(db: Any) -> list[dict[str, Any]]:
    pipeline = [
        {"$match": {"status": {"$ne": AppointmentStatus.CANCELLED}}},
        {"$group": {"_id": "$doctor_id", "appointments": {"$sum": 1}}},
        {"$sort": {"appointments": -1}},
    ]
    rows = list(db[Collection.APPOINTMENTS].aggregate(pipeline))
    out = []
    for row in rows:
        doc = db[Collection.DOCTORS].find_one({"doctor_id": row["_id"]})
        out.append(
            {
                "doctor_id": row["_id"],
                "doctor_name": doc["full_name"] if doc else row["_id"],
                "appointments": row["appointments"],
            }
        )
    return out


def patients_to_csv(db: Any) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["patient_id", "full_name", "date_of_birth", "gender", "facility_id", "active"])
    for p in db[Collection.PATIENTS].find().sort("patient_id", 1):
        writer.writerow(
            [
                p.get("patient_id"),
                p.get("full_name"),
                p.get("date_of_birth"),
                p.get("gender"),
                p.get("facility_id"),
                p.get("active", True),
            ]
        )
    return buf.getvalue()
