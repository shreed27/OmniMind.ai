from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


logger = logging.getLogger("app.events")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class EventEnvelope(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    name: str = Field(min_length=1)
    payload: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=_utcnow)

    class Config:
        frozen = True

    def emit(self) -> None:
        try:
            logger.info("EVENT %s payload=%s context=%s", self.name, self.payload, self.context)
        except Exception:
            pass

    def to_neo4j_payload(self) -> dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "name": self.name,
            "payload": self.payload,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
        }


def emit(
    name: str,
    payload: dict[str, Any],
    context: dict[str, Any] | None = None,
    *,
    event_id: UUID | None = None,
    mission_id: str | None = None,
    organization_id: str | None = None,
    department_id: str | None = None,
    worker_id: str | None = None,
    trace_id: str | None = None,
    **extra_context: Any,
) -> EventEnvelope:
    from app.core.config import enrich_event_context

    merged = enrich_event_context(context or {})
    if mission_id:
        merged.setdefault("mission_id", mission_id)
    if organization_id:
        merged.setdefault("organization_id", organization_id)
    if department_id:
        merged.setdefault("department_id", department_id)
    if worker_id:
        merged.setdefault("worker_id", worker_id)
    if trace_id:
        merged.setdefault("trace_id", trace_id)
    merged.update(extra_context)
    event = EventEnvelope(
        event_id=event_id or uuid4(),
        name=name,
        payload=payload,
        context=merged,
    )
    event.emit()
    return event
