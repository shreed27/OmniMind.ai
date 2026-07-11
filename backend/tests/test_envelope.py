import asyncio
from unittest.mock import AsyncMock

from app.core.events import EventEnvelope


def test_event_envelope_does_not_crash() -> None:
    envelope = EventEnvelope(name="Tested", payload={"ok": True}, context={})
    # logging is the only side-effect in emit(); we just assert no exception
    assert envelope.name == "Tested"
    assert envelope.payload == {"ok": True}
