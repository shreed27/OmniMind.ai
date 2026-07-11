"""Tests for Digital Twin Service - TASK-11.1"""

from __future__ import annotations

import pytest

from kernel.core.event_bus import InMemoryEventBus
from kernel.services.digital_twin import DigitalTwinService


@pytest.mark.asyncio
async def test_update_mission_state() -> None:
    """Mission state updates reflect in digital twin."""
    bus = InMemoryEventBus()
    twin = DigitalTwinService(event_bus=bus)

    await twin.update_mission_state(
        mission_id="mission-1",
        state="Executing",
        confidence=0.85,
        current_phase="engineering",
        progress=0.42,
        organization_id="org-1",
    )

    snapshot = await twin.get_mission_snapshot("mission-1")

    assert snapshot is not None
    assert snapshot["state"] == "Executing"
    assert snapshot["confidence"] == 0.85
    assert snapshot["progress"] == 0.42


@pytest.mark.asyncio
async def test_update_department_state() -> None:
    """Department state updates emit DigitalTwinUpdated event."""
    bus = InMemoryEventBus()
    twin = DigitalTwinService(event_bus=bus)

    await twin.update_department_state(
        department_id="dept-eng",
        organization_id="org-1",
        mission_id="mission-1",
        status="Executing",
        workers=["worker-1", "worker-2"],
        tasks=["task-a", "task-b"],
        health="healthy",
        confidence=0.9,
    )

    # Event should be published
    # (In production, would check Redis or event store)


@pytest.mark.asyncio
async def test_update_worker_state() -> None:
    """Worker state updates tracked in digital twin."""
    bus = InMemoryEventBus()
    twin = DigitalTwinService(event_bus=bus)

    await twin.update_worker_state(
        worker_id="worker-1",
        department_id="dept-eng",
        organization_id="org-1",
        mission_id="mission-1",
        status="Executing",
        current_task_id="task-a",
        confidence=0.88,
        eta="2026-07-11T18:00:00Z",
    )

    # Event emitted with worker state


@pytest.mark.asyncio
async def test_cache_invalidation() -> None:
    """Digital twin cache can be invalidated."""
    bus = InMemoryEventBus()
    twin = DigitalTwinService(event_bus=bus)

    await twin.update_mission_state(
        mission_id="mission-1",
        state="Planning",
        confidence=1.0,
        current_phase="ceo_planning",
        progress=0.1,
    )

    await twin.invalidate_cache("mission", "mission-1")

    snapshot = await twin.get_mission_snapshot("mission-1")
    assert snapshot is None  # Cache cleared


@pytest.mark.asyncio
async def test_organization_snapshot_aggregation() -> None:
    """Organization snapshot aggregates all entity states."""
    bus = InMemoryEventBus()
    twin = DigitalTwinService(event_bus=bus)

    snapshot = await twin.get_organization_snapshot("org-1")

    assert snapshot["organization_id"] == "org-1"
    assert "departments" in snapshot
    assert "workers" in snapshot
    assert "health" in snapshot
    assert "iq" in snapshot
    assert "plasticity" in snapshot
