from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class EventEnvelope:
    event_id: UUID
    causal_version: str
    timestamp: str
    source: dict[str, Any]
    mission_id: UUID | None
    organization_id: UUID | None
    department_id: UUID | None
    worker_id: UUID | None
    trace_id: UUID
    confidence: float
    payload: dict[str, Any]
    payload_hash: str
    immutable: bool = True

    @staticmethod
    def now(source: dict[str, Any]) -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def ulid_lite() -> str:
        now = datetime.now(timezone.utc)
        return now.strftime("%Y%m%d%H%M%S%f")

    @staticmethod
    def next_id() -> UUID:
        return uuid4()

    def with_ids(
        self,
        *,
        event_id: UUID | None = None,
        mission_id: UUID | None = None,
        organization_id: UUID | None = None,
        department_id: UUID | None = None,
        worker_id: UUID | None = None,
        trace_id: UUID | None = None,
    ) -> EventEnvelope:
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
        )

    @staticmethod
    def create(
        name: str,
        payload: dict[str, Any],
        *,
        mission_id: UUID | None = None,
        organization_id: UUID | None = None,
        department_id: UUID | None = None,
        worker_id: UUID | None = None,
        trace_id: UUID | None = None,
        confidence: float = 0.0,
        source: dict[str, Any] | None = None,
    ) -> EventEnvelope:
        raw = {
            "name": name,
            "mission_id": str(mission_id) if mission_id else None,
            "organization_id": str(organization_id) if organization_id else None,
            "department_id": str(department_id) if department_id else None,
            "worker_id": str(worker_id) if worker_id else None,
            "confidence": confidence,
            "payload": payload,
            "timestamp": EventEnvelope.now(source or {}),
        }
        payload_hash = hashlib.sha256(
            json.dumps(raw, sort_keys=True, default=str).encode("utf-8")
        ).hexdigest()
        return EventEnvelope(
            event_id=EventEnvelope.next_id(),
            causal_version=EventEnvelope.ulid_lite(),
            timestamp=raw["timestamp"],
            source=source or {"service": "kernel", "module": "unknown", "component": "unknown"},
            mission_id=mission_id,
            organization_id=organization_id,
            department_id=department_id,
            worker_id=worker_id,
            trace_id=trace_id or uuid4(),
            confidence=confidence,
            payload=payload,
            payload_hash=payload_hash,
            immutable=True,
        )


