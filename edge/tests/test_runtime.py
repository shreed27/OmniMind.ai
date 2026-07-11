import pytest
from edge.runtime import GemmaEdgeRuntime


@pytest.mark.asyncio
async def test_edge_runtime_start_stop() -> None:
    rt = GemmaEdgeRuntime()
    await rt.start()
    assert rt._running is True
    await rt.stop()
    assert rt._running is False
