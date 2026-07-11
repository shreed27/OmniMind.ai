import pytest

from app.core.config import get_settings


def test_default_settings_has_expected_defaults() -> None:
    settings = get_settings()
    assert settings.app_env == "development"
    assert settings.log_level == "INFO"
    assert "omnimind" in settings.database_url or settings.database_url.startswith("sqlite")
