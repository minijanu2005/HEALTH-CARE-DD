"""
Application configuration loaded from environment variables.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")


def _env(key: str, default: str | None = None) -> str | None:
    value = os.getenv(key, default)
    if value is None:
        return None
    stripped = value.strip()
    return stripped if stripped else None


def _env_int(key: str, default: int) -> int:
    raw = _env(key)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    mongodb_uri: str
    mongodb_db_name: str
    app_env: str
    log_level: str
    mongodb_username: str | None
    mongodb_password: str | None
    mongodb_auth_source: str | None
    facility_id: str
    facility_name: str
    sync_api_key: str
    sync_peer_urls: tuple[str, ...]
    sync_api_port: int
    session_timeout_minutes: int

    @property
    def is_development(self) -> bool:
        return self.app_env.lower() in {"development", "dev", "local"}


def get_settings() -> Settings:
    mongodb_uri = _env("MONGODB_URI")
    mongodb_db_name = _env("MONGODB_DB_NAME")

    if not mongodb_uri:
        raise ValueError(
            "MONGODB_URI is not set. Copy .env.example to .env and configure MongoDB."
        )
    if not mongodb_db_name:
        raise ValueError(
            "MONGODB_DB_NAME is not set. Copy .env.example to .env and set a database name."
        )

    peers_raw = _env("SYNC_PEER_URLS", "") or ""
    peers = tuple(u.strip().rstrip("/") for u in peers_raw.split(",") if u.strip())

    sync_key = _env("SYNC_API_KEY", "dev-sync-key-change-in-production") or ""

    return Settings(
        mongodb_uri=mongodb_uri,
        mongodb_db_name=mongodb_db_name,
        app_env=_env("APP_ENV", "development") or "development",
        log_level=_env("LOG_LEVEL", "INFO") or "INFO",
        mongodb_username=_env("MONGODB_USERNAME"),
        mongodb_password=_env("MONGODB_PASSWORD"),
        mongodb_auth_source=_env("MONGODB_AUTH_SOURCE", "admin"),
        facility_id=_env("FACILITY_ID", "HQ-MAIN") or "HQ-MAIN",
        facility_name=_env("FACILITY_NAME", "Main Campus") or "Main Campus",
        sync_api_key=sync_key,
        sync_peer_urls=peers,
        sync_api_port=_env_int("SYNC_API_PORT", 8100),
        session_timeout_minutes=_env_int("SESSION_TIMEOUT_MINUTES", 480),
    )
