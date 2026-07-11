from __future__ import annotations

from dataclasses import dataclass

from memory.ports import MemoryPort


@dataclass
class MemoryRecord:
    memory_id: str
    scope: str
    importance: float = 1.0
    confidence: float = 1.0
    content_hash: str = ""
    archived: bool = False
    content: dict[str, object] | None = None


class MemoryStore:
    def __init__(self, *, port: MemoryPort | None = None) -> None:
        self._records: dict[str, MemoryRecord] = {}
        self._seen_hashes: set[str] = set()
        self.port = port or MemoryPort()

    def write(self, record: MemoryRecord) -> MemoryRecord:
        if record.content_hash and record.content_hash in self._seen_hashes:
            record.archived = True
            return record
        self._records[record.memory_id] = record
        if record.content_hash:
            self._seen_hashes.add(record.content_hash)
        return record


class MemoryConsolidation:
    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    def decay(self, minimum_importance: float = 0.1) -> list[MemoryRecord]:
        removed = []
        for record in self.store._records.values():
            if record.importance < minimum_importance:
                record = MemoryStore.write(self.store, record)
                record.archived = True
                removed.append(record)
        return removed

    def deduplicate(self) -> list[MemoryRecord]:
        seen: dict[str, MemoryRecord] = {}
        removed = []
        for record in self.store._records.values():
            key = record.content_hash
            if not key:
                continue
            if key in seen:
                seen[key].archived = True
                removed.append(seen[key])
            else:
                seen[key] = record
        return removed


__all__ = [
    "ConsolidationReport",
    "MemoryConsolidation",
    "MemoryRecord",
    "MemoryStore",
]
