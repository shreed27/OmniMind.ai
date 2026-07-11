from __future__ import annotations

import pytest

from kernel.core.event_bus import InMemoryEventBus
from kernel.core.exceptions import InvalidTransitionError, KernelError
from kernel.services.organization_manager import OrganizationManagerService


@pytest.fixture()
def event_bus() -> InMemoryEventBus:
    return InMemoryEventBus()


@pytest.fixture()
def service(event_bus: InMemoryEventBus) -> OrganizationManagerService:
    return OrganizationManagerService(event_bus)


@pytest.mark.asyncio()
async def test_organization_created(service: OrganizationManagerService) -> None:
    org = await service.create("org-1", "mission-1", trace_id="trace-1", confidence=0.8)
    assert org.state == "Registered"
    assert service.snapshot("org-1")["organization_id"] == "org-1"


@pytest.mark.asyncio()
async def test_invalid_transition(service: OrganizationManagerService) -> None:
    await service.create("org-1", "mission-1")
    with pytest.raises(InvalidTransitionError):
        await service.transition("org-1", "Destroyed")


@pytest.mark.asyncio()
async def test_missing_organization(service: OrganizationManagerService) -> None:
    with pytest.raises(KernelError):
        service.get("missing")
