"""Tests for configuration loading (Phase 2)."""

import os

import pytest

from config import get_settings


def test_get_settings_reads_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MONGODB_URI", "mongodb://127.0.0.1:27017")
    monkeypatch.setenv("MONGODB_DB_NAME", "test_healthcare")

    settings = get_settings()

    assert settings.mongodb_uri == "mongodb://127.0.0.1:27017"
    assert settings.mongodb_db_name == "test_healthcare"
    assert settings.is_development is True


def test_get_settings_missing_uri_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MONGODB_URI", raising=False)
    monkeypatch.setenv("MONGODB_DB_NAME", "test_healthcare")

    with pytest.raises(ValueError, match="MONGODB_URI"):
        get_settings()
