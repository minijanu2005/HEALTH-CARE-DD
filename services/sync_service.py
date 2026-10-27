"""Multi-facility sync: outbox, idempotency, conflicts, retries."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

import requests

from config import get_settings
from models.constants import Collection, SyncStatus


def _now() -> datetime:
    return datetime.now(timezone.utc)


def queue_entity_sync(
    db: Any,
    *,
    entity_type: str,
    entity_id: str,
    payload: dict[str, Any],
) -> None:
    settings = get_settings()
    db[Collection.SYNC_OUTBOX].insert_one(
        {
            "message_id": str(uuid.uuid4()),
            "entity_type": entity_type,
            "entity_id": entity_id,
            "source_facility_id": settings.facility_id,
            "payload": payload,
            "version": payload.get("version", 1),
            "updated_at": payload.get("updated_at", _now()),
            "status": SyncStatus.PENDING,
            "attempts": 0,
            "created_at": _now(),
        }
    )


def _log_sync(
    db: Any,
    *,
    direction: str,
    status: str,
    message_id: str,
    entity_type: str,
    entity_id: str,
    detail: str,
    peer: str | None = None,
) -> None:
    db[Collection.SYNC_LOG].insert_one(
        {
            "timestamp": _now(),
            "direction": direction,
            "status": status,
            "message_id": message_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "peer": peer,
            "detail": detail,
        }
    )


def receive_sync_message(db: Any, message: dict[str, Any]) -> dict[str, Any]:
    """Apply inbound sync with idempotency and conflict detection."""
    settings = get_settings()
    message_id = message.get("message_id")
    if not message_id:
        return {"ok": False, "error": "message_id required"}

    if db[Collection.SYNC_PROCESSED].find_one({"message_id": message_id}):
        return {"ok": True, "duplicate": True}

    entity_type = message.get("entity_type")
    entity_id = message.get("entity_id")
    payload = message.get("payload") or {}
    incoming_version = int(message.get("version", 1))
    source_facility = message.get("source_facility_id", "UNKNOWN")

    if source_facility == settings.facility_id:
        db[Collection.SYNC_PROCESSED].insert_one({"message_id": message_id, "at": _now()})
        return {"ok": True, "skipped": "same_facility"}

    collection_map = {
        "patient": Collection.PATIENTS,
        "doctor": Collection.DOCTORS,
        "appointment": Collection.APPOINTMENTS,
        "medical_record": Collection.MEDICAL_RECORDS,
    }
    collection = collection_map.get(str(entity_type))
    if not collection:
        return {"ok": False, "error": "unsupported entity_type"}

    id_field = {
        Collection.PATIENTS: "patient_id",
        Collection.DOCTORS: "doctor_id",
        Collection.APPOINTMENTS: "appointment_id",
        Collection.MEDICAL_RECORDS: "record_id",
    }[collection]

    local = db[collection].find_one({id_field: entity_id})
    if local:
        local_version = int(local.get("version", 1))
        local_updated = local.get("updated_at")
        incoming_updated = payload.get("updated_at", message.get("updated_at"))
        if local_version > incoming_version:
            db[Collection.SYNC_CONFLICTS].insert_one(
                {
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "local_version": local_version,
                    "incoming_version": incoming_version,
                    "resolution": "kept_local",
                    "timestamp": _now(),
                    "source_facility_id": source_facility,
                }
            )
            _log_sync(
                db,
                direction="inbound",
                status=SyncStatus.CONFLICT,
                message_id=message_id,
                entity_type=str(entity_type),
                entity_id=str(entity_id),
                detail="Local version newer; kept local copy.",
            )
            db[Collection.SYNC_PROCESSED].insert_one({"message_id": message_id, "at": _now()})
            return {"ok": True, "conflict": True}

        if local_version == incoming_version and local_updated == incoming_updated:
            db[Collection.SYNC_PROCESSED].insert_one({"message_id": message_id, "at": _now()})
            return {"ok": True, "unchanged": True}

    payload["source_facility_id"] = source_facility
    payload["version"] = incoming_version
    db[collection].update_one({id_field: entity_id}, {"$set": payload}, upsert=True)
    db[Collection.SYNC_PROCESSED].insert_one({"message_id": message_id, "at": _now()})
    _log_sync(
        db,
        direction="inbound",
        status=SyncStatus.SUCCESS,
        message_id=message_id,
        entity_type=str(entity_type),
        entity_id=str(entity_id),
        detail="Applied inbound sync.",
    )
    return {"ok": True}


def push_pending_to_peers(db: Any) -> dict[str, int]:
    settings = get_settings()
    stats = {"sent": 0, "failed": 0, "skipped": 0}
    if not settings.sync_peer_urls:
        return stats

    pending = list(
        db[Collection.SYNC_OUTBOX].find({"status": SyncStatus.PENDING}).sort("created_at", 1).limit(50)
    )
    headers = {"X-Sync-Api-Key": settings.sync_api_key, "Content-Type": "application/json"}

    for item in pending:
        body = {
            "message_id": item["message_id"],
            "entity_type": item["entity_type"],
            "entity_id": item["entity_id"],
            "source_facility_id": item["source_facility_id"],
            "version": item["version"],
            "updated_at": item["updated_at"].isoformat()
            if hasattr(item["updated_at"], "isoformat")
            else str(item["updated_at"]),
            "payload": item["payload"],
        }
        success = False
        for peer in settings.sync_peer_urls:
            try:
                resp = requests.post(
                    f"{peer}/sync/receive",
                    json=body,
                    headers=headers,
                    timeout=8,
                )
                if resp.status_code == 200:
                    success = True
                    _log_sync(
                        db,
                        direction="outbound",
                        status=SyncStatus.SUCCESS,
                        message_id=item["message_id"],
                        entity_type=item["entity_type"],
                        entity_id=item["entity_id"],
                        detail="Delivered to peer.",
                        peer=peer,
                    )
                else:
                    _log_sync(
                        db,
                        direction="outbound",
                        status=SyncStatus.FAILED,
                        message_id=item["message_id"],
                        entity_type=item["entity_type"],
                        entity_id=item["entity_id"],
                        detail=f"HTTP {resp.status_code}",
                        peer=peer,
                    )
            except requests.RequestException as exc:
                _log_sync(
                    db,
                    direction="outbound",
                    status=SyncStatus.FAILED,
                    message_id=item["message_id"],
                    entity_type=item["entity_type"],
                    entity_id=item["entity_id"],
                    detail=str(exc)[:200],
                    peer=peer,
                )

        if success:
            db[Collection.SYNC_OUTBOX].update_one(
                {"_id": item["_id"]},
                {"$set": {"status": SyncStatus.SUCCESS, "synced_at": _now()}},
            )
            stats["sent"] += 1
        else:
            db[Collection.SYNC_OUTBOX].update_one(
                {"_id": item["_id"]},
                {"$inc": {"attempts": 1}, "$set": {"last_error_at": _now()}},
            )
            stats["failed"] += 1

    return stats


def get_sync_dashboard(db: Any) -> dict[str, int]:
    return {
        "pending": db[Collection.SYNC_OUTBOX].count_documents({"status": SyncStatus.PENDING}),
        "conflicts": db[Collection.SYNC_CONFLICTS].count_documents({}),
        "processed": db[Collection.SYNC_PROCESSED].count_documents({}),
    }
