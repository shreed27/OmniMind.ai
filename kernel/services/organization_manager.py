from __future__ import annotations

from typing import Any, Awaitable, Callable, Coroutine

from kernel.core.event import EventEnvelope
from kernel.core.exceptions import KernelError, InvalidTransitionError
from kernel.core.logging import get_logger


class Organization:
    __slots__ = (
        "organization_id",
        "mission_id",
        "state",
        "health",
        "hierarchy",
        "departments",
    )

    def __init__(
        self,
        organization_id: str,
        mission_id: str,
        *,
        state: str = "Registered",
        health: str = "healthy",
        hierarchy: dict[str, Any] | None = None,
        departments: list[str] | None = None,
    ) -> None:
        self.organization_id = organization_id
        self.mission_id = mission_id
        self.state = state
        self.health = health
        self.hierarchy = hierarchy or {"ceo": [], "executives": [], "departments": []}
        self.departments = departments or []


ALLOWED_ORGANIZATION_TRANSITIONS: dict[str, set[str]] = {
    "Registered": {"Initializing", "Archived", "Destroyed"},
    "Initializing": {"Planning", "Executing", "Archived", "Destroyed"},
    "Planning": {"Executing", "Archived", "Destroyed"},
    "Executing": {"Reflecting", "Archived", "Destroyed"},
    "Reflecting": {"Learning", "Executing", "Archived", "Destroyed"},
    "Learning": {"Evolving", "Executing", "Archived", "Destroyed"},
    "Evolving": {"Executing", "Archived", "Destroyed"},
    "Archived": {"Destroyed"},
    "Destroyed": set(),
}


class OrganizationManagerService:
    def __init__(self, event_bus: Any) -> None:
        self._bus = event_bus
        self._logger = get_logger("organization_manager")
        self._organizations: dict[str, Organization] = {}

    async def create(
        self,
        organization_id: str,
        mission_id: str,
        *,
        trace_id: str | None = None,
        confidence: float = 0.8,
        source: dict[str, Any] | None = None,
    ) -> Organization:
        org = Organization(
            organization_id=organization_id,
            mission_id=mission_id,
            state="Registered",
        )
        self._organizations[organization_id] = org
        event = EventEnvelope.create(
            name="OrganizationCreated",
            payload={
                "organization_id": organization_id,
                "mission_id": mission_id,
                "state": org.state,
                "health": org.health,
                "hierarchy": org.hierarchy,
                "organisms": [],
                "departments": org.departments,
            },
            mission_id=mission_id,
            trace_id=trace_id,
            confidence=confidence,
            source=source or {"service": "kernel", "module": "organization_manager", "component": "lifecycle"},
        )
        await self._bus.publish(event)
        return org

    async def transition(
        self,
        organization_id: str,
        new_state: str,
        *,
        trace_id: str | None = None,
        confidence: float = 0.8,
        source: dict[str, Any] | None = None,
    ) -> Organization:
        org = self._organizations.get(organization_id)
        if org is None:
            raise KernelError("organization not found", context={"organization_id": organization_id})
        current = org.state
        if new_state not in ALLOWED_ORGANIZATION_TRANSITIONS.get(current, set()):
            raise InvalidTransitionError(
                f"Invalid organization transition {current} -> {new_state}",
                context={"organization_id": organization_id, "from": current, "to": new_state},
            )
        org.state = new_state
        event = EventEnvelope.create(
            name="OrganizationUpdated",
            payload={
                "organization_id": organization_id,
                "mission_id": org.mission_id,
                "state": new_state,
                "health": org.health,
                "hierarchy": org.hierarchy,
                "departments": org.departments,
            },
            organization_id=organization_id,
            mission_id=org.mission_id,
            trace_id=trace_id,
            confidence=confidence,
            source=source or {"service": "kernel", "module": "organization_manager", "component": "lifecycle"},
        )
        await self._bus.publish(event)
        return org

    def get(self, organization_id: str) -> Organization:
        org = self._organizations.get(organization_id)
        if org is None:
            raise KernelError("organization not found", context={"organization_id": organization_id})
        return org

    def snapshot(self, organization_id: str) -> dict[str, Any]:
        org = self.get(organization_id)
        return {
            "organization_id": org.organization_id,
            "mission_id": org.mission_id,
            "state": org.state,
            "health": org.health,
            "hierarchy": org.hierarchy,
            "departments": org.departments,
        }
