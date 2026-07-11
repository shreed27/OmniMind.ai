"""Tests for Observatory Read Models - TASK-11.3"""

from __future__ import annotations

import pytest

from kernel.core.event import EventEnvelope
from backend.observatory.read_models import ObservatoryProjection


@pytest.mark.asyncio
async def test_mission_created_projection() -> None:
    """MissionCreated event projects to read model."""
    projection = ObservatoryProjection()

    event = EventEnvelope.create(
        name="MissionCreated",
        payload={
            "mission_id": "mission-1",
            "name": "Launch AI Startup",
            "objective": "Build and launch MVP in 90 days",
        },
        mission_id="mission-1",
        confidence=1.0,
    )

    await projection.handle_event(event)

    mission = projection.get_mission("mission-1")

    assert mission is not None
    assert mission.mission_id == "mission-1"
    assert mission.name == "Launch AI Startup"
    assert mission.status == "created"
    assert mission.progress == 0.0


@pytest.mark.asyncio
async def test_mission_state_changed_projection() -> None:
    """MissionStateChanged updates read model."""
    projection = ObservatoryProjection()

    # Create mission first
    create_event = EventEnvelope.create(
        name="MissionCreated",
        payload={
            "mission_id": "mission-1",
            "name": "Test Mission",
            "objective": "Test",
        },
        mission_id="mission-1",
    )

    await projection.handle_event(create_event)

    # Update state
    update_event = EventEnvelope.create(
        name="MissionStateChanged",
        payload={
            "mission_id": "mission-1",
            "from_state": "Created",
            "to_state": "Executing",
        },
        mission_id="mission-1",
        confidence=0.85,
    )

    await projection.handle_event(update_event)

    mission = projection.get_mission("mission-1")

    assert mission is not None
    assert mission.status == "Executing"
    assert mission.confidence == 0.85


@pytest.mark.asyncio
async def test_list_departments_for_organization() -> None:
    """List departments filters by organization."""
    projection = ObservatoryProjection()

    event1 = EventEnvelope.create(
        name="DepartmentCreated",
        payload={"department_id": "dept-1", "type": "engineering"},
        organization_id="org-1",
        mission_id="mission-1",
    )

    event2 = EventEnvelope.create(
        name="DepartmentCreated",
        payload={"department_id": "dept-2", "type": "marketing"},
        organization_id="org-1",
        mission_id="mission-1",
    )

    event3 = EventEnvelope.create(
        name="DepartmentCreated",
        payload={"department_id": "dept-3", "type": "engineering"},
        organization_id="org-2",
        mission_id="mission-2",
    )

    await projection.handle_event(event1)
    await projection.handle_event(event2)
    await projection.handle_event(event3)

    org1_depts = projection.list_departments("org-1")

    assert len(org1_depts) == 2
    assert all(dept.organization_id == "org-1" for dept in org1_depts)


@pytest.mark.asyncio
async def test_digital_twin_updated_projection() -> None:
    """DigitalTwinUpdated events update read models."""
    projection = ObservatoryProjection()

    # Create mission
    create_event = EventEnvelope.create(
        name="MissionCreated",
        payload={
            "mission_id": "mission-1",
            "name": "Test",
            "objective": "Test",
        },
        mission_id="mission-1",
    )

    await projection.handle_event(create_event)

    # Update via digital twin
    twin_event = EventEnvelope.create(
        name="DigitalTwinUpdated",
        payload={
            "entity_type": "mission",
            "entity_id": "mission-1",
            "snapshot": {
                "state": "Reflecting",
                "progress": 0.95,
                "current_phase": "reflection",
            },
        },
        mission_id="mission-1",
    )

    await projection.handle_event(twin_event)

    mission = projection.get_mission("mission-1")

    assert mission is not None
    assert mission.status == "Reflecting"
    assert mission.progress == 0.95
    assert mission.current_phase == "reflection"
