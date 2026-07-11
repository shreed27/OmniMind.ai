from __future__ import annotations

from typing import Any


class MissionGraphNode:
    def __init__(self, node_id: str, node_type: str, payload: dict[str, Any]) -> None:
        self.node_id = node_id
        self.node_type = node_type
        self.payload = payload
