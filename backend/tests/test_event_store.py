import pytest
from app.events.store import append_event, get_events_by_mission


@pytest.mark.asyncio
async def test_append_event_roundtrip(async_db_session: pytest.FixtureRequest) -> None:
    event = {
        "id": "evt-1",
        "name": "MissionCreated",
        "payload": {"mission_id": "mission-1"},
        "context": {},
        "mission_id": "mission-1",
    }
    await append_event(async_db_session, event)
    events = [event async for event in get_events_by_mission(async_db_session, "mission-1")]
    assert len(events) == 1
