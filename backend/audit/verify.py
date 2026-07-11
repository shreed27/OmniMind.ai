from __future__ import annotations

import logging
from typing import Any, Sequence

logger = logging.getLogger("audit.verify")


class AuditVerify:
    @staticmethod
    def verify(records: Sequence[dict[str, Any]]) -> dict[str, Any]:
        if not records:
            return {"valid": True, "entries": 0, "violations": []}
        sorted_records = sorted(records, key=lambda item: item.get("created_at") or "", reverse=False)
        removed_or_reordered = []
        for index, record in enumerate(sorted_records):
            original_index = records.index(record)
            if original_index != index:
                removed_or_reordered.append(
                    {"audit_id": record.get("audit_id"), "original_index": original_index, "current_index": index}
                )
        violations = []
        if removed_or_reordered:
            violations.append({"type": "order_violation", "details": removed_or_reordered})
        return {"valid": not bool(violations), "entries": len(sorted_records), "violations": violations}
