from __future__ import annotations

import logging
from typing import Any, Callable

from kernel.core.event import EventEnvelope
from kernel.core.event_registry import EventRegistry
from kernel.core.exceptions import KernelError, InvalidTransitionError
from kernel.core.logging import get_logger

DEPARTMENT_STATES: list[str] = [
    "Sleeping",
    "Initializing",
    "Planning",
    "Waiting",
    "Executing",
    "Reviewing",
    "Reflecting",
    "Archived",
    "Merged",
    "Split",
    "Destroyed",
]

ALLOWED_DEPARTMENT_TRANSITIONS: dict[str, set[str]] = {
    "Sleeping": {"Initializing", "Merged", "Split", "Destroyed", "Planning", "Waiting", "Executing", "Archived"},
    "Initializing": {"Planning", "Archived", "Destroyed"},
    "Planning": {"Waiting", "Executing", "Archived", "Destroyed"},
    "Waiting": {"Executing", "Archived", "Destroyed"},
    "Executing": {"Reviewing", "Waiting", "Reflecting", "Archived", "Destroyed"},
    "Reviewing": {"Executing", "Reflecting", "Archived", "Destroyed"},
    "Reflecting": {"Sleeping", "Archived", "Destroyed"},
    "Archived": {"Destroyed"},
    "Merged": {"Destroyed"},
    "Split": {"Destroyed"},
    "Destroyed": set(),
}


class Department:
    __slots__ = (
        "department_id",
        "organization_id",
        "mission_id",
        "name",
        "type",
        "status",
        "manager_id",
        "memory",
        "resources",
        "kpis",
        "workers",
    )

    def __init__(
        self,
        department_id: str,
        organization_id: str,
        name: str,
        *,
        department_type: str = "department",
        status: str = "Sleeping",
        manager_id: str | None = None,
        memory: dict[str, Any] | None = None,
        resources: dict[str, Any] | None = None,
        kpis: dict[str, Any] | None = None,
        workers: list[str] | None = None,
    ) -> None:
        self.department_id = department_id
        self.organization_id = organization_id
        self.mission_id = ""
        self.name = name
        self.type = department_type
        self.status = status
        self.manager_id = manager_id
        self.memory = memory or {}
        self.resources = resources or {}
        self.kpis = kpis or {}
        self.workers = workers or []


class KnowledgeStore:
    _knowledge: list[dict[str, Any]] = []

    @classmethod
    def retain(cls, record: dict[str, Any]) -> None:
        stored = {"id": EventEnvelope.next_id(), **record}
        cls._knowledge.append(stored)


