"""Audit logging for important actions (no secrets)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from models.constants import Collection


def log_audit(
    db: Any,
    *,
    actor_username: str,
    actor_role: str,
    action: str,
    entity_type: str,
    entity_id: str,
    details: dict[str, Any] | None = None,
) -> None:
    db[Collection.AUDIT_LOGS].insert_one(
        {
            "timestamp": datetime.now(timezone.utc),
            "actor_username": actor_username,
            "actor_role": actor_role,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "details": details or {},
        }
    )
