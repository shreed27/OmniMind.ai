from __future__ import annotations

import pytest

from kernel.core.event_bus import InMemoryEventBus
from kernel.core.exceptions import InvalidTransitionError, KernelError
from kernel.services.worker_scheduler import WorkerSchedulerService


@pytest.fixture()
def event_bus() -> InMemoryEventBus:
    return InMemoryEventBus()


@pytest.fixture()
def service(event_bus: InMemoryEventBus) -> WorkerSchedulerService:
    return WorkerSchedulerService(event_bus)


@pytest.mark.asyncio()
async def test_worker_spawn(service: WorkerSchedulerService) -> None:
    worker = await service.spawn("dept-1", "org-1", "Backend Engineer", mission_id="mission-1")
    assert worker.role == "Backend Engineer"
    assert worker.status in {"Created", "Sleeping"}


@pytest.mark.asyncio()
async def test_worker_specialist_lifecycle(service: WorkerSchedulerService) -> None:
    worker = await service.spawn("dept-1", "org-1", "Specialist", mission_id="mission-1")
    await service.transition(str(worker.worker_id), "Waiting")
    await service.transition(str(worker.worker_id), "Executing")
    await service.transition(str(worker.worker_id), "Reviewing")
    completed = await service.transition(str(worker.worker_id), "Completed")
    retired = await service.retire(str(worker.worker_id))
    assert retired.status == "Archived"


@pytest.mark.asyncio()
async def test_worker_retirement(service: WorkerSchedulerService) -> None:
    worker = await service.spawn("dept-1", "org-1", "QA Engineer", mission_id="mission-1")
    retired = await service.retire(str(worker.worker_id))
    assert retired.status == "Archived"
    assert retired.notes["lineage"] == []
