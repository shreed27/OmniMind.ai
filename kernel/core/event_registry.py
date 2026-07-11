from __future__ import annotations

from typing import Any

from kernel.core.registry import load_registry


class InvalidEventError(Exception):
    """Raised when an event schema is invalid."""


REQUIRED_EVENT_FIELDS = {"name", "payload", "context", "created_at"}


def validate_event(event: dict[str, Any]) -> None:
    missing = REQUIRED_EVENT_FIELDS - event.keys()
    if missing:
        raise InvalidEventError(f"missing fields: {', '.join(sorted(missing))}")


def load_event_registry(path: str = "docs/registry/EVENTS.md") -> dict[str, Any]:
    return load_registry(path)
