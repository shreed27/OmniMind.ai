from __future__ import annotations

from typing import Any

from kernel.core.event import EventEnvelope
from kernel.core.registry import load_registry


class RegistryError(Exception):
    """Raised when the registry file is invalid or missing."""


class InvalidEventError(Exception):
    """Raised when an event schema is invalid."""


REQUIRED_EVENT_FIELDS = {"name", "payload", "timestamp", "source"}


def validate_event(event: EventEnvelope) -> None:
    if not isinstance(event, EventEnvelope):
        raise InvalidEventError("event must be an EventEnvelope instance")
    payload = getattr(event, "payload", None) or {}
    missing = REQUIRED_EVENT_FIELDS - set(payload.keys()) - set(getattr(event, "source", {}).keys())
    if "name" in missing:
        missing.discard("name")
        missing.add("name")
    if missing:
        raise InvalidEventError(f"missing fields: {', '.join(sorted(missing))}")


def load_event_registry(path: str | None = None) -> dict[str, Any]:
    base = Path(__file__).resolve().parent.parent
    target = Path(path) if path else base / "docs" / "registry" / "EVENTS.md"
    if not target.exists():
        target = Path(path or "docs/registry/EVENTS.md")
    return load_registry(str(target))


class EventRegistry:
    _registry: dict[str, dict[str, Any]] = {
        "MissionCreated": {"description": "Mission entering the system."},
        "MissionUpdated": {"description": "Non-destructive metadata update."},
        "MissionPaused": {"description": "Kernel pauses execution."},
        "MissionResumed": {"description": "Kernel resumes execution."},
        "MissionBlocked": {"description": "Mission cannot proceed without external input."},
        "MissionUnblocked": {"description": "Blocker removed."},
        "MissionCancelled": {"description": "Cancellation; reflection still executes."},
        "OrganizationCreated": {"description": "Binding mission to new org."},
        "OrganizationUpdated": {"description": "Health/IQ/plasticity changes."},
        "OrganizationEvolved": {"description": "Structural changes already applied."},
        "OrganizationArchived": {"description": "Post-completion archival."},
        "DepartmentCreated": {"description": "Spawned by CEO or Executive action."},
        "DepartmentMerged": {"description": "Two departments merged."},
        "DepartmentSplit": {"description": "One department split."},
        "DepartmentDestroyed": {"description": "Removed; knowledge retained."},
        "WorkerSpawned": {"description": "New worker created."},
        "WorkerRetired": {"description": "Archived; lineage retained."},
        "WorkerDestroyed": {"description": "Removed from active org."},
        "SpecialistSpawned": {"description": "Ephemeral worker spawned."},
        "SpecialistKnowledgeTransferred": {"description": "Knowledge moved to department."},
        "SpecialistDestroyed": {"description": "Ephemeral worker removed."},
        "TaskCreated": {"description": "Assigned to worker."},
        "TaskStarted": {"description": "Execution began."},
        "TaskCompleted": {"description": "Successful completion."},
        "TaskFailed": {"description": "Terminal failure."},
        "TaskBlocked": {"description": "Dependency missing."},
        "TaskCancelled": {"description": "Ancestor cancelled."},
        "ArtifactCreated": {"description": "Published."},
        "ArtifactUpdated": {"description": "Patched/relinked."},
        "ArtifactReviewed": {"description": "Review decision attached."},
        "ArtifactPublished": {"description": "Approved and surfaced."},
        "ReflectionStarted": {"description": "Mandatory reflection begins."},
        "ReflectionCompleted": {"description": "Lessons/knowledge/skills emitted."},
        "LearningCompleted": {"description": "Knowledge graph + constitution updated."},
        "MissionGraphUpdated": {"description": "Mission graph changed."},
        "ConflictRaised": {"description": "Disagreement detected."},
        "VoteStarted": {"description": "Executive vote started."},
        "VoteCompleted": {"description": "Immutable vote node recorded."},
        "ApprovalRequested": {"description": "Human approval required."},
        "ApprovalCompleted": {"description": "Human answered."},
        "NightCycleStarted": {"description": "Idle maintenance started."},
        "NightCycleCompleted": {"description": "Maintenance finished."},
        "KernelTick": {"description": "Kernel loop completed."},
        "EdgeActivated": {"description": "Local mode enabled."},
        "PluginInstalled": {"description": "Manifest registered."},
        "PluginRemoved": {"description": "Manifest unregistered."},
        "OrganizationIQUpdated": {"description": "Aggregate score changed."},
        "SimulationStarted": {"description": "Counterfactual run initiated."},
        "SimulationCompleted": {"description": "Counterfactual run completed."},
        "SimulationDiscarded": {"description": "Branch discarded; production untouched."},
    }

    @classmethod
    def validate(cls, event: EventEnvelope) -> None:
        if not isinstance(event, EventEnvelope):
            raise InvalidEventError("event must be an EventEnvelope instance")
        if not isinstance(event.payload, dict):
            raise InvalidEventError("event payload must be a mapping")
        name = event.payload.get("name") or getattr(event, "name", None)
        if name not in cls._registry:
            raise InvalidEventError(f"unknown event: {name}")

    @classmethod
    def defined_events(cls) -> list[str]:
        return sorted(cls._registry.keys())

    @classmethod
    def canonical_definition(cls, name: str) -> dict[str, Any]:
        if name not in cls._registry:
            raise KeyError(f"unknown event: {name}")
        return cls._registry[name]
