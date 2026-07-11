from __future__ import annotations

from typing import Any

import pytest

from kernel.core.event_bus import InMemoryEventBus
from kernel.core.exceptions import InvalidTransitionError
from kernel.services.mission_scheduler import MissionSchedulerService


@pytest.fixture()
def event_bus() -> InMemoryEventBus:
    return InMemoryEventBus()


@pytest.fixture()
def scheduler(event_bus: InMemoryEventBus) -> MissionSchedulerService:
    return MissionSchedulerService(event_bus)


@pytest.mark.asyncio()
async def test_valid_transition(scheduler: MissionSchedulerService) -> None:
    await scheduler.transition("mission-1", "Queued", confidence=0.9)
    assert scheduler.state("mission-1") == "Queued"


@pytest.mark.asyncio()
async def test_invalid_transition(scheduler: MissionSchedulerService) -> None:
    with pytest.raises(InvalidTransitionError):
        await scheduler.transition("mission-1", "Archived", confidence=0.9)


@pytest.mark.asyncio()
async def test_terminal_state_emits_reflection(scheduler: MissionSchedulerService) -> None:
    seen: list[str] = []

    async def _listener(event: Any) -> None:
        seen.append(event.payload.get("name"))

    await scheduler._bus.subscribe("ReflectionStarted", _listener)
    await scheduler.transition("mission-1", "Cancelled", confidence=0.9)
    assert "ReflectionStarted" in seen


def test_not_terminal_by_default(scheduler: MissionSchedulerService) -> None:
    assert scheduler.is_terminal("mission-1") is False
