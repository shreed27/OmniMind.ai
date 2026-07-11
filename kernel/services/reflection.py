from __future__ import annotations


class ReflectionInput:
    def __init__(self, mission_id: str, result: dict[str, object]) -> None:
        self.mission_id = mission_id
        self.result = result


class ReflectionOutput:
    def __init__(self, lessons: list[str], knowledge: list[str], skills: list[str], recommendations: list[str], confidence: float) -> None:
        self.lessons = lessons
        self.knowledge = knowledge
        self.skills = skills
        self.recommendations = recommendations
        self.confidence = confidence


class ReflectionService:
    async def run(self, payload: ReflectionInput) -> ReflectionOutput:
        return ReflectionOutput(
            lessons=["lesson"],
            knowledge=["knowledge"],
            skills=["skill"],
            recommendations=["recommendation"],
            confidence=0.9,
        )
