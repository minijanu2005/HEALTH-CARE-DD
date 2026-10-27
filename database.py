"""
MongoDB connection helpers (Phase 3).

This module connects PyMongo to the database defined in `.env`.
Schema and repositories are added in Phase 4.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import quote_plus, urlparse, urlunparse

from pymongo import MongoClient, ReturnDocument
from pymongo.database import Database
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError

from config import Settings, get_settings
from models.constants import Collection

# Default: fail fast in dev if MongoDB is not running (adjust in production if needed)
DEFAULT_SERVER_SELECTION_TIMEOUT_MS = 5_000

_shared_client: MongoClient[dict[str, Any]] | None = None


def build_mongodb_uri(settings: Settings) -> str:
    """
    Return a MongoDB URI, injecting username/password when set in the environment.

    Passwords stay in `.env` — never hard-code them here.
    """
    if not settings.mongodb_username or not settings.mongodb_password:
        return settings.mongodb_uri

    parsed = urlparse(settings.mongodb_uri)
    auth_source = settings.mongodb_auth_source or "admin"
    user = quote_plus(settings.mongodb_username)
    password = quote_plus(settings.mongodb_password)
    netloc = f"{user}:{password}@{parsed.hostname or '127.0.0.1'}"
    if parsed.port:
        netloc += f":{parsed.port}"

    return urlunparse(
        (
            parsed.scheme or "mongodb",
            netloc,
            parsed.path or "",
            parsed.params,
            parsed.query,
            parsed.fragment,
        )
    )


def get_mongo_client(
    settings: Settings | None = None,
    *,
    server_selection_timeout_ms: int = DEFAULT_SERVER_SELECTION_TIMEOUT_MS,
) -> MongoClient[dict[str, Any]]:
    """Create a new MongoClient. Caller should close it when finished."""
    settings = settings or get_settings()
    uri = build_mongodb_uri(settings)
    return MongoClient(uri, serverSelectionTimeoutMS=server_selection_timeout_ms)


def get_database(
    client: MongoClient[dict[str, Any]] | None = None,
    settings: Settings | None = None,
) -> Database[dict[str, Any]]:
    """Return the application database handle."""
    settings = settings or get_settings()
    if client is None:
        client = get_mongo_client(settings)
    return client[settings.mongodb_db_name]


def ping_mongodb(settings: Settings | None = None) -> dict[str, Any]:
    """
    Verify that MongoDB accepts connections.

    Returns:
        dict with keys: ok (bool), message (str), and optional server_version.

    Raises:
        Does not raise — connection problems are returned as ok=False.
    """
    settings = settings or get_settings()
    client: MongoClient[dict[str, Any]] | None = None
    try:
        client = get_mongo_client(settings)
        client.admin.command("ping")
        build_info = client.admin.command("buildInfo")
        return {
            "ok": True,
            "message": "MongoDB ping succeeded.",
            "server_version": build_info.get("version"),
            "database": settings.mongodb_db_name,
        }
    except ServerSelectionTimeoutError:
        return {
            "ok": False,
            "message": (
                "Could not reach MongoDB in time. Is mongod running on the host "
                "and port in MONGODB_URI?"
            ),
            "database": settings.mongodb_db_name,
        }
    except PyMongoError as exc:
        return {
            "ok": False,
            "message": f"MongoDB error: {exc}",
            "database": settings.mongodb_db_name,
        }
    finally:
        if client is not None:
            client.close()


def get_shared_client(
    settings: Settings | None = None,
) -> MongoClient[dict[str, Any]]:
    """Reuse one client for the app lifecycle (e.g. Streamlit session)."""
    global _shared_client
    if _shared_client is None:
        _shared_client = get_mongo_client(settings)
    return _shared_client


def get_shared_database(settings: Settings | None = None) -> Database[dict[str, Any]]:
    settings = settings or get_settings()
    return get_shared_client(settings)[settings.mongodb_db_name]


def ensure_indexes(db: Database[dict[str, Any]]) -> None:
    """Create indexes for uniqueness and query performance."""
    db[Collection.USERS].create_index("username", unique=True)
    db[Collection.PATIENTS].create_index("patient_id", unique=True)
    db[Collection.PATIENTS].create_index("full_name")
    db[Collection.DOCTORS].create_index("doctor_id", unique=True)
    db[Collection.APPOINTMENTS].create_index("appointment_id", unique=True)
    db[Collection.APPOINTMENTS].create_index([("doctor_id", 1), ("appointment_datetime", 1)])
    db[Collection.MEDICAL_RECORDS].create_index("record_id", unique=True)
    db[Collection.MEDICAL_RECORDS].create_index("patient_id")
    db[Collection.AUDIT_LOGS].create_index("timestamp")
    db[Collection.AUDIT_LOGS].create_index("action")
    db[Collection.PATIENTS].create_index("facility_id")
    db[Collection.SYNC_OUTBOX].create_index("status")
    db[Collection.SYNC_PROCESSED].create_index("message_id", unique=True)
    db[Collection.SYNC_LOG].create_index("timestamp")
    db[Collection.SYNC_CONFLICTS].create_index("timestamp")


def next_sequence(db: Database[dict[str, Any]], name: str) -> int:
    """Atomic counter for human-readable IDs (PAT-00001, etc.)."""
    doc = db[Collection.COUNTERS].find_one_and_update(
        {"_id": name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return int(doc["seq"])
