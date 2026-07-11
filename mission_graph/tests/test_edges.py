import pytest
from mission_graph.edges import EdgeWriter, Edge


def test_edge_writer_appends_edge() -> None:
    writer = EdgeWriter()
    edge = Edge("edge-1", "node-1", "node-2", "DEPENDS_ON")
    assert writer.append(edge) == "edge-1"
    assert writer._edges[0].type == "DEPENDS_ON"
