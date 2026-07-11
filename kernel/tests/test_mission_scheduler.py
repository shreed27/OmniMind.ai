from __future__ import annotations

from kernel.services.mission_scheduler import MissionSchedulerService


def test_mission_state_allowed() -> None:
    service = MissionSchedulerService(event_bus=__import__("kernel.core.event_bus", fromlist=["InMemoryEventBus"]).InMemoryEventBus())
    assert service.state("missing") == "Created"


def test_terminal_state_check() -> None:
    service = MissionSchedulerService(event_bus=__import__("kernel.core.event_bus", fromlist=["InMemoryEventBus"]).InMemoryEventBus())
    assert service.is_terminal("missing") is False
