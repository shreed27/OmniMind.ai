from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class ReflectionInput:
    mission_id: str
    result: dict[str, Any]


# Alias for backward compatibility
ReflectionContext = ReflectionInput


@dataclass
class ReflectionOutput:
    lessons: list[str]
    knowledge: list[str]
    skills: list[str]
    recommendations: list[str]
    confidence: float
    completed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    signature: str = "reflection-sig"


class ReflectionService:
    def __init__(self, memory_service: Any = None, knowledge_graph: Any = None) -> None:
        self.memory_service = memory_service
        self.knowledge_graph = knowledge_graph

    async def run(self, payload: ReflectionInput) -> ReflectionOutput:
        if self.memory_service:
            self.memory_service.write("mission", f"reflection-{payload.mission_id}", {"result": payload.result})
        if self.knowledge_graph:
            await self.knowledge_graph.write_node(f"reflection-{payload.mission_id}", ["Reflection"], {"mission_id": payload.mission_id})
        return ReflectionOutput(
            lessons=["lesson"],
            knowledge=["knowledge"],
            skills=["skill"],
            recommendations=["recommendation"],
            confidence=0.9,
        )
