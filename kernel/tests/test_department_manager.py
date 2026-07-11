from __future__ import annotations

import pytest

from kernel.core.event_bus import InMemoryEventBus
from kernel.core.exceptions import InvalidTransitionError, KernelError
from kernel.services.department_manager import DepartmentManagerService


@pytest.fixture()
def event_bus() -> InMemoryEventBus:
    return InMemoryEventBus()


@pytest.fixture()
def service(event_bus: InMemoryEventBus) -> DepartmentManagerService:
    return DepartmentManagerService(event_bus)


@pytest.mark.asyncio()
async def test_spawn_department(service: DepartmentManagerService) -> None:
    department = await service.spawn("org-1", "Engineering", mission_id="mission-1", department_id="dept-1", manager_id="mgr-1")
    assert department.name == "Engineering"
    assert department.status == "Sleeping"


@pytest.mark.asyncio()
async def test_department_transition(service: DepartmentManagerService) -> None:
    await service.spawn("org-1", "Engineering", mission_id="mission-1", department_id="dept-1")
    updated = await service.transition("dept-1", "Executing")
    assert updated.status == "Executing"


@pytest.mark.asyncio()
async def test_merge_requires_sleeping(service: DepartmentManagerService) -> None:
    await service.spawn("org-1", "Engineering", mission_id="mission-1", department_id="dept-1")
    await service.spawn("org-1", "QA", mission_id="mission-1", department_id="dept-2")
    with pytest.raises(InvalidTransitionError):
        await service.transition("dept-1", "Executing")
        await service.merge("dept-1", "dept-2")


@pytest.mark.asyncio()
async def test_merge_sleeping_ok(service: DepartmentManagerService) -> None:
    await service.spawn("org-1", "Engineering", mission_id="mission-1", department_id="dept-1")
    await service.spawn("org-1", "QA", mission_id="mission-1", department_id="dept-2")
    result = await service.merge("dept-1", "dept-2")
    assert result["target_id"] == "dept-2"
