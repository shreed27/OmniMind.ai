from __future__ import annotations

from typing import Any

from kernel.core.event import EventBus
from kernel.core.exceptions import InvalidTransitionError


class Worker:
    __slots__ = ("worker_id", "department_id", "role", "status", "confidence")

    def __init__(self, worker_id: str, department_id: str, role: str = "worker", status: str = "idle", confidence: float = 1.0) -> None:
        self.worker_id = worker_id
        self.department_id = department_id
        self.role = role
        self.status = status
        self.confidence = confidence


class WorkerSchedulerService:
    def __init__(self, event_bus: EventBus) -> None:
        self._bus = event_bus
        self._workers: dict[str, Worker] = {}

    def create(self, worker_id: str, department_id: str, role: str = "worker") -> Worker:
        worker = Worker(worker_id=worker_id, department_id=department_id, role=role)
        self._workers[worker_id] = worker
        return worker

    def get(self, worker_id: str) -> Worker:
        worker = self._workers.get(worker_id)
        if worker is None:
            raise InvalidTransitionError("worker not found", context={"worker_id": worker_id})
        return worker
