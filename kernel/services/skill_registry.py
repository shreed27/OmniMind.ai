from __future__ import annotations

from typing import Any


class Skill:
    def __init__(self, skill_id: str, name: str, version: str = "1.0.0") -> None:
        self.skill_id = skill_id
        self.name = name
        self.version = version


class SkillRegistry:
    def __init__(self) -> None:
        self._skills: dict[str, Skill] = {}

    def register(self, skill: Skill) -> None:
        self._skills[skill.skill_id] = skill

    def get(self, skill_id: str) -> Skill | None:
        return self._skills.get(skill_id)
