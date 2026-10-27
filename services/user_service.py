"""User accounts and authentication."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from auth import hash_password, verify_password
from models.constants import Collection, Role
from permissions import PermissionDenied, can_manage_users
from utils.audit import log_audit
from utils.validators import ValidationError, require_non_empty


def count_users(db: Any) -> int:
    return db[Collection.USERS].count_documents({})


def list_users(db: Any) -> list[dict[str, Any]]:
    return list(db[Collection.USERS].find().sort("username", 1))


def find_by_username(db: Any, username: str, *, include_inactive: bool = False) -> dict[str, Any] | None:
    query: dict[str, Any] = {"username": username.lower()}
    if not include_inactive:
        query["active"] = True
    return db[Collection.USERS].find_one(query)


def authenticate(db: Any, username: str, password: str) -> dict[str, Any] | None:
    clean = (username or "").strip().lower()
    user = find_by_username(db, clean, include_inactive=True)
    if not user or not user.get("active", True):
        log_audit(
            db,
            actor_username=clean or "unknown",
            actor_role="—",
            action="login_failed",
            entity_type="user",
            entity_id=clean or "unknown",
            details={"reason": "invalid_credentials"},
        )
        return None
    if not verify_password(user["password_hash"], password):
        log_audit(
            db,
            actor_username=username.lower(),
            actor_role=user.get("role", "—"),
            action="login_failed",
            entity_type="user",
            entity_id=username.lower(),
            details={"reason": "invalid_password"},
        )
        return None
    log_audit(
        db,
        actor_username=user["username"],
        actor_role=user["role"],
        action="login_success",
        entity_type="user",
        entity_id=user["username"],
    )
    return user


def create_user(
    db: Any,
    *,
    actor: dict[str, str],
    username: str,
    password: str,
    role: str,
    full_name: str,
) -> dict[str, Any]:
    if not can_manage_users(actor["role"]):
        raise PermissionDenied("Only administrators can create users.")
    username_clean = require_non_empty(username, "username").lower()
    password_clean = require_non_empty(password, "password")
    full_name_clean = require_non_empty(full_name, "full_name")
    if len(password_clean) < 8:
        raise ValidationError("Password must be at least 8 characters.")
    try:
        Role(role)
    except ValueError as exc:
        raise ValidationError("Invalid role.") from exc
    if db[Collection.USERS].find_one({"username": username_clean}):
        raise ValidationError("Username already exists.")

    doc = {
        "username": username_clean,
        "password_hash": hash_password(password_clean),
        "role": role,
        "full_name": full_name_clean,
        "active": True,
        "created_at": datetime.now(timezone.utc),
    }
    db[Collection.USERS].insert_one(doc)
    log_audit(
        db,
        actor_username=actor["username"],
        actor_role=actor["role"],
        action="create_user",
        entity_type="user",
        entity_id=username_clean,
        details={"role": role},
    )
    return doc


def set_user_active(
    db: Any,
    *,
    actor: dict[str, str],
    username: str,
    active: bool,
) -> None:
    if not can_manage_users(actor["role"]):
        raise PermissionDenied("Only administrators can change user status.")
    username_clean = username.lower()
    result = db[Collection.USERS].update_one(
        {"username": username_clean},
        {"$set": {"active": active, "updated_at": datetime.now(timezone.utc)}},
    )
    if result.matched_count == 0:
        raise ValidationError("User not found.")
    log_audit(
        db,
        actor_username=actor["username"],
        actor_role=actor["role"],
        action="user_activate" if active else "user_deactivate",
        entity_type="user",
        entity_id=username_clean,
    )


def bootstrap_admin_from_env(db: Any) -> str | None:
    if count_users(db) > 0:
        return None
    username = os.getenv("ADMIN_BOOTSTRAP_USERNAME", "").strip()
    password = os.getenv("ADMIN_BOOTSTRAP_PASSWORD", "").strip()
    if not username or not password:
        return "No users found. Set ADMIN_BOOTSTRAP_USERNAME/PASSWORD or run scripts/seed_demo_data.py"
    doc = {
        "username": username.lower(),
        "password_hash": hash_password(password),
        "role": Role.ADMINISTRATOR,
        "full_name": "System Administrator",
        "active": True,
        "created_at": datetime.now(timezone.utc),
    }
    db[Collection.USERS].insert_one(doc)
    return None
