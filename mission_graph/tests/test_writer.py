import pytest
from mission_graph.writer import MissionGraphWriter
from mission_graph.node import MissionGraphNode


def test_writer_appends_node() -> None:
    writer = MissionGraphWriter()
    node = MissionGraphNode("node-1", "Event", {"name": "Tested"})
    assert writer.append(node) == "node-1"
    assert writer._nodes["node-1"].node_type == "Event"
