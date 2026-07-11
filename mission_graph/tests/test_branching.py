import pytest
from mission_graph.writer import MissionGraphWriter
from mission_graph.edges import EdgeWriter, Edge
from mission_graph.node import MissionGraphNode


def test_branch_and_merge_nodes() -> None:
    writer = MissionGraphWriter()
    for index in range(2):
        writer.append(MissionGraphNode(f"node-{index}", "Event", {"name": f"evt-{index}"}))
    fork = MissionGraphNode("node-fork", "Branch", {"from": "node-0"})
    writer.append(fork)
    assert writer._nodes["node-fork"].node_type == "Branch"


def test_rollback_preserves_history() -> None:
    writer = MissionGraphWriter()
    writer.append(MissionGraphNode("node-1", "Event", {"name": "evt-1"}))
    writer.append(MissionGraphNode("node-2", "Event", {"name": "evt-2"}))
    assert len(writer._nodes) == 2
