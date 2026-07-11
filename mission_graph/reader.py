"""
Mission Graph Query Layer - TASK-4.3

Comprehensive read model for timeline, lineage, branch resolution,
path finding, pattern matching, and temporal queries.
"""

from __future__ import annotations

from collections import deque
from datetime import datetime
from typing import Any

from mission_graph.node import MissionGraphNode


class MissionGraphReader:
    """
    Mission Graph query layer.

    Provides read-only access to the Mission Graph with:
    - Timeline queries (causal order)
    - Lineage queries (bounded depth)
    - Branch head resolution
    - Path finding between nodes
    - Pattern matching
    - Temporal queries
    - Confidence filtering
    """

    def __init__(self, writer: Any) -> None:
        self._writer = writer

    def timeline(
        self,
        mission_id: str,
        *,
        from_timestamp: str | None = None,
        to_timestamp: str | None = None,
        node_types: list[str] | None = None,
        min_confidence: float | None = None,
    ) -> list[MissionGraphNode]:
        """
        Get mission timeline in causal order.

        Args:
            mission_id: Mission to query
            from_timestamp: Start timestamp (inclusive)
            to_timestamp: End timestamp (inclusive)
            node_types: Filter by node types
            min_confidence: Minimum confidence threshold

        Returns:
            List of nodes in chronological order
        """
        nodes = [
            node
            for node in self._writer._nodes.values()
            if node.payload.get("mission_id") == mission_id
        ]

        # Filter by timestamp range
        if from_timestamp:
            nodes = [
                n for n in nodes if n.payload.get("timestamp", "") >= from_timestamp
            ]

        if to_timestamp:
            nodes = [n for n in nodes if n.payload.get("timestamp", "") <= to_timestamp]

        # Filter by node types
        if node_types:
            nodes = [n for n in nodes if n.node_type in node_types]

        # Filter by confidence
        if min_confidence is not None:
            nodes = [
                n for n in nodes if n.payload.get("confidence", 0.0) >= min_confidence
            ]

        # Sort by timestamp (causal order)
        nodes.sort(key=lambda n: n.payload.get("timestamp", ""))

        return nodes

    def lineage(
        self,
        node_id: str,
        *,
        max_depth: int = 12,
        direction: str = "backward",
        edge_types: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get node lineage with bounded depth.

        Args:
            node_id: Starting node
            max_depth: Maximum depth (default 12 per registry)
            direction: "backward" (dependencies) or "forward" (dependents)
            edge_types: Filter by specific edge types

        Returns:
            List of lineage entries with depth information
        """
        if node_id not in self._writer._nodes:
            return []

        lineage = []
        visited = set()
        queue = deque([(node_id, 0)])  # (node_id, depth)

        edge_writer = self._writer._edge_writer if hasattr(self._writer, "_edge_writer") else None

        while queue:
            current_id, depth = queue.popleft()

            if current_id in visited or depth > max_depth:
                continue

            visited.add(current_id)

            if current_id in self._writer._nodes:
                node = self._writer._nodes[current_id]
                lineage.append(
                    {
                        "node_id": current_id,
                        "node_type": node.node_type,
                        "depth": depth,
                        "payload": node.payload,
                    },
                )

                # Find connected edges
                if edge_writer:
                    connected_edges = []

                    for edge in edge_writer._edges:
                        if direction == "backward" and edge.target == current_id:
                            if not edge_types or edge.type in edge_types:
                                connected_edges.append(edge.source)
                        elif direction == "forward" and edge.source == current_id:
                            if not edge_types or edge.type in edge_types:
                                connected_edges.append(edge.target)

                    for next_id in connected_edges:
                        if next_id not in visited and depth + 1 <= max_depth:
                            queue.append((next_id, depth + 1))

        return lineage

    def branch_head(
        self,
        mission_id: str,
        branch_name: str = "main",
    ) -> MissionGraphNode | None:
        """
        Get latest approved node on branch.

        Args:
            mission_id: Mission ID
            branch_name: Branch name (default "main")

        Returns:
            Latest approved node or None
        """
        # Filter nodes by mission and branch
        branch_nodes = [
            node
            for node in self._writer._nodes.values()
            if node.payload.get("mission_id") == mission_id
            and node.payload.get("branch", "main") == branch_name
            and node.payload.get("approved", False) is True
        ]

        if not branch_nodes:
            return None

        # Return latest node by timestamp
        branch_nodes.sort(key=lambda n: n.payload.get("timestamp", ""), reverse=True)
        return branch_nodes[0]

    def find_path(
        self,
        from_node_id: str,
        to_node_id: str,
        *,
        max_depth: int = 12,
        edge_types: list[str] | None = None,
    ) -> list[str] | None:
        """
        Find path between two nodes.

        Args:
            from_node_id: Start node
            to_node_id: Target node
            max_depth: Maximum path length
            edge_types: Filter by edge types

        Returns:
            List of node IDs forming the path, or None if no path exists
        """
        if from_node_id not in self._writer._nodes or to_node_id not in self._writer._nodes:
            return None

        edge_writer = self._writer._edge_writer if hasattr(self._writer, "_edge_writer") else None
        if not edge_writer:
            return None

        # BFS to find shortest path
        queue = deque([(from_node_id, [from_node_id])])
        visited = {from_node_id}

        while queue:
            current_id, path = queue.popleft()

            if current_id == to_node_id:
                return path

            if len(path) >= max_depth:
                continue

            # Find neighbors
            for edge in edge_writer._edges:
                next_id = None

                if edge.source == current_id:
                    if not edge_types or edge.type in edge_types:
                        next_id = edge.target

                if next_id and next_id not in visited:
                    visited.add(next_id)
                    queue.append((next_id, path + [next_id]))

        return None  # No path found

    def pattern_match(
        self,
        mission_id: str,
        pattern: dict[str, Any],
    ) -> list[MissionGraphNode]:
        """
        Match nodes by pattern.

        Args:
            mission_id: Mission to search
            pattern: Dictionary of field -> value patterns
                    Supports wildcards and operators

        Returns:
            Matching nodes

        Example:
            pattern = {
                "node_type": "Decision",
                "payload.confidence": {"$gte": 0.8},
                "payload.department_id": "dept-123",
            }
        """
        nodes = [
            node
            for node in self._writer._nodes.values()
            if node.payload.get("mission_id") == mission_id
        ]

        matching = []

        for node in nodes:
            if self._matches_pattern(node, pattern):
                matching.append(node)

        return matching

    def _matches_pattern(
        self,
        node: MissionGraphNode,
        pattern: dict[str, Any],
    ) -> bool:
        """Check if node matches pattern."""
        for key, value in pattern.items():
            # Handle nested keys (e.g., "payload.confidence")
            if "." in key:
                parts = key.split(".")
                node_value = node

                for part in parts:
                    if hasattr(node_value, part):
                        node_value = getattr(node_value, part)
                    elif isinstance(node_value, dict) and part in node_value:
                        node_value = node_value[part]
                    else:
                        return False

                # Handle operators
                if isinstance(value, dict):
                    for op, op_value in value.items():
                        if op == "$gte" and node_value < op_value:
                            return False
                        if op == "$lte" and node_value > op_value:
                            return False
                        if op == "$gt" and node_value <= op_value:
                            return False
                        if op == "$lt" and node_value >= op_value:
                            return False
                        if op == "$eq" and node_value != op_value:
                            return False
                        if op == "$ne" and node_value == op_value:
                            return False
                elif node_value != value:
                    return False
            else:
                # Direct attribute comparison
                if hasattr(node, key):
                    if getattr(node, key) != value:
                        return False
                else:
                    return False

        return True

    def temporal_query(
        self,
        mission_id: str,
        *,
        start_time: str,
        end_time: str,
        node_types: list[str] | None = None,
        aggregate: str | None = None,
    ) -> list[MissionGraphNode] | dict[str, Any]:
        """
        Query nodes within time range with optional aggregation.

        Args:
            mission_id: Mission ID
            start_time: Start timestamp (ISO 8601)
            end_time: End timestamp (ISO 8601)
            node_types: Filter by node types
            aggregate: Aggregation type ("count", "confidence_avg", etc.)

        Returns:
            List of nodes or aggregation result
        """
        nodes = self.timeline(
            mission_id,
            from_timestamp=start_time,
            to_timestamp=end_time,
            node_types=node_types,
        )

        if aggregate:
            return self._aggregate_nodes(nodes, aggregate)

        return nodes

    def _aggregate_nodes(
        self,
        nodes: list[MissionGraphNode],
        aggregate_type: str,
    ) -> dict[str, Any]:
        """Aggregate nodes by type."""
        if aggregate_type == "count":
            return {"count": len(nodes)}

        if aggregate_type == "confidence_avg":
            if not nodes:
                return {"confidence_avg": 0.0}

            total_confidence = sum(
                n.payload.get("confidence", 0.0) for n in nodes
            )
            return {"confidence_avg": total_confidence / len(nodes)}

        if aggregate_type == "by_type":
            type_counts: dict[str, int] = {}
            for node in nodes:
                type_counts[node.node_type] = type_counts.get(node.node_type, 0) + 1
            return {"by_type": type_counts}

        if aggregate_type == "by_department":
            dept_counts: dict[str, int] = {}
            for node in nodes:
                dept_id = node.payload.get("department_id", "unknown")
                dept_counts[dept_id] = dept_counts.get(dept_id, 0) + 1
            return {"by_department": dept_counts}

        return {"error": f"Unknown aggregation type: {aggregate_type}"}

    def confidence_filter(
        self,
        nodes: list[MissionGraphNode],
        *,
        min_confidence: float,
        max_confidence: float = 1.0,
    ) -> list[MissionGraphNode]:
        """Filter nodes by confidence range."""
        return [
            n
            for n in nodes
            if min_confidence
            <= n.payload.get("confidence", 0.0)
            <= max_confidence
        ]
