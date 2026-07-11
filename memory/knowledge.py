from __future__ import annotations

from typing import Any

import neo4j

from app.db.neo4j import get_neo4j_driver
from app.core.events import emit
from app.core.logging import get_logger

from memory.ports import MemoryPort

logger = get_logger("memory.knowledge")


class KnowledgeGraph:
    def __init__(self, *, port: MemoryPort | None = None, collection: str = "knowledge") -> None:
        self.port = port or MemoryPort()
        self.collection = collection

    async def write_node(self, node_id: str, labels: list[str], properties: dict[str, Any]) -> dict[str, Any]:
        return await self._write_graph(operation="write_node", target=node_id, labels=labels, properties=properties)

    async def write_edge(self, source_id: str, target_id: str, relationship: str, properties: dict[str, Any] | None = None) -> dict[str, Any]:
        return await self._write_graph(
            operation="write_edge",
            target=f"{source_id}:{relationship}:{target_id}",
            labels=[],
            properties=properties or {},
            source_id=source_id,
            target_id=target_id,
            relationship=relationship,
        )

    async def search(self, query: str, *, limit: int = 10) -> list[dict[str, Any]]:
        return await self._search_graph(query=query, limit=limit)

    async def invalidate_embeddings(self, node_id: str) -> None:
        await self._invalidate_embeddings(node_id=node_id)

    async def _write_graph(self, **kwargs: Any) -> dict[str, Any]:
        payload = {
            "operation": kwargs.get("operation"),
            "collection": self.collection,
            "labels": kwargs.get("labels", []),
            "properties": kwargs.get("properties", {}),
        }
        for key in ("target", "source_id", "target_id", "relationship"):
            if key in kwargs:
                payload[key] = kwargs[key]
        emit("KnowledgeWritten", payload, {"collection": self.collection})
        logger.info("knowledge write %s", payload)
        return {"status": "queued", "payload": payload}

    async def _search_graph(self, *, query: str, limit: int) -> list[dict[str, Any]]:
        payload = {"query": query, "limit": limit, "collection": self.collection}
        emit("KnowledgeSearched", payload, {"collection": self.collection})
        logger.info("knowledge search %s", payload)
        return [{"node_id": "demo-node", "score": 0.99, "collection": self.collection}]

    async def _invalidate_embeddings(self, *, node_id: str) -> None:
        payload = {"node_id": node_id, "collection": self.collection}
        emit("EmbeddingInvalidated", payload, {"collection": self.collection})
        logger.info("embedding invalidated %s", payload)
        return None


__all__ = ["KnowledgeGraph"]
