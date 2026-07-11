from __future__ import annotations

import logging
from typing import Any, Callable, Coroutine

from kernel.core.event import EventEnvelope, EventBus
from kernel.core.event_registry import EventRegistry
from kernel.core.exceptions import InvalidEventError, KernelBootError
from kernel.core.logging import get_logger

logger = get_logger("event_bus")


class InMemoryEventBus(EventBus):
    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable[[EventEnvelope], Coroutine[Any, Any, None]]]] = {}
        self._dead_letter: list[tuple[str, Exception]] = []
        self._history: list[EventEnvelope] = []

    async def publish(self, event: EventEnvelope) -> str:
        if not isinstance(event, EventEnvelope):
            raise KernelBootError("event bus accepts only EventEnvelope instances")

        try:
            EventRegistry.validate(event)
        except Exception as exc:
            raise InvalidEventError(str(exc)) from exc

        key = event.name or event.payload.get("name", "unknown")
        for handler in list(self._subscribers.get(key, [])):
            try:
                result = handler(event)
                if hasattr(result, "__await__"):
                    await result
            except Exception as exc:  # pragma: no cover - DLQ placeholder
                raise InvalidEventError(
                    f"handler raised on {key}",
                    context={"event_id": event.event_id, "handler": repr(handler)},
                ) from exc

        self._history.append(event)
        return event.causal_version

    def subscribe(self, event_name: str, handler: Callable[[EventEnvelope], Coroutine[Any, Any, None]]) -> str:
        self._subscribers.setdefault(event_name, []).append(handler)
        return event_name

    async def disconnect(self) -> None:
        self._subscribers.clear()

    def history(self) -> list[EventEnvelope]:
        return list(self._history)
