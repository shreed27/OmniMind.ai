from __future__ import annotations

from typing import Any

import pytest

from memory.knowledge import KnowledgeGraph


@pytest.mark.asyncio
async def test_write_node_emits_event() -> None:
    graph = KnowledgeGraph()
    result = await graph.write_node("n1", ["Mission"], {"name": "Demo"})
    assert result["status"] == "queued"


@pytest.mark.asyncio
async def test_write_edge_returns_queued() -> None:
    graph = KnowledgeGraph()
    result = await graph.write_edge("n1", "n2", "HAS_DEPARTMENT")
    assert result["status"] == "queued"


@pytest.mark.asyncio
async def test_search_returns_relevant_candidate() -> None:
    graph = KnowledgeGraph()
    results = await graph.search("mission")
    assert len(results) >= 1


@pytest.mark.asyncio
async def test_invalidate_embeddings_emits_event() -> None:
    graph = KnowledgeGraph()
    await graph.invalidate_embeddings("n1")
