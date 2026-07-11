from __future__ import annotations

import pytest

from kernel.services.reflection import ReflectionContext, ReflectionOutput, ReflectionService


class FakeMemoryService:
    def __init__(self) -> None:
        self.writes: list[tuple[str, str, dict[str, object]]] = []

    def write(self, scope: str, memory_id: str, value: dict[str, object]) -> dict[str, object]:
        self.writes.append((scope, memory_id, value))
        return value


class FakeKnowledgeGraph:
    def __init__(self) -> None:
        self.nodes: list[tuple[str, list[str], dict[str, object]]] = []

    async def write_node(self, node_id: str, labels: list[str], properties: dict[str, object]) -> dict[str, object]:
        self.nodes.append((node_id, labels, properties))
        return {"status": "queued"}


@pytest.mark.asyncio
async def test_reflection_delegates_to_memory_and_knowledge() -> None:
    memory = FakeMemoryService()
    knowledge = FakeKnowledgeGraph()
    service = ReflectionService(memory_service=memory, knowledge_graph=knowledge)
    payload = ReflectionInput(mission_id="mission-1", result={"status": "ok"})
    output = await service.run(payload)
    assert memory.writes
    assert knowledge.nodes
    assert output.completed_at is not None
    assert output.signature
