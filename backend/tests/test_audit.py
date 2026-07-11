from __future__ import annotations

import pytest

from backend.audit.logger import AuditLogger, AuditRecord
from backend.audit.verify import AuditVerify


def test_audit_logger_records_entries() -> None:
    logger = AuditLogger()
    record = logger.record(AuditRecord(action="created", target_type="mission", target_id="mission-1"))
    assert record.audit_id
    assert len(logger.records()) == 1
    assert len(logger.export()) == 1


def test_audit_verify_detects_order_violation() -> None:
    records = [
        {"audit_id": "a1", "created_at": "2025-01-01T00:00:00Z"},
        {"audit_id": "a2", "created_at": "2025-01-02T00:00:00Z"},
        {"audit_id": "a3", "created_at": "2025-01-01T00:00:00Z"},
    ]
    result = AuditVerify.verify(records)
    assert result["valid"] is False
    assert result["entries"] == 3

