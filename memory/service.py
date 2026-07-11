from __future__ import annotations

from typing import Any


class MemoryService:
    def __init__(self) -> None:
        self._memories: dict[str, Any] = {}

    def store(self, key: str, value: Any) -> None:
        self._memories[key] = value

    def get(self, key: str) -> Any | None:
        return self._memories.get(key)
