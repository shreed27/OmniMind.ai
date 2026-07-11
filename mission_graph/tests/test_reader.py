import pytest
from mission_graph.reader import MissionGraphReader
from mission_graph.writer import MissionGraphWriter
from mission_graph.node import MissionGraphNode


def test_reader_timeline_after_appends() -> None:
    writer = MissionGraphWriter()
    for index in range(3):
        writer.append(MissionGraphNode(f"node-{index}", "Event", {"name": f"evt-{index}"}))
    reader = MissionGraphReader(writer)
    timeline = reader.timeline("mission-1")
    assert len(timeline) == 3


def test_reader_lineage_bounded() -> None:
    writer = MissionGraphWriter()
    reader = MissionGraphReader(writer)
    assert reader.lineage("node-1", limit=12) == []
