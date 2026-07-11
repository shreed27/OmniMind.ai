from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.event import Event


async def append_event(session: AsyncSession, event: dict[str, Any]) -> None:
    entity = Event(
        id=event["id"],
        name=event["name"],
        payload=str(event.get("payload") or {}),
        context=str(event.get("context") or {}),
        mission_id=event.get("mission_id"),
    )
    session.add(entity)
    await session.flush()


async def get_events_by_mission(
    session: AsyncSession, mission_id: str, limit: int = 50
) -> AsyncIterator[Event]:
    statement = (
        select(Event)
        .where(Event.mission_id == mission_id)
        .order_by(Event.created_at.desc())
        .limit(limit)
    )
    result = await session.stream(statement)
    async for row in result:
        yield row
