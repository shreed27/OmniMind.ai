from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Sequence

logger = logging.getLogger("kernel.reflection")


@dataclass
class ReflectionContext:
    mission_id: str
    organization_id: str | None = None
    department_id: str | None = None
    worker_id: str | None = None
    trace_id: str | None = None


@dataclass
class ReflectionInput:
    context: ReflectionContext
    evidence: dict[str, Any] = field(default_factory=dict)
    artifacts: Sequence[dict[str, Any]] = field(default_factory=tuple)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ReflectionOutput:
    context: ReflectionContext
    lessons: list[dict[str, Any]] = field(default_factory=list)
    knowledge: list[dict[str, Any]] = field(default_factory=list)
    skills: list[dict[str, Any]] = field(default_factory=list)
    recommendations: list[dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    signature: str | None = None

    def mark_completed(self) -> None:
        self.completed_at = datetime.now(timezone.utc)
        payload = {
            "mission_id": self.context.mission_id,
            "lessons": self.lessons,
            "knowledge": self.knowledge,
            "skills": self.skills,
            "recommendations": self.recommendations,
            "confidence": self.confidence,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat(),
        }
        self.signature = hashlib.sha256(
            __import__("json").dumps(payload, sort_keys=True).encode("utf-8")
        ).hexdigest()


class ReflectionService:
    async def run(self, reflection_input: ReflectionInput) -> ReflectionOutput:
        logger.info(
            "ReflectionStarted mission_id=%s org=%s dept=%s worker=%s",
            reflection_input.context.mission_id,
            reflection_input.context.organization_id,
            reflection_input.context.department_id,
            reflection_input.context.worker_id,
        )

        output = ReflectionOutput(context=reflection_input.context)
        output.lessons = self._extract_lessons(reflection_input)
        output.knowledge = self._generate_knowledge(reflection_input, output.lessons)
        output.skills = self._generate_skills(reflection_input, output.lessons)
        output.recommendations = self._build_recommendations(reflection_input, output)
        output.confidence = self._score(reflection_input, output)
        output.mark_completed()

        logger.info(
            "ReflectionCompleted mission_id=%s confidence=%.3f lessons=%d knowledge=%d skills=%d",
            output.context.mission_id,
            output.confidence,
            len(output.lessons),
            len(output.knowledge),
            len(output.skills),
        )
        return output

    def _extract_lessons(self, reflection_input: ReflectionInput) -> list[dict[str, Any]]:
        lessons: list[dict[str, Any]] = []
        evidence = reflection_input.evidence or {}
        failures = evidence.get("failures") or []
        successes = evidence.get("successes") or []
        for failure in failures:
            lessons.append(
                {
                    "type": "failure",
                    "source": failure.get("source"),
                    "summary": failure.get("summary") or "Failure observed during execution.",
                    "confidence": float(failure.get("confidence", 0.0)),
                }
            )
        for success in successes:
            lessons.append(
                {
                    "type": "success",
                    "source": success.get("source"),
                    "summary": success.get("summary") or "Successful execution pattern observed.",
                    "confidence": float(success.get("confidence", 1.0)),
                }
            )
        if not lessons:
            lessons.append(
                {
                    "type": "neutral",
                    "source": "system",
                    "summary": "No notable evidence found; record baseline lesson.",
                    "confidence": 0.5,
                }
            )
        return lessons

    def _generate_knowledge(
        self,
        reflection_input: ReflectionInput,
        lessons: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        seen: set[str] = set()
        for lesson in lessons:
            summary = lesson.get("summary") or ""
            evidence_id = __import__("hashlib").sha256(summary.encode("utf-8")).hexdigest()[:12]
            if evidence_id in seen:
                continue
            seen.add(evidence_id)
            items.append(
                {
                    "knowledge_id": f"kg-{reflection_input.context.mission_id}-{evidence_id}",
                    "source": lesson.get("source") or "reflection",
                    "statement": summary,
                    "confidence": float(lesson.get("confidence", 0.0)),
                    "lesson_ref": lesson,
                }
            )
        return items

    def _generate_skills(
        self,
        reflection_input: ReflectionInput,
        lessons: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        skills: list[dict[str, Any]] = []
        for lesson in lessons:
            if lesson.get("confidence", 0.0) < 0.0:
                continue
            skill_name = lesson.get("source") or "generalized-skill"
            skills.append(
                {
                    "name": f"learned-{skill_name}-v1",
                    "description": lesson.get("summary") or "Generalized reusable skill.",
                    "version": "0.1.0",
                    "status": "draft",
                    "author": "reflection",
                    "source_lesson": lesson,
                }
            )
        return skills

    def _build_recommendations(
        self,
        reflection_input: ReflectionInput,
        output: ReflectionOutput,
    ) -> list[dict[str, Any]]:
        recommendations: list[dict[str, Any]] = []
        if any(lesson.get("type") == "failure" for lesson in output.lessons):
            recommendations.append(
                {
                    "action": "review_failure_patterns",
                    "priority": "high",
                    "owner": "manager",
                    "summary": "Review failure patterns and propose mitigations before next execution.",
                }
            )
        if output.skills:
            recommendations.append(
                {
                    "action": "publish_skills",
                    "priority": "medium",
                    "owner": "kernel",
                    "summary": "Publish learned skills to skill registry after review.",
                }
            )
        return recommendations

    def _score(self, reflection_input: ReflectionInput, output: ReflectionOutput) -> float:
        score = 0.5
        score += 0.1 * min(len(output.lessons), 10) / 10
        score += 0.2 * min(len(output.knowledge), 5) / 5
        score += 0.2 * min(len(output.skills), 5) / 5
        failures = sum(1 for lesson in output.lessons if lesson.get("type") == "failure")
        score -= 0.15 * min(failures, 4) / 4
        return round(max(0.0, min(1.0, score)), 4)
