from __future__ import annotations

from typing import Any

import pytest

from memory.consolidation import MemoryConsolidation, MemoryRecord, MemoryStore
from memory.ports import MemoryPort
from memory.service import MemoryService


def test_scoped_write_and_read() -> None:
    service = MemoryService()
    record = service.write("mission", "m1", {"content": "alpha"})
    assert record["scope"] == "mission"
    assert service.read("m1")["content"] == "alpha"


def test_invalid_scope_raises() -> None:
    service = MemoryService()
    with pytest.raises(ValueError):
        service.write("unknown", "m1", {"content": "alpha"})


def test_search_is_scope_aware() -> None:
    service = MemoryService()
    service.write("working", "w1", {"content": "alpha"})
    matches = service.search("working", "alpha")
    assert len(matches) == 1
    assert service.search("organization", "alpha") == []


def test_archive_marks_record() -> None:
    service = MemoryService()
    service.write("mission", "m1", {"content": "alpha"})
    service.archive("m1")
    record = service.read("m1")
    assert record["archived"] is True


def test_consolidation_is_idempotent() -> None:
    store = MemoryStore()
    store.write(MemoryRecord(memory_id="a", scope="mission", importance=1.0, content_hash="h1", content={"text": "alpha"}))
    consolidation = MemoryConsolidation(store)
    first_removed = consolidation.deduplicate()
    second_removed = consolidation.deduplicate()
    assert len(first_removed) == 0
    assert second_removed == []


def test_decay_archives_low_importance_memories() -> None:
    store = MemoryStore()
    store.write(MemoryRecord(memory_id="a", scope="mission", importance=0.05, content_hash="h1", content={"text": "alpha"}))
    store.write(MemoryRecord(memory_id="b", scope="mission", importance=0.9, content_hash="h2", content={"text": "beta"}))
    removed = MemoryConsolidation(store).decay()
    assert len(removed) == 1
    assert removed[0].memory_id == "a"


def test_duplicated_hashes_archive_duplicates() -> None:
    store = MemoryStore()
    store.write(MemoryRecord(memory_id="a", scope="mission", importance=1.0, content_hash="h1", content={"text": "alpha"}))
    store.write(MemoryRecord(memory_id="b", scope="mission", importance=1.0, content_hash="h1", content={"text": "alpha"}))
    removed = MemoryConsolidation(store).deduplicate()
    assert {record.memory_id for record in removed} == {"a", "b"}
