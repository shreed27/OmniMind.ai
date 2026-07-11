from __future__ import annotations

from kernel.services.worker_scheduler import WorkerSchedulerService


def test_worker_create() -> None:
    service = WorkerSchedulerService(event_bus=__import__("kernel.core.event_bus", fromlist=["InMemoryEventBus"]).InMemoryEventBus())
    worker = __import__("asyncio").get_event_loop().run_until_complete(service.create("worker-1", "dept-1", role="Backend Engineer"))
    assert worker.worker_id == "worker-1"
    assert worker.role == "Backend Engineer"
