from __future__ import annotations

from typing import Any

from kernel.core.event import EventBus, EventEnvelope
from kernel.core.exceptions import InvalidTransitionError


class Organization:
    __slots__ = ("organization_id", "mission_id", "state", "health", "hierarchy", "departments")

    def __init__(self, organization_id: str, mission_id: str, *, state: str = "Registered", health: str = "healthy", hierarchy: dict[str, Any] | None = None, departments: list[str] | None = None) -> None:
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
    def __init__(self, event_bus: EventBus) -> None:
        self._bus = event_bus
        self._organizations: dict[str, Organization] = {}

    def create(self, organization_id: str, mission_id: str) -> Organization:
        org = Organization(organization_id=organization_id, mission_id=mission_id, state="Registered")
        self._organizations[organization_id] = org
        return org

    def transition(self, organization_id: str, new_state: str) -> Organization:
        org = self._organizations[organization_id]
        current = org.state
        if new_state not in ALLOWED_ORGANIZATION_TRANSITIONS.get(current, set()):
            raise InvalidTransitionError("Invalid organization transition", context={"organization_id": organization_id, "from": current, "to": new_state})
        org.state = new_state
        return org

    def get(self, organization_id: str) -> Organization:
        org = self._organizations.get(organization_id)
        if org is None:
            raise InvalidTransitionError("organization not found", context={"organization_id": organization_id})
        return org

    def snapshot(self, organization_id: str) -> dict[str, Any]:
        org = self.get(organization_id)
        return {"organization_id": org.organization_id, "mission_id": org.mission_id, "state": org.state, "health": org.health, "hierarchy": org.hierarchy, "departments": org.departments}
