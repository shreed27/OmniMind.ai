from __future__ import annotations

from typing import Any

from app.core.logging import get_logger
from pydantic import BaseModel, Field

from memory.ports import MemoryPort

logger = get_logger("skill.registry")


class SkillCreate(BaseModel):
    name: str
    description: str | None = None
    owner_department_id: str | None = None
    author: str


class SkillVersionCreate(BaseModel):
    version: str
    manifest: dict[str, Any]
    benchmark: dict[str, Any] | None = None
    created_by: str


class BenchmarkSchema(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    sample_size: int = Field(ge=0)
    target: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class SkillRegistry:
    def __init__(self, *, port: MemoryPort | None = None) -> None:
        self.port = port or MemoryPort()
        self._skills: dict[str, dict[str, Any]] = {}
        self._versions: dict[str, dict[str, dict[str, Any]]] = {}

    async def publish(self, skill_id: str, payload: SkillCreate) -> dict[str, Any]:
        if skill_id in self._skills:
            skill = dict(self._skills[skill_id])
            major, minor, patch = (int(part) for part in skill["version"].split("."))
            next_version = f"{major}.{minor}.{patch + 1}"
        else:
            next_version = "0.1.0"
            self._skills[skill_id] = {
                "skill_id": skill_id,
                "name": payload.name,
                "description": payload.description,
                "owner_department_id": payload.owner_department_id,
                "author": payload.author,
            }
        self._skills[skill_id]["version"] = next_version
        logger.info("published skill %s version %s", skill_id, next_version)
        return self._skills[skill_id]

    async def create_version(self, skill_id: str, payload: SkillVersionCreate) -> dict[str, Any]:
        if payload.benchmark is not None:
            BenchmarkSchema.model_validate(payload.benchmark)
        version = {
            "skill_version_id": f"{skill_id}:{payload.version}",
            "skill_id": skill_id,
            "version": payload.version,
            "manifest": payload.manifest,
            "benchmark": payload.benchmark,
            "created_by": payload.created_by,
        }
        self._versions.setdefault(skill_id, {})[payload.version] = version
        return version

    async def fork(self, source_skill_id: str, target_skill_id: str, author: str) -> dict[str, Any]:
        if source_skill_id not in self._skills:
            raise ValueError("Unknown source skill")
        target = dict(self._skills[source_skill_id])
        target["skill_id"] = target_skill_id
        target["author"] = author
        target.setdefault("parent_skill_id", source_skill_id)
        self._skills[target_skill_id] = target
        return target

    async def get(self, skill_id: str) -> dict[str, Any]:
        return self._skills[skill_id]

    async def versions(self, skill_id: str) -> dict[str, dict[str, Any]]:
        return self._versions.get(skill_id, {})


__all__ = ["BenchmarkSchema", "SkillCreate", "SkillRegistry", "SkillVersionCreate"]
