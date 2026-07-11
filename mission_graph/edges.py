from __future__ import annotations

from typing import Any


class Edge:
    def __init__(self, edge_id: str, source: str, target: str, type: str) -> None:
        self.edge_id = edge_id
        self.source = source
        self.target = target
        self.type = type


class EdgeWriter:
    def __init__(self) -> None:
        self._edges: list[Edge] = []

    def append(self, edge: Edge) -> str:
        self._edges.append(edge)
        return edge.edge_id
