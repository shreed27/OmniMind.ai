from __future__ import annotations

import pytest

from kernel.core.event import EventEnvelope
from kernel.core.event_bus import InMemoryEventBus


@pytest.mark.asyncio()
async def test_event_bus_publish_returns_event_reference() -> None:
    bus = InMemoryEventBus()
    event = EventEnvelope(name="MissionCreated", payload={"ok": True}, context={"mission_id": "m1"})
    reference = await bus.publish(event)
    assert reference.endswith(event.event_id)


@pytest.mark.asyncio()
async def test_event_bus_subscriber_receives_event() -> None:
    bus = InMemoryEventBus()
    received: list[EventEnvelope] = []

    def handler(event: EventEnvelope) -> None:
        received.append(event)

    bus.subscribe("MissionCreated", handler)
    event = EventEnvelope(
        name="MissionCreated",
        payload={"ok": True, "service": "kernel"},
        context={"mission_id": "m1"},
    )
    await bus.publish(event)
    assert received == [event]
