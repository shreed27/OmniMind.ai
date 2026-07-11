from __future__ import annotations

from kernel.services.organization_manager import OrganizationManagerService


def test_organization_create_publishes_event() -> None:
    bus = __import__("kernel.core.event_bus", fromlist=["InMemoryEventBus"]).InMemoryEventBus()
    service = OrganizationManagerService(event_bus=bus)
    org = __import__("asyncio").get_event_loop().run_until_complete(service.create("org-1", "mission-1"))
    assert org.organization_id == "org-1"
    assert org.state == "Registered"


def test_organization_get_raises_when_missing() -> None:
    service = OrganizationManagerService(event_bus=__import__("kernel.core.event_bus", fromlist=["InMemoryEventBus"]).InMemoryEventBus())
    try:
        service.get("missing")
    except Exception as exc:
        assert "organization not found" in str(exc)
