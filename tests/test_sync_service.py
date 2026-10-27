"""Sync service unit tests (in-memory style with live MongoDB when enabled)."""

from __future__ import annotations

import os
import uuid

import pytest

from services.sync_service import receive_sync_message


@pytest.mark.integration
def test_sync_idempotency() -> None:
    if os.getenv("INTEGRATION_TESTS") != "1":
        pytest.skip("Set INTEGRATION_TESTS=1 for MongoDB integration tests.")

    from database import get_shared_database

    db = get_shared_database()
    message_id = str(uuid.uuid4())
    message = {
        "message_id": message_id,
        "entity_type": "patient",
        "entity_id": "PAT-SYNC-TEST",
        "source_facility_id": "REMOTE-FAC",
        "version": 1,
        "updated_at": "2026-01-01T00:00:00",
        "payload": {
            "patient_id": "PAT-SYNC-TEST",
            "full_name": "Sync Test Patient",
            "date_of_birth": "1990-01-01",
            "gender": "Female",
            "version": 1,
            "facility_id": "REMOTE-FAC",
            "active": True,
        },
    }
    first = receive_sync_message(db, message)
    second = receive_sync_message(db, message)
    assert first.get("ok") is True
    assert second.get("duplicate") is True
