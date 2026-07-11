from __future__ import annotations

import asyncio
from typing import Any
from memory.ports import MemoryPort
from memory.knowledge import KnowledgeGraph


class DefaultMemoryPort(MemoryPort):
    def __init__(self) -> None:
        self.records: dict[str, dict[str, Any]] = {}

    def write(self, scope: str, memory_id: str, value: dict[str, Any]) -> dict[str, Any]:
        record = dict(value)
        record.update({"memory_id": memory_id, "scope": scope, "archived": False})
        self.records[memory_id] = record
        return record

    def read(self, memory_id: str) -> dict[str, Any]:
        return self.records.get(memory_id, {"memory_id": memory_id, "archived": False})

    def search(self, scope: str, query: str) -> list[dict[str, Any]]:
        results = []
        for record in self.records.values():
            if record.get("scope") == scope:
                content = record.get("content", "")
                if query in str(content) or query in str(record):
                    results.append(record)
        return results

    def archive(self, memory_id: str) -> None:
        if memory_id in self.records:
            self.records[memory_id]["archived"] = True


class MemoryService:
    def __init__(self, port: MemoryPort | None = None) -> None:
        self.port = port or DefaultMemoryPort()
        self.knowledge = KnowledgeGraph()
        self._memories: dict[str, Any] = {}

    def store(self, key: str, value: Any) -> None:
        self._memories[key] = value

    def get(self, key: str) -> Any | None:
        return self._memories.get(key)

    def write(self, scope: str, memory_id: str, value: dict[str, Any]) -> dict[str, Any]:
        allowed_scopes = {"mission", "organization", "department", "working", "specialist"}
        if scope not in allowed_scopes:
            raise ValueError(f"Invalid scope: {scope}")
        return self.port.write(scope, memory_id, value)

    def read(self, memory_id: str) -> dict[str, Any]:
        return self.port.read(memory_id)

    def search(self, scope: str, query: str) -> list[dict[str, Any]]:
        return self.port.search(scope, query)

    def archive(self, memory_id: str) -> None:
        self.port.archive(memory_id)

    async def write_knowledge(self, node_id: str, labels: list[str], properties: dict[str, Any]) -> dict[str, Any]:
        return await self.knowledge.write_node(node_id, labels, properties)


class MemoryQuery:
    def __init__(self, service: MemoryService) -> None:
        self.service = service

    def by_scope(self, scope: str, query: str) -> list[dict[str, Any]]:
        results = self.service.search(scope, query)
        mapped = []
        for r in results:
            item = {
                "memory_id": r.get("memory_id"),
                "scope": r.get("scope"),
            }
            if "content" in r:
                item["content"] = r["content"]
            elif "value" in r:
                item["content"] = r.get("value", {}).get("content")
            mapped.append(item)
        return mapped
