"""Lightweight facility sync API (run per demo node)."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

from config import get_settings
from database import ensure_indexes, get_shared_database
from services.migration_service import apply_safe_migrations
from services.sync_service import receive_sync_message

app = FastAPI(title="Healthcare Facility Sync API", version="1.0.0")


class SyncMessage(BaseModel):
    message_id: str
    entity_type: str
    entity_id: str
    source_facility_id: str
    version: int
    updated_at: str
    payload: dict[str, Any]


@app.on_event("startup")
def _startup() -> None:
    db = get_shared_database()
    ensure_indexes(db)
    apply_safe_migrations(db)


@app.get("/health")
def health() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "facility_id": settings.facility_id,
        "facility_name": settings.facility_name,
    }


@app.post("/sync/receive")
def sync_receive(
    message: SyncMessage,
    x_sync_api_key: str | None = Header(default=None),
) -> dict[str, Any]:
    settings = get_settings()
    if x_sync_api_key != settings.sync_api_key:
        raise HTTPException(status_code=401, detail="Invalid sync API key")
    db = get_shared_database()
    result = receive_sync_message(db, message.model_dump())
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("error", "sync failed"))
    return result
