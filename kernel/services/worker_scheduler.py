from __future__ import annotations

from typing import Any

from kernel.core.event import EventEnvelope
from kernel.core.exceptions import InvalidTransitionError, KernelError
from kernel.core.logging import get_logger

WORKER_STATES: list[str] = [
    "Created",
    "Sleeping",
    "Waiting",
    "Thinking",
    "Planning",
    "Executing",
    "Reviewing",
    "Blocked",
    "Escalated",
    "Reflecting",
    "Completed",
    "Archived",
    "Destroyed",
]

ALLOWED_WORKER_TRANSITIONS: dict[str, set[str]] = {
    "Created": {"Sleeping", "Waiting", "Destroyed"},
    "Sleeping": {"Waiting", "Thinking", "Archived", "Destroyed"},
    "Waiting": {"Thinking", "Executing", "Blocked", "Escalated", "Destroyed"},
    "Thinking": {"Planning", "Executing", "Waiting", "Destroyed"},
    "Planning": {"Executing", "Waiting", "Destroyed"},
    "Executing": {"Reviewing", "Blocked", "Escalated", "Reflecting", "Completed", "Destroyed"},
    "Reviewing": {"Executing", "Reflecting", "Completed", "Destroyed"},
    "Blocked": {"Executing", "Reflecting", "Failed", "Destroyed"},
    "Escalated": {"Executing", "Waiting", "Failed", "Destroyed"},
    "Reflecting": {"Sleeping", "Completed", "Archived", "Destroyed"},
    "Completed": {"Archived", "Destroyed"},
    "Archived": {"Destroyed"},
    "Destroyed": set(),
}


class Worker:
    __slots__ = ("worker_id", "department_id", "organization_id", "mission_id", "role", "status", "confidence", "notes")

    def __init__(
        self,
        worker_id: str,
        department_id: str,
        organization_id: str,
        role: str,
        *,
        mission_id: str = "",
        status: str = "Created",
        confidence: float = 0.0,
        notes: dict[str, Any] | None = None,
    ) -> None:
        self.worker_id = worker_id
        self.department_id = department_id
        self.organization_id = organization_id
        self.mission_id = mission_id
        self.role = role
        self.status = status
        self.confidence = confidence
        self.notes = notes or {"lineage": [], "tasks": []}


class WorkerSchedulerService:
    def __init__(self, event_bus: Any) -> None:
        self._bus = event_bus
        self._logger = get_logger("worker_scheduler")
        self._workers: dict[str, Worker] = {}

    async def spawn(
        self,
        department_id: str,
        organization_id: str,
        role: str,
        *,
        mission_id: str = "",
        trace_id: str | None = None,
        confidence: float = 0.8,
        source: dict[str, Any] | None = None,
    ) -> Worker:
        from kernel.core.event import EventEnvelope
        worker_id = EventEnvelope.next_id()
        worker = Worker(
            worker_id=worker_id,
            department_id=department_id,
            organization_id=organization_id,
            role=role,
            mission_id=mission_id,
            status="Created",
            confidence=confidence,
        )
        self._workers[worker_id] = worker
        event = EventEnvelope.create(
            name="WorkerSpawned",
            payload={
                "worker_id": worker_id,
                "department_id": department_id,
                "organization_id": organization_id,
                "mission_id": mission_id,
                "role": role,
                "status": worker.status,
                "confidence": confidence,
            },
            department_id=department_id,
            trace_id=trace_id,
            confidence=confidence,
            source=source or {"service": "kernel", "module": "worker_scheduler", "component": "lifecycle"},
        )
        await self._bus.publish(event)
        self._logger.info("Worker spawned %s/%s", department_id, role)
        return worker

    async def transition(
        self,
        worker_id: str,
        new_state: str,
        *,
        trace_id: str | None = None,
        confidence: float = 0.8,
        source: dict[str, Any] | None = None,
    ) -> Worker:
        if new_state not in WORKER_STATES:
            raise InvalidTransitionError(f"Unknown worker state: {new_state}")
        worker = self._get(worker_id)
        current = worker.status
        if new_state not in ALLOWED_WORKER_TRANSITIONS.get(current, set()):
            raise InvalidTransitionError(
                f"Invalid worker transition {current} -> {new_state}",
                context={"worker_id": worker_id, "from": current, "to": new_state},
            )
        worker.status = new_state
        from kernel.core.event import EventEnvelope
        event_name = "WorkerRetired" if new_state == "Archived" else "WorkerDestroyed" if new_state == "Destroyed" else "WorkerUpdated"
        event = EventEnvelope.create(
            name=event_name,
            payload={
                "worker_id": worker_id,
                "role": worker.role,
                "department_id": worker.department_id,
                "organization_id": worker.organization_id,
                "state": new_state,
                "confidence": worker.confidence,
            },
            department_id=worker.department_id,
            trace_id=trace_id,
            confidence=confidence,
            source=source or {"service": "kernel", "module": "worker_scheduler", "component": "lifecycle"},
        )
        await self._bus.publish(event)
        return worker

    async def retire(
        self,
        worker_id: str,
        *,
        trace_id: str | None = None,
        confidence: float = 0.8,
        source: dict[str, Any] | None = None,
    ) -> Worker:
        worker = await self.transition(worker_id, "Archived", trace_id=trace_id, confidence=confidence, source=source)
        return worker

    def get(self, worker_id: str) -> Worker:
        return self._get(worker_id)

    def _get(self, worker_id: str) -> Worker:
        worker = self._workers.get(worker_id)
        if worker is None:
            raise KernelError("worker not found", context={"worker_id": worker_id})
        return worker

    def by_department(self, department_id: str) -> list[Worker]:
        return [worker for worker in self._workers.values() if worker.department_id == department_id and worker.status != "Destroyed"]
