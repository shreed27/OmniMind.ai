from __future__ import annotations

import os


class MissingSecretError(Exception):
    """Raised when a required secret is missing."""


def get_secret(name: str, default: str | None = None) -> str:
    value = os.environ.get(name)
    if value:
        return value
    if default is not None:
        return default
    raise MissingSecretError(name)
