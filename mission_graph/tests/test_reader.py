"""Tests for Mission Graph Reader - TASK-4.3"""

from __future__ import annotations

import pytest

from mission_graph.edges import Edge, EdgeWriter
from mission_graph.node import MissionGraphNode
from mission_graph.reader import MissionGraphReader
from mission_graph.writer import MissionGraphWriter


class TestMissionGraphReader:
    """Test Mission Graph query layer."""

    def test_timeline_returns_chronological_order(self) -> None:
        """Timeline returns nodes in chronological order."""
        writer = MissionGraphWriter()

        # Add nodes with timestamps
        writer.append(
            MissionGraphNode(
                "node-1",
                "Task",
                {
                    "mission_id": "mission-1",
                    "timestamp": "2026-07-11T10:00:00Z",
                    "confidence": 0.8,
                },
            ),
        )
        writer.append(
            MissionGraphNode(
                "node-2",
                "Decision",
                {
                    "mission_id": "mission-1",
                    "timestamp": "2026-07-11T09:00:00Z",
                    "confidence": 0.9,
                },
            ),
        )
        writer.append(
            MissionGraphNode(
                "node-3",
                "Artifact",
                {
                    "mission_id": "mission-1",
                    "timestamp": "2026-07-11T11:00:00Z",
                    "confidence": 0.7,
                },
            ),
        )

        reader = MissionGraphReader(writer)
        timeline = reader.timeline("mission-1")

        assert len(timeline) == 3
        assert timeline[0].node_id == "node-2"  # 09:00
        assert timeline[1].node_id == "node-1"  # 10:00
        assert timeline[2].node_id == "node-3"  # 11:00

    def test_timeline_filters_by_timestamp_range(self) -> None:
        """Timeline filters by timestamp range."""
        writer = MissionGraphWriter()

        writer.append(
            MissionGraphNode(
                "node-1",
                "Task",
                {
                    "mission_id": "mission-1",
                    "timestamp": "2026-07-11T09:00:00Z",
                },
            ),
        )
        writer.append(
            MissionGraphNode(
                "node-2",
                "Task",
                {
                    "mission_id": "mission-1",
                    "timestamp": "2026-07-11T11:00:00Z",
                },
            ),
        )
        writer.append(
            MissionGraphNode(
                "node-3",
                "Task",
                {
                    "mission_id": "mission-1",
                    "timestamp": "2026-07-11T13:00:00Z",
                },
            ),
        )

        reader = MissionGraphReader(writer)
        timeline = reader.timeline(
            "mission-1",
            from_timestamp="2026-07-11T10:00:00Z",
            to_timestamp="2026-07-11T12:00:00Z",
        )

        assert len(timeline) == 1
        assert timeline[0].node_id == "node-2"

    def test_timeline_filters_by_node_types(self) -> None:
        """Timeline filters by node types."""
        writer = MissionGraphWriter()

        writer.append(
            MissionGraphNode(
                "node-1",
                "Task",
                {"mission_id": "mission-1", "timestamp": "2026-07-11T10:00:00Z"},
            ),
        )
        writer.append(
            MissionGraphNode(
                "node-2",
                "Decision",
                {"mission_id": "mission-1", "timestamp": "2026-07-11T10:01:00Z"},
            ),
        )
        writer.append(
            MissionGraphNode(
                "node-3",
                "Artifact",
                {"mission_id": "mission-1", "timestamp": "2026-07-11T10:02:00Z"},
            ),
        )

        reader = MissionGraphReader(writer)
        timeline = reader.timeline("mission-1", node_types=["Task", "Artifact"])

        assert len(timeline) == 2
        assert timeline[0].node_type == "Task"
        assert timeline[1].node_type == "Artifact"

    def test_timeline_filters_by_confidence(self) -> None:
        """Timeline filters by minimum confidence."""
        writer = MissionGraphWriter()

        writer.append(
            MissionGraphNode(
                "node-1",
                "Task",
                {
                    "mission_id": "mission-1",
                    "timestamp": "2026-07-11T10:00:00Z",
                    "confidence": 0.5,
                },
            ),
        )
        writer.append(
            MissionGraphNode(
                "node-2",
                "Task",
                {
                    "mission_id": "mission-1",
                    "timestamp": "2026-07-11T10:01:00Z",
                    "confidence": 0.9,
                },
            ),
        )

        reader = MissionGraphReader(writer)
        timeline = reader.timeline("mission-1", min_confidence=0.8)

        assert len(timeline) == 1
        assert timeline[0].payload["confidence"] == 0.9

    def test_lineage_bounded_to_max_depth(self) -> None:
        """Lineage query bounded to max depth 12."""
        writer = MissionGraphWriter()
        edge_writer = EdgeWriter()
        writer._edge_writer = edge_writer

        # Create chain of nodes
        for i in range(15):
            writer.append(
                MissionGraphNode(
                    f"node-{i}",
                    "Task",
                    {"mission_id": "mission-1"},
                ),
            )

        # Create dependency chain
        for i in range(14):
            edge_writer.append(
                Edge(
                    f"edge-{i}",
                    source=f"node-{i}",
                    target=f"node-{i+1}",
                    type="DEPENDS_ON",
                ),
            )

        reader = MissionGraphReader(writer)
        lineage = reader.lineage("node-0", max_depth=12)

        # Should stop at depth 12
        assert len(lineage) <= 13  # Depth 0 to 12 = 13 nodes

    def test_lineage_backward_direction(self) -> None:
        """Lineage query in backward direction (dependencies)."""
        writer = MissionGraphWriter()
        edge_writer = EdgeWriter()
        writer._edge_writer = edge_writer

        writer.append(MissionGraphNode("node-1", "Task", {}))
        writer.append(MissionGraphNode("node-2", "Task", {}))
        writer.append(MissionGraphNode("node-3", "Task", {}))

        # node-3 depends on node-2, node-2 depends on node-1
        edge_writer.append(Edge("edge-1", "node-1", "node-2", "DEPENDS_ON"))
        edge_writer.append(Edge("edge-2", "node-2", "node-3", "DEPENDS_ON"))

        reader = MissionGraphReader(writer)
        lineage = reader.lineage("node-3", direction="backward")

        # Should find node-3 and its dependencies (node-2, node-1)
        node_ids = [entry["node_id"] for entry in lineage]
        assert "node-3" in node_ids
        assert "node-2" in node_ids

    def test_branch_head_returns_latest_approved_node(self) -> None:
        """Branch head resolution returns latest approved node."""
        writer = MissionGraphWriter()

        writer.append(
            MissionGraphNode(
                "node-1",
                "Decision",
                {
                    "mission_id": "mission-1",
                    "branch": "main",
                    "approved": True,
                    "timestamp": "2026-07-11T10:00:00Z",
                },
            ),
        )
        writer.append(
            MissionGraphNode(
                "node-2",
                "Decision",
                {
                    "mission_id": "mission-1",
                    "branch": "main",
                    "approved": True,
                    "timestamp": "2026-07-11T11:00:00Z",
                },
            ),
        )
        writer.append(
            MissionGraphNode(
                "node-3",
                "Decision",
                {
                    "mission_id": "mission-1",
                    "branch": "main",
                    "approved": False,
                    "timestamp": "2026-07-11T12:00:00Z",
                },
            ),
        )

        reader = MissionGraphReader(writer)
        head = reader.branch_head("mission-1", "main")

        assert head is not None
        assert head.node_id == "node-2"  # Latest approved

    def test_find_path_returns_shortest_path(self) -> None:
        """Find path returns shortest path between nodes."""
        writer = MissionGraphWriter()
        edge_writer = EdgeWriter()
        writer._edge_writer = edge_writer

        for i in range(5):
            writer.append(MissionGraphNode(f"node-{i}", "Task", {}))

        # Create graph: 0 -> 1 -> 2 -> 4
        #                0 -> 3 -> 4
        edge_writer.append(Edge("e1", "node-0", "node-1", "DEPENDS_ON"))
        edge_writer.append(Edge("e2", "node-1", "node-2", "DEPENDS_ON"))
        edge_writer.append(Edge("e3", "node-2", "node-4", "DEPENDS_ON"))
        edge_writer.append(Edge("e4", "node-0", "node-3", "DEPENDS_ON"))
        edge_writer.append(Edge("e5", "node-3", "node-4", "DEPENDS_ON"))

        reader = MissionGraphReader(writer)
        path = reader.find_path("node-0", "node-4")

        # Shortest path is 0 -> 3 -> 4
        assert path is not None
        assert len(path) == 3
        assert path[0] == "node-0"
        assert path[-1] == "node-4"

    def test_pattern_match_basic(self) -> None:
        """Pattern match finds nodes matching criteria."""
        writer = MissionGraphWriter()

        writer.append(
            MissionGraphNode(
                "node-1",
                "Decision",
                {
                    "mission_id": "mission-1",
                    "confidence": 0.9,
                    "department_id": "dept-1",
                },
            ),
        )
        writer.append(
            MissionGraphNode(
                "node-2",
                "Task",
                {
                    "mission_id": "mission-1",
                    "confidence": 0.5,
                    "department_id": "dept-1",
                },
            ),
        )
        writer.append(
            MissionGraphNode(
                "node-3",
                "Decision",
                {
                    "mission_id": "mission-1",
                    "confidence": 0.8,
                    "department_id": "dept-2",
                },
            ),
        )

        reader = MissionGraphReader(writer)
        matches = reader.pattern_match(
            "mission-1",
            {
                "node_type": "Decision",
                "payload.confidence": {"$gte": 0.8},
            },
        )

        assert len(matches) == 2
        assert all(m.node_type == "Decision" for m in matches)
        assert all(m.payload["confidence"] >= 0.8 for m in matches)

    def test_temporal_query_with_aggregation(self) -> None:
        """Temporal query supports aggregation."""
        writer = MissionGraphWriter()

        for i in range(5):
            writer.append(
                MissionGraphNode(
                    f"node-{i}",
                    "Task",
                    {
                        "mission_id": "mission-1",
                        "timestamp": f"2026-07-11T10:0{i}:00Z",
                        "confidence": 0.8 + (i * 0.02),
                    },
                ),
            )

        reader = MissionGraphReader(writer)
        result = reader.temporal_query(
            "mission-1",
            start_time="2026-07-11T10:00:00Z",
            end_time="2026-07-11T10:10:00Z",
            aggregate="count",
        )

        assert result["count"] == 5

    def test_temporal_query_confidence_avg(self) -> None:
        """Temporal query calculates confidence average."""
        writer = MissionGraphWriter()

        writer.append(
            MissionGraphNode(
                "node-1",
                "Task",
                {
                    "mission_id": "mission-1",
                    "timestamp": "2026-07-11T10:00:00Z",
                    "confidence": 0.8,
                },
            ),
        )
        writer.append(
            MissionGraphNode(
                "node-2",
                "Task",
                {
                    "mission_id": "mission-1",
                    "timestamp": "2026-07-11T10:01:00Z",
                    "confidence": 0.6,
                },
            ),
        )

        reader = MissionGraphReader(writer)
        result = reader.temporal_query(
            "mission-1",
            start_time="2026-07-11T10:00:00Z",
            end_time="2026-07-11T10:10:00Z",
            aggregate="confidence_avg",
        )

        assert result["confidence_avg"] == 0.7

    def test_confidence_filter(self) -> None:
        """Confidence filter returns nodes in range."""
        writer = MissionGraphWriter()

        nodes = [
            MissionGraphNode("n1", "Task", {"confidence": 0.5}),
            MissionGraphNode("n2", "Task", {"confidence": 0.7}),
            MissionGraphNode("n3", "Task", {"confidence": 0.9}),
        ]

        for node in nodes:
            writer.append(node)

        reader = MissionGraphReader(writer)
        filtered = reader.confidence_filter(
            list(writer._nodes.values()),
            min_confidence=0.6,
            max_confidence=0.8,
        )

        assert len(filtered) == 1
        assert filtered[0].payload["confidence"] == 0.7
