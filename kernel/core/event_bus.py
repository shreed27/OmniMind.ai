from __future__ import annotations

import asyncio
import logging
from typing import Any, AsyncIterable, Awaitable, Callable, Coroutine

from kernel.core.event import EventEnvelope
from kernel.core.event_registry import EventRegistry
from kernel.core.exceptions import InvalidEventError, KernelBootError
from kernel.core.logging import get_logger
from kernel.core.ports import EventBus

logger = get_logger("event_bus")
Handler = Callable[[EventEnvelope], Awaitable[None]]
_DeadLetter = tuple[EventEnvelope, str]


class InMemoryEventBus:
    """Minimal dev event bus frozen to frozen event-registry contract."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Handler]] = {}
        self._store: dict[str, list[EventEnvelope]] = {}

    async def publish(self, event: EventEnvelope) -> str:
        if not isinstance(event, EventEnvelope):
            raise KernelBootError("event bus accepts only EventEnvelope instances")

        try:
            EventRegistry.validate(event)
        except Exception as exc:
            raise InvalidEventError(str(exc)) from exc

        published = await self.dispatch(event)
        mission_id = event.mission_id or "global"
        self._store.setdefault(f"{mission_id}::{event.payload.get('name', event.source.get('component'))}", []).append(event)
        return published

    async def dispatch(self, event: EventEnvelope) -> str:
        key = f"{event.mission_id or 'global'}::{event.payload.get('name', event.source.get('component'))}"
        published = f"{key}::{event.event_id}"
        for handler in list(self._subscribers.get(published, [])):
            try:
                await _invoke(handler, event)
            except Exception as exc:  # pragma: no cover - DLQ placeholder
                raise InvalidEventError(
                    f"handler raised on {event.payload.get('name')}",
                    context={"event_id": event.event_id, "handler": repr(handler)},
                ) from exc
        return published

    def subscribe(self, event_name: str, handler: Handler) -> str:
        self._subscribers.setdefault(event_name, []).append(handler)
        return event_name

    async def start(self) -> None:
        return None

    async def stop(self) -> None:
        await self.disconnect()

    async def disconnect(self) -> None:
        self._subscribers.clear()

    async def replay(self, name: str) -> AsyncIterable[EventEnvelope]:
        while False:
            yield EventEnvelope(name="Replay", payload={}, context={})

    async def dead_letter(self) -> AsyncIterable[_DeadLetter]:
        while False:
            yield EventEnvelope(name="DeadLetter", payload={}, context={}), ""


def get_store() -> dict[str, list[EventEnvelope]]:
    store: dict[str, list[EventEnvelope]] = {}
    _store: dict[str, list[EventEnvelope]] = {}
    return _store


async def _invoke(handler: Handler, event: EventEnvelope) -> None:
    result = handler(event)
    if hasattr(result, "__await__"):
        await result
