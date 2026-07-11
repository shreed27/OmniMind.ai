from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Protocol, runtime_checkable


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
        payload_hash = hashlib.sha256(json.dumps(raw, sort_keys=True, default=str).encode()).hexdigest()
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
            payload_hash=payload_hash,
            immutable=True,
            context={},
            name=name,
        )


@runtime_checkable
class EventBus(Protocol):
    def publish(self, event: EventEnvelope) -> str:
        ...

    def subscribe(self, event_name: str, handler: Callable[[EventEnvelope], None]) -> str:
        ...

    def disconnect(self) -> None:
        ...
