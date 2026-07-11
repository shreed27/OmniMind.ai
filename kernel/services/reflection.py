from __future__ import annotations

from typing import Any

from app.core.events import emit
from app.core.logging import get_logger
from pydantic import BaseModel

from memory.ports import MemoryPort

logger = get_logger("reflection.service")


class ReflectionInput(BaseModel):
    mission_id: str
    department_id: str | None = None
    worker_id: str | None = None
    result: dict[str, Any]


class ReflectionOutput(BaseModel):
    lessons: list[dict[str, Any]]
    knowledge: list[dict[str, Any]]
    skills: list[dict[str, Any]]
    recommendations: list[dict[str, Any]]


class ReflectionService:
    def __init__(self, *, memory_service: Any = None, knowledge_graph: Any = None) -> None:
        self.memory_service = memory_service
        self.knowledge_graph = knowledge_graph

    async def run(self, payload: ReflectionInput) -> ReflectionOutput:
        lessons = [{"text": "Lesson 1", "confidence": 0.9}]
        knowledge = [{"title": "Knowledge 1"}]
        skills = [{"name": "Skill 1"}]
        recommendations = [{"title": "Recommendation 1"}]
        if self.memory_service is not None:
            self.memory_service.write("mission", f"reflection:{payload.mission_id}", {"type": "reflection", "lessons": lessons})
        if self.knowledge_graph is not None:
            await self.knowledge_graph.write_node(f"reflection:{payload.mission_id}", ["Reflection"], {"mission_id": payload.mission_id})
        emit(
            "ReflectionCompleted",
            {
                "mission_id": payload.mission_id,
                "department_id": payload.department_id,
                "worker_id": payload.worker_id,
                "lessons": lessons,
                "knowledge": knowledge,
                "skills": skills,
                "recommendations": recommendations,
            },
            {"mission_id": payload.mission_id},
        )
        return ReflectionOutput(lessons=lessons, knowledge=knowledge, skills=skills, recommendations=recommendations)


__all__ = ["ReflectionInput", "ReflectionOutput", "ReflectionService"]
