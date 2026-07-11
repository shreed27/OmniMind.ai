from __future__ import annotations

from kernel.core.event import EventEnvelope


def test_event_envelope_is_immutable() -> None:
    payload = {"mission_id": "mission-1"}
    context = {"trace_id": "trace-1"}
    event = EventEnvelope(name="MissionCreated", payload=payload, context=context)
    assert event.name == "MissionCreated"
    assert event.payload_hash == EventEnvelope(name="MissionCreated", payload=payload, context=context).payload_hash
    assert len(event.event_id) == 64


def test_event_envelope_rejects_non_hashable_payload() -> None:
    with pytest.raises(ValueError):
        EventEnvelope(name="Bad", payload=[set()]).payload_hash  # type: ignore[arg-type]
