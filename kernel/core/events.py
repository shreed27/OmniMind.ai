from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class EventEnvelope:
    event_id: UUID
    name: str
    payload: dict[str, Any]
    context: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.timestamp:
            object.__setattr__(self, "timestamp", _utcnow())

    timestamp: datetime = field(default_factory=_utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "name": self.name,
            "payload": self.payload,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True)
class MessageEnvelope:
    source: str
    name: str
    payload: dict[str, Any]
    context: dict[str, Any] = field(default_factory=dict)
