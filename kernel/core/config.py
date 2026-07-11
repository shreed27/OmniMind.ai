from __future__ import annotations

from typing import Any


class ConfigStore:
    def __init__(self, values: dict[str, Any] | None = None) -> None:
        self.values: dict[str, Any] = values or {}

    def set(self, key: str, value: Any) -> None:
        self.values[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.values.get(key, default)
