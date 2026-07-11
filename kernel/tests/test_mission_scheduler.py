import pytest
from kernel.services.mission_scheduler import MissionSchedulerService, MissionState


def test_allowed_transitions_rejects_invalid() -> None:
    bus = __import__("kernel.core.event_bus", fromlist=["InMemoryEventBus"]).InMemoryEventBus()
    service = MissionSchedulerService(event_bus=bus)
    with pytest.raises(Exception):
        __import__("asyncio").get_event_loop().run_until_complete(service.transition("m1", "Archived"))


def test_terminal_check() -> None:
    service = MissionSchedulerService(event_bus=__import__("kernel.core.event_bus", fromlist=["InMemoryEventBus"]).InMemoryEventBus())
    assert service.is_terminal("m1") is False
