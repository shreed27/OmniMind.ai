from __future__ import annotations

from typing import Any

import pytest
from neo4j import AsyncGraphDatabase

from app.db.redis import create_redis, ping
from app.db.qdrant import create_qdrant, ensure_collection


@pytest.mark.asyncio
async def test_redis_connection(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/1")
    client = create_redis("redis://localhost:6379/1")
    assert await ping(client) is False
    await client.aclose()


def test_qdrant_ensure_collection() -> None:
    client = create_qdrant("http://localhost:6333")
    ensure_collection(client, "test-scope", vector_size=192)
    collections = client.get_collections().collections
    assert any(collection.name == "test-scope" for collection in collections)
