from __future__ import annotations

from typing import Any


class MissionGraphReader:
    def __init__(self, writer: Any) -> None:
        self._writer = writer

    def timeline(self, mission_id: str) -> list[Any]:
        return list(self._writer._nodes.values())

    def lineage(self, node_id: str, limit: int = 12) -> list[Any]:
        return []
