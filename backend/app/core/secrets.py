from __future__ import annotations

import os

from app.core.config import get_settings


def get_secret(name: str, default: str | None = None) -> str:
    value = os.environ.get(name)
    if value is None and default is None:
        raise MissingSecretError(name)
    return value or (default or "")  # type: ignore[return-value]


class MissingSecretError(Exception):
    """Raised when a required secret is missing."""
