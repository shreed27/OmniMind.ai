from __future__ import annotations

from typing import Any

import pytest

from memory.consolidation import MemoryConsolidation, MemoryRecord, MemoryStore
from memory.knowledge import KnowledgeGraph
from memory.ports import MemoryPort
from memory.service import MemoryService, MemoryQuery


class RecordingMemoryPort(MemoryPort):
    def __init__(self) -> None:
        self.records: dict[str, dict[str, Any]] = {}
        self.events: list[dict[str, Any]] = []

    def write(self, scope: str, memory_id: str, value: dict[str, Any]) -> dict[str, Any]:
        record = dict(value)
        record.update({"memory_id": memory_id, "scope": scope})
        self.records[memory_id] = record
        self.events.append({"name": "MemoryWritten", "scope": scope, "memory_id": memory_id})
        return record

    def read(self, memory_id: str) -> dict[str, Any]:
        return dict(self.records.get(memory_id, {"memory_id": memory_id, "archived": False}))

    def search(self, scope: str, query: str) -> list[dict[str, Any]]:
        return [record for record in self.records.values() if record.get("scope") == scope]

    def archive(self, memory_id: str) -> None:
        self.records[memory_id]["archived"] = True
        self.events.append({"name": "MemoryArchived", "memory_id": memory_id})


@pytest.fixture()
def memory_service() -> MemoryService:
    return MemoryService(port=RecordingMemoryPort())


def test_write_and_read(memory_service: MemoryService) -> None:
    record = memory_service.write("mission", "m1", {"content": "alpha"})
    assert memory_service.read("m1")["content"] == "alpha"
    assert record["scope"] == "mission"


def test_search_is_scope_aware(memory_service: MemoryService) -> None:
    memory_service.write("working", "w1", {"content": "alpha"})
    assert len(memory_service.search("working", "alpha")) == 1
    assert memory_service.search("organization", "alpha") == []


def test_archive_marks_record(memory_service: MemoryService) -> None:
    memory_service.write("mission", "m1", {"content": "alpha"})
    memory_service.archive("m1")
    assert memory_service.read("m1")["archived"] is True


def test_knowledge_write_delegates(memory_service: MemoryService) -> None:
    result = asyncio.run(memory_service.write_knowledge("n1", ["Mission"], {"name": "Demo"}))
    assert result["status"] == "queued"


def test_memory_query_delegates(memory_service: MemoryService) -> None:
    memory_service.write("mission", "m1", {"content": "alpha"})
    assert MemoryQuery(memory_service).by_scope("mission", "alpha") == [{"memory_id": "m1", "scope": "mission", "content": "alpha"}]
