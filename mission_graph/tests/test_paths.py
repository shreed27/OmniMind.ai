from __future__ import annotations

from mission_graph.writer import MissionGraphWriter
from mission_graph.edges import EdgeWriter, Edge


def test_node_and_edge_append() -> None:
    writer = MissionGraphWriter()
    from mission_graph.node import MissionGraphNode
    node = MissionGraphNode("node-1", "Event", {"name": "Tested"})
    assert writer.append(node) == "node-1"

    edge_writer = EdgeWriter()
    edge = Edge("edge-1", "node-1", "node-2", "DEPENDS_ON")
    assert edge_writer.append(edge) == "edge-1"
    assert edge_writer._edges[0].type == "DEPENDS_ON"
