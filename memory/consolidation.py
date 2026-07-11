from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MemoryRecord:
    memory_id: str
    scope: str
    importance: float
    content_hash: str
    content: dict[str, Any]
    archived: bool = False


class MemoryStore:
    def __init__(self) -> None:
        self.records: dict[str, MemoryRecord] = {}

    def write(self, record: MemoryRecord) -> None:
        self.records[record.memory_id] = record

    def read(self, memory_id: str) -> MemoryRecord | None:
        return self.records.get(memory_id)

    def all(self) -> list[MemoryRecord]:
        return list(self.records.values())


class MemoryConsolidation:
    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    def deduplicate(self) -> list[MemoryRecord]:
        all_records = self.store.all()
        seen_hashes: dict[str, list[MemoryRecord]] = {}
        for record in all_records:
            if not record.archived:
                seen_hashes.setdefault(record.content_hash, []).append(record)

        removed: list[MemoryRecord] = []
        for content_hash, records in seen_hashes.items():
            if len(records) > 1:
                for record in records:
                    record.archived = True
                    removed.append(record)
        return removed

    def decay(self) -> list[MemoryRecord]:
        all_records = self.store.all()
        removed: list[MemoryRecord] = []
        for record in all_records:
            if not record.archived and record.importance < 0.1:
                record.archived = True
                removed.append(record)
        return removed
