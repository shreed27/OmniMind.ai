from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.events.store import append_event, get_events_by_mission


@pytest.mark.asyncio
async def test_append_event_roundtrip(async_db_session: AsyncSession) -> None:
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
