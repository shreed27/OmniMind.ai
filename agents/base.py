from __future__ import annotations

from abc import ABC, abstractmethod


class BaseAgent(ABC):
    @abstractmethod
    async def execute(self, task: dict[str, object]) -> dict[str, object]:
        ...
