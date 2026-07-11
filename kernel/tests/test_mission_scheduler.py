import pytest
from kernel.services.mission_scheduler import MissionSchedulerService


def test_allowed_transitions_rejects_invalid() -> None:
    bus = __import__("kernel.core.event_bus", fromlist=["EventBus"]).EventBus()
    service = MissionSchedulerService(event_bus=bus)
    with pytest.raises(Exception):
        service.transition("m1", "Archived")


def test_terminal_check() -> None:
    service = MissionSchedulerService(event_bus=__import__("kernel.core.event_bus", fromlist=["EventBus"]).EventBus())
    assert service.is_terminal("m1") is False
