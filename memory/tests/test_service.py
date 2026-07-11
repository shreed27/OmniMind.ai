import pytest
from memory.service import MemoryService


def test_memory_service_store_and_get() -> None:
    service = MemoryService()
    service.store("key", {"value": 1})
    assert service.get("key") == {"value": 1}
