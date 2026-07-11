from __future__ import annotations

import logging
import traceback
from typing import Any

from app.core.config import get_logger

logger = get_logger("app.events")


class EventEnvelope:
    """Event envelope for internal events."""

    __slots__ = ("name", "payload", "context")

    def __init__(self, name: str, payload: dict[str, Any], context: dict[str, Any]) -> None:
        self.name = name
        self.payload = payload
        self.context = context

    def emit(self) -> None:
        try:
            logger.info(
                'EVENT %s payload=%s context=%s',
                self.name,
                self.payload,
                self.context,
            )
        except Exception:  # pragma: no cover - logging must never fail orphaning events
            traceback.print_exc()


def _base_context() -> dict[str, Any]:
    from app.core.config import get_settings, enrich_event_context

    return enrich_event_context({})


def emit(name: str, payload: dict[str, Any], context: dict[str, Any] | None = None) -> EventEnvelope:
    """Create an event envelope and emit it immediately with structured logging."""
    merged = _base_context()
    if context:
        merged.update(context)
    event = EventEnvelope(name=name, payload=payload, context=merged)
    event.emit()
    return event
