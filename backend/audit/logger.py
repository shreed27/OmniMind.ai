from __future__ import annotations

import logging
import uuid

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Sequence

logger = logging.getLogger("audit.logger")


@dataclass(frozen=True)
class AuditRecord:
    audit_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    actor_id: str | None = None
    action: str = ""
    target_type: str = ""
    target_id: str = ""
    before: dict[str, Any] | None = None
    after: dict[str, Any] | None = None
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    immutable: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "audit_id": self.audit_id,
            "actor_id": self.actor_id,
            "action": self.action,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "before": self.before,
            "after": self.after,
            "trace_id": self.trace_id,
            "created_at": self.created_at.isoformat(),
            "immutable": self.immutable,
        }


class AuditLogger:
    def __init__(self) -> None:
        self._records: list[AuditRecord] = []

    def record(self, record: AuditRecord) -> AuditRecord:
        logger.info(
            "AuditRecorded action=%s target=%s/%s trace_id=%s",
            record.action,
            record.target_type,
            record.target_id,
            record.trace_id,
        )
        self._records.append(record)
        return record

    def records(self) -> list[dict[str, Any]]:
        return [record.to_dict() for record in self._records]

    def export(self) -> list[dict[str, Any]]:
        return [record.to_dict() for record in self._records]
