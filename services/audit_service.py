"""Audit log queries."""

from __future__ import annotations

from typing import Any

from models.constants import Collection
from permissions import PermissionDenied


def list_audit_logs(
    db: Any,
    *,
    actor_role: str,
    action: str | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    if actor_role != "Administrator":
        raise PermissionDenied("Only administrators can view audit logs.")
    query: dict[str, Any] = {}
    if action:
        query["action"] = action
    return list(db[Collection.AUDIT_LOGS].find(query).sort("timestamp", -1).limit(limit))
