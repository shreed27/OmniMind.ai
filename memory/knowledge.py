from __future__ import annotations

from typing import Any


class KnowledgeGraph:
    async def write_node(self, node_id: str, labels: list[str], properties: dict[str, Any]) -> dict[str, Any]:
        return {"status": "queued"}

    async def write_edge(self, source_id: str, target_id: str, rel_type: str) -> dict[str, Any]:
        return {"status": "queued"}

    async def search(self, query: str) -> list[str]:
        return ["candidate"]

    async def invalidate_embeddings(self, node_id: str) -> None:
        pass
