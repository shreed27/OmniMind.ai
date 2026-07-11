from __future__ import annotations

from typing import Any

from kernel.core.event import EventEnvelope


class InvalidEventError(Exception):
    """Raised when an event envelope is invalid."""


class EventRegistry:
    _defined: dict[str, dict[str, Any]] = {
        "MissionStateChanged": {"description": "Mission lifecycle transition."},
        "OrganizationCreated": {"description": "Organization registered."},
        "OrganizationUpdated": {"description": "Organization state changed."},
        "DepartmentCreated": {"description": "Department spawned."},
        "DepartmentUpdated": {"description": "Department state changed."},
        "DepartmentMerged": {"description": "Department merged."},
        "DepartmentDestroyed": {"description": "Department destroyed."},
        "WorkerSpawned": {"description": "Worker created."},
        "WorkerUpdated": {"description": "Worker state changed."},
        "WorkerRetired": {"description": "Worker archived."},
        "WorkerDestroyed": {"description": "Worker removed."},
        "ReflectionStarted": {"description": "Reflection triggered."},
    }

    @classmethod
    def validate(cls, event: EventEnvelope) -> None:
        if not isinstance(event, EventEnvelope):
            raise InvalidEventError("event must be an EventEnvelope instance")
        if not event.payload or not event.name:
            raise InvalidEventError("event missing payload/name")

    @classmethod
    def defined_events(cls) -> list[str]:
        return sorted(cls._defined.keys())

    @classmethod
    def canonical_definition(cls, name: str) -> dict[str, Any]:
        if name not in cls._defined:
            raise KeyError(f"unknown event: {name}")
        return cls._defined[name]
