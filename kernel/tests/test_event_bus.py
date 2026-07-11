from __future__ import annotations

from kernel.core.event import EventBus, EventEnvelope


def test_event_bus_publishes_to_subscriber() -> None:
    bus = EventBus()
    calls: list[EventEnvelope] = []
    bus.subscribe("MissionCreated", lambda event: calls.append(event))
    event = EventEnvelope.create("MissionCreated", {"value": 1})
    bus.publish(event)
    assert len(calls) == 1
    assert calls[0].payload["value"] == 1
