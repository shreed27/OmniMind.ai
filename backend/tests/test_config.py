from __future__ import annotations

import pytest

from app.core.config import get_settings


def test_default_settings() -> None:
    settings = get_settings()
    assert settings.app_name == "omnimind-backend"
    assert settings.app_env
    assert settings.log_level
    assert settings.database_url


def test_settings_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_NAME", "override-name")
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    settings = get_settings()
    assert settings.app_name == "override-name"
    assert settings.app_env == "test"
