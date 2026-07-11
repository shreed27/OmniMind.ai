from __future__ import annotations

import pytest

from kernel.services.worker_scheduler import WorkerSchedulerService


def test_create_and_get() -> None:
    bus = __import__("kernel.core.event_bus", fromlist=["EventBus"]).EventBus()
    service = WorkerSchedulerService(event_bus=bus)
    worker = service.create("worker-1", "dept-1", role="Backend Engineer")
    assert worker.role == "Backend Engineer"
    assert service.get("worker-1").worker_id == "worker-1"
