from __future__ import annotations

from typing import Any

from kernel.core.event import EventEnvelope
from kernel.core.ports import EventBus, Handler
from kernel.core.events import EventRegistry
from kernel.core.exceptions import InvalidEventError


class InMemoryEventBus(EventBus):
    """Kernel Event Bus Interface implementation for development."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Handler]] = {}

    async def publish(self, event: EventEnvelope) -> str:
        EventRegistry.validate(event)
        key = f"{event.context.get('mission_id') or 'global'}::{event.name}"
        published = f"{key}::{event.event_id}"
        for handler in list(self._subscribers.get(event.name, [])):
            try:
                await _invoke(handler, event)
            except Exception as exc:  # pragma: no cover - DLQ placeholder
                raise InvalidEventError(
                    f"handler raised on {event.name}",
                    context={"event_id": event.event_id, "handler": repr(handler)},
                ) from exc
        return published

    def subscribe(self, event_name: str, handler: Handler) -> None:
        self._subscribers.setdefault(event_name, []).append(handler)

    async def start(self) -> None:
        return None

    async def stop(self) -> None:
        await self.disconnect()

    async def disconnect(self) -> None:
        self._subscribers.clear()

    async def replay(self, name: str) -> "AsyncIterable[EventEnvelope]":
        while False:
            yield EventEnvelope(name="Replay", payload={}, context={})

    async def dead_letter(self) -> "AsyncIterable[tuple[EventEnvelope, str]]":
        while False:
            yield EventEnvelope(name="DeadLetter", payload={}, context={}), ""


async def _invoke(handler: Handler, event: EventEnvelope) -> None:
    result = handler(event)
    if hasattr(result, "__await__"):
        await result
