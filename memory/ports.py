from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class MemoryPort(ABC):
    @abstractmethod
    def write(self, scope: str, memory_id: str, value: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def read(self, memory_id: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def search(self, scope: str, query: str) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def archive(self, memory_id: str) -> None:
        raise NotImplementedError
