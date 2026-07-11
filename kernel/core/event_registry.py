from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from kernel.core.event import EventEnvelope

EVENT_REGISTRY: dict[str, dict[str, Any]] = {
    "MissionCreated": {},
    "MissionUpdated": {},
    "MissionPaused": {},
    "MissionResumed": {},
    "MissionBlocked": {},
    "MissionUnblocked": {},
    "MissionCancelled": {},
    "OrganizationCreated": {},
    "OrganizationUpdated": {},
    "OrganizationEvolved": {},
    "OrganizationArchived": {},
    "DepartmentCreated": {},
    "DepartmentActivated": {},
    "DepartmentPaused": {},
    "DepartmentResumed": {},
    "DepartmentMerged": {},
    "DepartmentSplit": {},
    "DepartmentDestroyed": {},
    "WorkerSpawned": {},
    "WorkerActivated": {},
    "WorkerPromoted": {},
    "WorkerRetired": {},
    "WorkerDestroyed": {},
    "SpecialistSpawned": {},
    "SpecialistKnowledgeTransferred": {},
    "SpecialistDestroyed": {},
    "TaskCreated": {},
    "TaskStarted": {},
    "TaskCompleted": {},
    "TaskFailed": {},
    "TaskRetried": {},
    "TaskBlocked": {},
    "TaskCancelled": {},
    "ArtifactCreated": {},
    "ArtifactUpdated": {},
    "ArtifactReviewed": {},
    "ArtifactPublished": {},
    "ReflectionStarted": {},
    "ReflectionCompleted": {},
    "LearningCompleted": {},
    "MissionGraphUpdated": {},
    "ConflictRaised": {},
    "VoteStarted": {},
    "VoteCompleted": {},
    "ApprovalRequested": {},
    "ApprovalCompleted": {},
    "NightCycleStarted": {},
    "NightCycleCompleted": {},
    "KernelTick": {},
    "EdgeActivated": {},
    "PluginInstalled": {},
    "PluginRemoved": {},
    "OrganizationIQUpdated": {},
    "SimulationStarted": {},
    "SimulationCompleted": {},
    "SimulationDiscarded": {},
}

class EventRegistry:
    _registry: dict[str, dict[str, Any]] = EVENT_REGISTRY

    @classmethod
    def defined_events(cls) -> list[str]:
        return sorted(cls._registry.keys())

    @classmethod
    def validate(cls, event: EventEnvelope) -> None:
        if event.payload_hash is None or len(event.payload_hash) != 64:
            raise ValueError("invalid payload hash")
        if event.source.get("service") is None:
            raise ValueError("event source service missing")

    @classmethod
    def canonical_definition(cls, name: str) -> dict[str, Any]:
        if name not in cls._registry:
            raise KeyError(f"unknown event: {name}")
        return cls._registry[name]


