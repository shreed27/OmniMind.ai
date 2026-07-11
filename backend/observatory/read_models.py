"""
Observatory Read Models - TASK-11.3

Denormalized projections for fast frontend queries.
Updated via event subscriptions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from kernel.core.event import EventEnvelope
from kernel.core.logging import get_logger


@dataclass
class MissionReadModel:
    """Denormalized mission view for frontend."""

    mission_id: str
    name: str
    objective: str
    status: str
    current_phase: str
    progress: float
    confidence: float
    organization_id: str | None = None
    department_count: int = 0
    worker_count: int = 0
    artifact_count: int = 0
    health: str = "healthy"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class OrganizationReadModel:
    """Denormalized organization view."""

    organization_id: str
    mission_id: str
    health: str
    iq: float
    plasticity: float
    state: str
    departments: list[dict[str, Any]] = field(default_factory=list)
    hierarchy: dict[str, Any] = field(default_factory=dict)
    current_event_cursor: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class DepartmentReadModel:
    """Denormalized department view."""

    department_id: str
    organization_id: str
    mission_id: str
    type: str
    status: str
    manager_id: str | None
    worker_ids: list[str] = field(default_factory=list)
    task_ids: list[str] = field(default_factory=list)
    kpis: dict[str, Any] = field(default_factory=dict)
    health: str = "healthy"
    confidence: float = 0.8
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class WorkerReadModel:
    """Denormalized worker view."""

    worker_id: str
    department_id: str
    organization_id: str
    mission_id: str
    role: str
    status: str
    current_task_id: str | None
    confidence: float
    dna: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ObservatoryProjection:
    """
    Event-sourced read model projections.

    Subscribes to events and updates denormalized views.
    """

    def __init__(self) -> None:
        self._logger = get_logger("observatory")
        self._missions: dict[str, MissionReadModel] = {}
        self._organizations: dict[str, OrganizationReadModel] = {}
        self._departments: dict[str, DepartmentReadModel] = {}
        self._workers: dict[str, WorkerReadModel] = {}

    async def handle_event(self, event: EventEnvelope) -> None:
        """Update read models based on event."""
        event_name = event.payload.get("name", "")

        if event_name == "MissionCreated":
            await self._handle_mission_created(event)
        elif event_name == "MissionStateChanged":
            await self._handle_mission_state_changed(event)
        elif event_name == "OrganizationCreated":
            await self._handle_organization_created(event)
        elif event_name == "DepartmentCreated":
            await self._handle_department_created(event)
        elif event_name == "WorkerSpawned":
            await self._handle_worker_spawned(event)
        elif event_name == "DigitalTwinUpdated":
            await self._handle_digital_twin_updated(event)

    async def _handle_mission_created(self, event: EventEnvelope) -> None:
        """Project MissionCreated event."""
        payload = event.payload
        mission_id = payload.get("mission_id")

        if not mission_id:
            return

        self._missions[mission_id] = MissionReadModel(
            mission_id=mission_id,
            name=payload.get("name", ""),
            objective=payload.get("objective", ""),
            status="created",
            current_phase="planning",
            progress=0.0,
            confidence=event.confidence,
            organization_id=event.organization_id,
        )

        self._logger.info("Projected MissionCreated: %s", mission_id)

    async def _handle_mission_state_changed(self, event: EventEnvelope) -> None:
        """Project MissionStateChanged event."""
        payload = event.payload
        mission_id = payload.get("mission_id")

        if mission_id and mission_id in self._missions:
            mission = self._missions[mission_id]
            mission.status = payload.get("to_state", mission.status)
            mission.confidence = event.confidence
            mission.updated_at = event.timestamp

    async def _handle_organization_created(self, event: EventEnvelope) -> None:
        """Project OrganizationCreated event."""
        payload = event.payload
        organization_id = payload.get("organization_id")

        if not organization_id:
            return

        self._organizations[organization_id] = OrganizationReadModel(
            organization_id=organization_id,
            mission_id=payload.get("mission_id", ""),
            health="healthy",
            iq=0.0,
            plasticity=0.0,
            state="initializing",
        )

        self._logger.info("Projected OrganizationCreated: %s", organization_id)

    async def _handle_department_created(self, event: EventEnvelope) -> None:
        """Project DepartmentCreated event."""
        payload = event.payload
        department_id = payload.get("department_id")

        if not department_id:
            return

        self._departments[department_id] = DepartmentReadModel(
            department_id=department_id,
            organization_id=event.organization_id or "",
            mission_id=event.mission_id or "",
            type=payload.get("type", "unknown"),
            status="initializing",
            manager_id=None,
        )

    async def _handle_worker_spawned(self, event: EventEnvelope) -> None:
        """Project WorkerSpawned event."""
        payload = event.payload
        worker_id = payload.get("worker_id")

        if not worker_id:
            return

        self._workers[worker_id] = WorkerReadModel(
            worker_id=worker_id,
            department_id=event.department_id or "",
            organization_id=event.organization_id or "",
            mission_id=event.mission_id or "",
            role=payload.get("role", "worker"),
            status="waiting",
            current_task_id=None,
            confidence=event.confidence,
        )

    async def _handle_digital_twin_updated(self, event: EventEnvelope) -> None:
        """Project DigitalTwinUpdated event."""
        payload = event.payload
        entity_type = payload.get("entity_type")
        entity_id = payload.get("entity_id")
        snapshot = payload.get("snapshot", {})

        if entity_type == "mission" and entity_id in self._missions:
            mission = self._missions[entity_id]
            mission.status = snapshot.get("state", mission.status)
            mission.progress = snapshot.get("progress", mission.progress)
            mission.current_phase = snapshot.get("current_phase", mission.current_phase)
            mission.updated_at = snapshot.get("updated_at", mission.updated_at)

    def get_mission(self, mission_id: str) -> MissionReadModel | None:
        """Query mission read model."""
        return self._missions.get(mission_id)

    def get_organization(self, organization_id: str) -> OrganizationReadModel | None:
        """Query organization read model."""
        return self._organizations.get(organization_id)

    def list_missions(self, limit: int = 100) -> list[MissionReadModel]:
        """List all missions."""
        return list(self._missions.values())[:limit]

    def list_departments(self, organization_id: str) -> list[DepartmentReadModel]:
        """List departments for organization."""
        return [dept for dept in self._departments.values() if dept.organization_id == organization_id]

    def list_workers(self, department_id: str) -> list[WorkerReadModel]:
        """List workers for department."""
        return [worker for worker in self._workers.values() if worker.department_id == department_id]
