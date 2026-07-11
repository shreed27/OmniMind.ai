"""Tests for Edge Runtime - TASK-12.1/12.2"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from edge.runtime import EdgeRuntime, EdgeRuntimeStatus


@pytest.mark.asyncio
async def test_edge_activation() -> None:
    """Edge runtime activates mini-organization when offline."""
    with tempfile.TemporaryDirectory() as tmpdir:
        runtime = EdgeRuntime(storage_root=Path(tmpdir))

        assert runtime.status() == EdgeRuntimeStatus.ONLINE

        await runtime.activate_edge(
            mission_id="mission-1",
            mission_context={
                "objective": "Build MVP",
                "constraints": [],
            },
        )

        assert runtime.status() == EdgeRuntimeStatus.EDGE_ACTIVATED
        assert runtime.is_offline() is True


@pytest.mark.asyncio
async def test_offline_mission_continuation() -> None:
    """Mission continues execution using mini-organization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        runtime = EdgeRuntime(storage_root=Path(tmpdir))

        await runtime.activate_edge(
            mission_id="mission-1",
            mission_context={"objective": "Test"},
        )

        result = await runtime.continue_mission_offline(
            mission_id="mission-1",
            objective="Build feature X",
        )

        assert "plan" in result
        assert "results" in result
        assert result["queued_for_sync"] > 0


@pytest.mark.asyncio
async def test_edge_to_cloud_sync() -> None:
    """Edge artifacts sync back to cloud after reconnection."""
    with tempfile.TemporaryDirectory() as tmpdir:
        runtime = EdgeRuntime(storage_root=Path(tmpdir))

        await runtime.activate_edge(mission_id="mission-1", mission_context={})
        await runtime.continue_mission_offline(mission_id="mission-1", objective="Test")

        sync_result = await runtime.sync_to_cloud()

        assert sync_result["status"] == "completed"
        assert sync_result["synced_count"] > 0
        assert runtime.status() == EdgeRuntimeStatus.ONLINE


@pytest.mark.asyncio
async def test_edge_storage_wipe() -> None:
    """Edge storage is wiped after sync."""
    with tempfile.TemporaryDirectory() as tmpdir:
        runtime = EdgeRuntime(storage_root=Path(tmpdir))

        await runtime.activate_edge(mission_id="mission-1", mission_context={})

        mission_storage = Path(tmpdir) / "mission-1"
        assert mission_storage.exists()

        await runtime.wipe_edge_storage("mission-1")

        assert not mission_storage.exists()


@pytest.mark.asyncio
async def test_mini_org_memory_persistence() -> None:
    """Mini-organization stores and retrieves local memory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        runtime = EdgeRuntime(storage_root=Path(tmpdir))

        await runtime.activate_edge(mission_id="mission-1", mission_context={})

        mini_org = runtime._mini_orgs["mission-1"]

        await mini_org.store_memory("test_key", {"value": 123})
        retrieved = await mini_org.retrieve_memory("test_key")

        assert retrieved == {"value": 123}
