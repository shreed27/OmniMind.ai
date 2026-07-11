from __future__ import annotations

import asyncio
from typing import Any

from app.core.events import emit
from app.core.logging import get_logger
from memory.knowledge import KnowledgeGraph
from pydantic import BaseModel

from memory.service import MemoryService, MemoryQuery

logger = get_logger("memory.service")


class MemoryQuery:
    def __init__(self, service: MemoryService) -> None:
        self.service = service

    def by_scope(self, scope: str, query: str) -> list[dict[str, Any]]:
        return self.service.search(scope, query)


class MemoryService:
    def __init__(
        self,
        *,
        port: Any | None = None,
        knowledge_graph: KnowledgeGraph | None = None,
        store: Any | None = None,
    ) -> None:
        self.store = store
        self.knowledge_graph = knowledge_graph or KnowledgeGraph()
        self.port = port

    def write(self, scope: str, memory_id: str, value: dict[str, Any]) -> dict[str, Any]:
        if self.port is not None:
            self.port.write(scope, memory_id, value)
        return value

    def read(self, memory_id: str) -> dict[str, Any]:
        if self.port is not None:
            return self.port.read(memory_id)
        raise ValueError("memory port not configured")

    def search(self, scope: str, query: str) -> list[dict[str, Any]]:
        if self.port is not None:
            return self.port.search(scope, query)
        return []

    def archive(self, memory_id: str) -> None:
        if self.port is not None:
            self.port.archive(memory_id)

    async def consolidation(self) -> None:
        logger.info("memory consolidation scheduled")

    async def write_knowledge(self, node_id: str, labels: list[str], properties: dict[str, Any]) -> dict[str, Any]:
        return await self.knowledge_graph.write_node(node_id, labels, properties)


__all__ = ["MemoryQuery", "MemoryService"]
