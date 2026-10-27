"""MongoDB connection tests (Phase 3)."""

from __future__ import annotations

import os

import pytest
from pymongo.errors import ServerSelectionTimeoutError

from config import Settings
from database import build_mongodb_uri, get_mongo_client, ping_mongodb


def _settings(**overrides: object) -> Settings:
    base = {
        "mongodb_uri": "mongodb://127.0.0.1:27017/?directConnection=true",
        "mongodb_db_name": "healthcare_dev",
        "app_env": "development",
        "log_level": "INFO",
        "mongodb_username": None,
        "mongodb_password": None,
        "mongodb_auth_source": "admin",
        "facility_id": "TEST",
        "facility_name": "Test Facility",
        "sync_api_key": "test-key",
        "sync_peer_urls": (),
        "sync_api_port": 8100,
        "session_timeout_minutes": 60,
    }
    base.update(overrides)
    return Settings(**base)  # type: ignore[arg-type]


def test_build_mongodb_uri_without_credentials() -> None:
    settings = _settings()
    assert build_mongodb_uri(settings) == settings.mongodb_uri


def test_build_mongodb_uri_with_credentials() -> None:
    settings = _settings(mongodb_username="app_user", mongodb_password="p@ss:word")
    uri = build_mongodb_uri(settings)
    assert "app_user" in uri
    assert "p%40ss%3Aword" in uri


@pytest.mark.integration
def test_ping_mongodb_when_server_running() -> None:
    """Runs only when INTEGRATION_TESTS=1 and MongoDB is reachable."""
    if os.getenv("INTEGRATION_TESTS") != "1":
        pytest.skip("Set INTEGRATION_TESTS=1 to run live MongoDB tests.")

    result = ping_mongodb()
    if not result["ok"]:
        pytest.skip(result["message"])
    assert result["ok"] is True
    assert result.get("server_version")


def test_get_mongo_client_raises_clearly_when_down(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MONGODB_URI", "mongodb://127.0.0.1:59999/?directConnection=true")
    monkeypatch.setenv("MONGODB_DB_NAME", "healthcare_dev")

    client = get_mongo_client(server_selection_timeout_ms=500)
    try:
        with pytest.raises(ServerSelectionTimeoutError):
            client.admin.command("ping")
    finally:
        client.close()
