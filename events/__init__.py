from __future__ import annotations

from typing import Any
from uuid import uuid4

from events.store import get_store
from kernel.core.events import EventEnvelope
from kernel.core.ports import EventBus
from kernel.core.event_bus import InMemoryEventBus


_event_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    global _event_bus
    if _event_bus is None:
        _event_bus = InMemoryEventBus()
    return _event_bus


async def publish_event(name: str, payload: dict[str, Any], context: dict[str, Any] | None = None) -> EventEnvelope:
    bus = get_event_bus()
    await bus.start()
    event = EventEnvelope(event_id=uuid4(), name=name, payload=payload, context=context or {})
    await bus.publish(event)
    return event


def load_history(mission_id: str | None = None) -> list[EventEnvelope]:
    history: list[EventEnvelope] = []
    for key, events in get_store().items():
        if mission_id and mission_id not in key:
            continue
        history.extend(events)
    history.sort(key=lambda event: event.timestamp)
    return history
