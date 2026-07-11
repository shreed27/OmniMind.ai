from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine


@dataclass(frozen=True, slots=True)
class EventEnvelope:
    event_id: str
    causal_version: str
    timestamp: str
    source: dict[str, Any]
    mission_id: str | None
    organization_id: str | None
    department_id: str | None
    worker_id: str | None
    trace_id: str
    confidence: float
    payload: dict[str, Any]
    payload_hash: str
    immutable: bool = True
    context: dict[str, Any] = field(default_factory=dict)
    name: str = ""

    def with_ids(
        self,
        *,
        event_id: str | None = None,
        mission_id: str | None = None,
        organization_id: str | None = None,
        department_id: str | None = None,
        worker_id: str | None = None,
        trace_id: str | None = None,
    ) -> "EventEnvelope":
        return EventEnvelope(
            event_id=event_id or self.event_id,
            causal_version=self.causal_version,
            timestamp=self.timestamp,
            source=self.source,
            mission_id=mission_id if mission_id is not None else self.mission_id,
            organization_id=organization_id if organization_id is not None else self.organization_id,
            department_id=department_id if department_id is not None else self.department_id,
            worker_id=worker_id if worker_id is not None else self.worker_id,
            trace_id=trace_id or self.trace_id,
            confidence=self.confidence,
            payload=self.payload,
            payload_hash=self.payload_hash,
            immutable=self.immutable,
            context=self.context,
            name=self.name,
        )

    @classmethod
    def create(
        cls,
        name: str,
        payload: dict[str, Any],
        *,
        mission_id: str | None = None,
        organization_id: str | None = None,
        department_id: str | None = None,
        worker_id: str | None = None,
        trace_id: str | None = None,
        confidence: float = 0.0,
        source: dict[str, Any] | None = None,
    ) -> "EventEnvelope":
        from datetime import datetime, timezone
        from uuid import uuid4
        import hashlib
        import json

        source = source or {"service": "kernel", "module": "unknown", "component": "unknown"}
        timestamp = datetime.now(timezone.utc).isoformat()
        raw = {
            "name": name,
            "mission_id": mission_id,
            "organization_id": organization_id,
            "department_id": department_id,
            "worker_id": worker_id,
            "confidence": confidence,
            "payload": payload,
            "timestamp": timestamp,
            "source": source,
        }
        return cls(
            event_id=str(uuid4()),
            causal_version=datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f"),
            timestamp=timestamp,
            source=source,
            mission_id=mission_id,
            organization_id=organization_id,
            department_id=department_id,
            worker_id=worker_id,
            trace_id=trace_id or str(uuid4()),
            confidence=confidence,
            payload=payload,
            payload_hash=hashlib.sha256(json.dumps(raw, sort_keys=True, default=str).encode()).hexdigest(),
            immutable=True,
            context={},
            name=name,
        )


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable[["EventEnvelope"], None]]] = {}
        self._history: list[EventEnvelope] = []

    async def publish(self, event: EventEnvelope) -> str:
        from kernel.core.event_registry import EventRegistry
        EventRegistry.validate(event)
        key = event.name or event.payload.get("name") or "unknown"
        for handler in list(self._subscribers.get(key, [])):
            result = handler(event)
            if hasattr(result, "__await__"):
                await result
        self._history.append(event)
        return event.causal_version

    def subscribe(self, event_name: str, handler: Callable[["EventEnvelope"], None]) -> str:
        self._subscribers.setdefault(event_name, []).append(handler)
        return event_name

    def disconnect(self) -> None:
        self._subscribers.clear()

    def history(self) -> list[EventEnvelope]:
        return list(self._history)