class DepartmentManagerService:
    def __init__(self, event_bus: Any) -> None:
        self._bus = event_bus
        self._logger = get_logger("department_manager")
        self._departments: dict[str, Department] = {}
        self._knowledge_index: dict[str, list[str]] = {}

    async def spawn(
        self,
        organization_id: str,
        name: str,
        *,
        mission_id: str,
        department_id: str | None = None,
        department_type: str = "department",
        manager_id: str | None = None,
        kpis: dict[str, Any] | None = None,
        trace_id: str | None = None,
        confidence: float = 0.8,
        source: dict[str, Any] | None = None,
    ) -> Department:
        from kernel.core.event import EventEnvelope
        identifier = department_id or EventEnvelope.next_id()
        department = Department(
            department_id=identifier,
            organization_id=organization_id,
            name=name,
            department_type=department_type,
            manager_id=manager_id,
            kpis=kpis or {},
        )
        department.mission_id = mission_id
        self._departments[identifier] = department
        event = EventEnvelope.create(
            name="DepartmentCreated",
            payload={
                "department_id": identifier,
                "organization_id": organization_id,
                "mission_id": mission_id,
                "name": name,
                "type": department.type,
                "status": department.status,
                "manager_id": manager_id,
                "kpis": department.kpis,
                "worker_ids": [],
            },
            organization_id=organization_id,
            mission_id=mission_id,
            trace_id=trace_id,
            confidence=confidence,
            source=source or {"service": "kernel", "module": "department_manager", "component": "lifecycle"},
        )
        await self._bus.publish(event)
        self._logger.info("Department spawned %s/%s", organization_id, name)
        return department

    async def transition(
        self,
        department_id: str,
        new_state: str,
        *,
        trace_id: str | None = None,
        confidence: float = 0.8,
        source: dict[str, Any] | None = None,
    ) -> Department:
        if new_state not in DEPARTMENT_STATES:
            raise InvalidTransitionError(f"Unknown department state: {new_state}")
        department = self._get(department_id)
        current = department.status
        if new_state not in ALLOWED_DEPARTMENT_TRANSITIONS.get(current, set()):
            raise InvalidTransitionError(
                f"Invalid department transition {current} -> {new_state}",
                context={"department_id": department_id, "from": current, "to": new_state},
            )
        department.status = new_state
        event_name = (
            "DepartmentMerged" if new_state == "Merged" else "DepartmentDestroyed" if new_state == "Destroyed" else "DepartmentUpdated"
        )
        from kernel.core.event import EventEnvelope
        event = EventEnvelope.create(
            name=event_name,
            payload={
                "department_id": department_id,
                "name": department.name,
                "state": new_state,
                "manager_id": department.manager_id,
                "worker_count": len(department.workers),
            },
            department_id=department_id,
            trace_id=trace_id,
            confidence=confidence,
            source=source or {"service": "kernel", "module": "department_manager", "component": "lifecycle"},
        )
        await self._bus.publish(event)
        return department

    async def merge(
        self,
        source_id: str,
        target_id: str,
        *,
        trace_id: str | None = None,
        confidence: float = 0.8,
        source: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        source_dept = self._get(source_id)
        target_dept = self._get(target_id)
        if source_dept.status != "Sleeping":
            raise InvalidTransitionError("Source department must be Sleeping before merge")
        if target_dept.status == "Destroyed":
            raise InvalidTransitionError("Cannot merge into a destroyed department")
        merged_workers = list(source_dept.workers) + list(target_dept.workers)
        target_dept.workers = merged_workers
        await self.transition(source_id, "Merged", trace_id=trace_id, confidence=confidence, source=source)
        self._index_knowledge(source_id, target_dept.name)
        return {"target_id": target_id, "worker_count": len(merged_workers), "departments": [source_id, target_id]}

    async def split(
        self,
        source_id: str,
        *,
        names: list[str],
        trace_id: str | None = None,
        confidence: float = 0.8,
        source: dict[str, Any] | None = None,
    ) -> list[str]:
        from kernel.core.event import EventEnvelope
        source_dept = self._get(source_id)
        if source_dept.status != "Sleeping":
            raise InvalidTransitionError("Source department must be Sleeping before split")
        created_names = []
        for name in names:
            department = Department(
                department_id=EventEnvelope.next_id(),
                organization_id=source_dept.organization_id,
                name=name,
                department_type=source_dept.type,
                manager_id=source_dept.manager_id,
            )
            self._departments[department.department_id] = department
            created_names.append(department.department_id)
        await self.transition(source_id, "Split", trace_id=trace_id, confidence=confidence, source=source)
        for name in names:
            self._index_knowledge(source_id, name)
        return created_names

    def register_worker(self, department_id: str, worker_id: str) -> None:
        department = self._get(department_id)
        if worker_id not in department.workers:
            department.workers.append(worker_id)

    def workers(self, department_id: str) -> list[str]:
        return list(self._get(department_id).workers)

    def _get(self, department_id: str) -> Department:
        department = self._departments.get(department_id)
        if department is None:
            raise KernelError("department not found", context={"department_id": department_id})
        return department

    def _index_knowledge(self, source_id: str, target_name: str) -> None:
        self._knowledge_index.setdefault(source_id, []).append(target_name)
        KnowledgeStore.retain({"source_department_id": source_id, "name": target_name})
