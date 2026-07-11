"""Tests for Research Service - TASK-14.1"""

from __future__ import annotations

import pytest

from kernel.core.event_bus import InMemoryEventBus
from kernel.services.research_service import ResearchService


@pytest.mark.asyncio
async def test_research_query() -> None:
    """Research query returns results and recommendations."""
    bus = InMemoryEventBus()
    research = ResearchService(event_bus=bus)

    report = await research.query(
        query="Best practices for event-driven architecture",
        sources=["web", "papers"],
        max_results=5,
    )

    assert "research_id" in report
    assert report["query"] == "Best practices for event-driven architecture"
    assert report["results_count"] > 0
    assert "recommendations" in report
    assert 0 <= report["confidence"] <= 1


@pytest.mark.asyncio
async def test_recommendations_never_modify_production() -> None:
    """Research generates recommendations, not direct changes."""
    bus = InMemoryEventBus()
    research = ResearchService(event_bus=bus)

    report = await research.query(query="How to optimize database queries")

    for recommendation in report["recommendations"]:
        assert recommendation["requires_approval"] is True
        assert recommendation["type"] in ["approach", "warning", "alternative"]


@pytest.mark.asyncio
async def test_research_caching() -> None:
    """Research results are cached for retrieval."""
    bus = InMemoryEventBus()
    research = ResearchService(event_bus=bus)

    report = await research.query(query="Test query")

    cached = await research.get_research(report["research_id"])

    assert cached is not None
    assert cached["research_id"] == report["research_id"]
