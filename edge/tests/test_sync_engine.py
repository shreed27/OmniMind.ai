"""Tests for Edge Sync Engine - TASK-12.3"""

from __future__ import annotations

import pytest

from edge.sync_engine import EdgeSyncEngine, SyncStrategy
from kernel.core.event_bus import InMemoryEventBus


@pytest.mark.asyncio
async def test_conflict_detection() -> None:
    """Sync engine detects conflicts via hash comparison."""
    bus = InMemoryEventBus()
    sync = EdgeSyncEngine(event_bus=bus)

    edge_artifacts = [
        {"artifact_id": "art-1", "content": "edge version", "version": "v1"},
    ]

    cloud_artifacts = [
        {"artifact_id": "art-1", "content": "cloud version", "version": "v2"},
    ]

    result = await sync.synchronize(
        mission_id="mission-1",
        edge_artifacts=edge_artifacts,
        cloud_artifacts=cloud_artifacts,
        strategy=SyncStrategy.CLOUD_WINS,
    )

    assert result["conflicts_detected"] > 0


@pytest.mark.asyncio
async def test_cloud_wins_strategy() -> None:
    """Cloud wins strategy uses cloud artifact."""
    bus = InMemoryEventBus()
    sync = EdgeSyncEngine(event_bus=bus)

    edge_artifacts = [{"artifact_id": "art-1", "content": "edge"}]
    cloud_artifacts = [{"artifact_id": "art-1", "content": "cloud"}]

    result = await sync.synchronize(
        mission_id="mission-1",
        edge_artifacts=edge_artifacts,
        cloud_artifacts=cloud_artifacts,
        strategy=SyncStrategy.CLOUD_WINS,
    )

    resolution = result["resolutions"][0]
    assert resolution["winner"] == "cloud"


@pytest.mark.asyncio
async def test_edge_wins_strategy() -> None:
    """Edge wins strategy uses edge artifact."""
    bus = InMemoryEventBus()
    sync = EdgeSyncEngine(event_bus=bus)

    edge_artifacts = [{"artifact_id": "art-1", "content": "edge"}]
    cloud_artifacts = [{"artifact_id": "art-1", "content": "cloud"}]

    result = await sync.synchronize(
        mission_id="mission-1",
        edge_artifacts=edge_artifacts,
        cloud_artifacts=cloud_artifacts,
        strategy=SyncStrategy.EDGE_WINS,
    )

    resolution = result["resolutions"][0]
    assert resolution["winner"] == "edge"


@pytest.mark.asyncio
async def test_merge_strategy() -> None:
    """Merge strategy attempts to combine both versions."""
    bus = InMemoryEventBus()
    sync = EdgeSyncEngine(event_bus=bus)

    edge_artifacts = [{"artifact_id": "art-1", "edge_field": "value1"}]
    cloud_artifacts = [{"artifact_id": "art-1", "cloud_field": "value2"}]

    result = await sync.synchronize(
        mission_id="mission-1",
        edge_artifacts=edge_artifacts,
        cloud_artifacts=cloud_artifacts,
        strategy=SyncStrategy.MERGE,
    )

    resolution = result["resolutions"][0]
    assert resolution["action"] == "merged"
    assert "merged_artifact" in resolution


@pytest.mark.asyncio
async def test_manual_resolution_required() -> None:
    """Manual strategy escalates to human approval."""
    bus = InMemoryEventBus()
    sync = EdgeSyncEngine(event_bus=bus)

    edge_artifacts = [{"artifact_id": "art-1", "content": "edge"}]
    cloud_artifacts = [{"artifact_id": "art-1", "content": "cloud"}]

    result = await sync.synchronize(
        mission_id="mission-1",
        edge_artifacts=edge_artifacts,
        cloud_artifacts=cloud_artifacts,
        strategy=SyncStrategy.MANUAL,
    )

    resolution = result["resolutions"][0]
    assert resolution["requires_approval"] is True
