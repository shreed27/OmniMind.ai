from __future__ import annotations

from typing import Any


class MissionGraphWriter:
    def __init__(self) -> None:
        self._nodes: dict[str, Any] = {}

    def append(self, node: Any) -> str:
        self._nodes[node.node_id] = node
        return node.node_id
