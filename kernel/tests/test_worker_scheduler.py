import pytest
from kernel.services.worker_scheduler import WorkerSchedulerService


def test_create_and_get() -> None:
    bus = __import__("kernel.core.event_bus", fromlist=["InMemoryEventBus"]).InMemoryEventBus()
    service = WorkerSchedulerService(event_bus=bus)
    worker = __import__("asyncio").get_event_loop().run_until_complete(service.create("worker-1", "dept-1", role="Backend Engineer"))
    assert worker.role == "Backend Engineer"
    assert service.get("worker-1").worker_id == "worker-1"
