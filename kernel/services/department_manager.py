from __future__ import annotations

from typing import Any

from kernel.core.event import EventBus, EventEnvelope
from kernel.core.exceptions import InvalidTransitionError


class Department:
    __slots__ = ("department_id", "organization_id", "type", "manager_id", "name", "description")

    def __init__(self, department_id: str, organization_id: str, type: str = "general", manager_id: str | None = None, name: str | None = None, description: str | None = None) -> None:
        self.department_id = department_id
        self.organization_id = organization_id
        self.type = type
        self.manager_id = manager_id or ""
        self.name = name or ""
        self.description = description or ""


class DepartmentManagerService:
    def __init__(self, event_bus: EventBus) -> None:
        self._bus = event_bus
        self._departments: dict[str, Department] = {}

    def create(self, department_id: str, organization_id: str, type: str = "general", name: str | None = None, description: str | None = None) -> Department:
        dept = Department(department_id=department_id, organization_id=organization_id, type=type, name=name, description=description)
        self._departments[department_id] = dept
        return dept

    def get(self, department_id: str) -> Department:
        dept = self._departments.get(department_id)
        if dept is None:
            raise InvalidTransitionError("department not found", context={"department_id": department_id})
        return dept
