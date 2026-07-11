import pytest
from kernel.services.organization_manager import OrganizationManagerService


def test_create_sets_registered() -> None:
    bus = __import__("kernel.core.event_bus", fromlist=["InMemoryEventBus"]).InMemoryEventBus()
    service = OrganizationManagerService(event_bus=bus)
    org = __import__("asyncio").get_event_loop().run_until_complete(service.create("org-1", "mission-1"))
    assert org.state == "Registered"


def test_snapshot_returns_dict() -> None:
    bus = __import__("kernel.core.event_bus", fromlist=["InMemoryEventBus"]).InMemoryEventBus()
    service = OrganizationManagerService(event_bus=bus)
    __import__("asyncio").get_event_loop().run_until_complete(service.create("org-1", "mission-1"))
    snap = service.snapshot("org-1")
    assert snap["organization_id"] == "org-1"
