"""Tests for WebSocket Gateway - TASK-11.2"""

from __future__ import annotations

import pytest

from kernel.core.event import EventEnvelope
from kernel.core.event_bus import InMemoryEventBus
from backend.websocket.gateway import WebSocketGateway


@pytest.mark.asyncio
async def test_broadcast_filters_by_mission() -> None:
    """Events are filtered by mission subscription."""
    bus = InMemoryEventBus()
    gateway = WebSocketGateway(event_bus=bus)

    # Test that subscription filtering logic works
    subscriptions = {
        "mission_id": "mission-1",
        "organization_id": None,
        "event_types": [],
    }

    event_match = EventEnvelope.create(
        name="TaskCompleted",
        payload={"task_id": "task-1"},
        mission_id="mission-1",
    )

    event_no_match = EventEnvelope.create(
        name="TaskCompleted",
        payload={"task_id": "task-2"},
        mission_id="mission-2",
    )

    assert gateway._matches_subscription(event_match, subscriptions) is True
    assert gateway._matches_subscription(event_no_match, subscriptions) is False


@pytest.mark.asyncio
async def test_broadcast_filters_by_organization() -> None:
    """Events are filtered by organization subscription."""
    bus = InMemoryEventBus()
    gateway = WebSocketGateway(event_bus=bus)

    subscriptions = {
        "mission_id": None,
        "organization_id": "org-1",
        "event_types": [],
    }

    event_match = EventEnvelope.create(
        name="DepartmentCreated",
        payload={"department_id": "dept-1"},
        organization_id="org-1",
    )

    event_no_match = EventEnvelope.create(
        name="DepartmentCreated",
        payload={"department_id": "dept-2"},
        organization_id="org-2",
    )

    assert gateway._matches_subscription(event_match, subscriptions) is True
    assert gateway._matches_subscription(event_no_match, subscriptions) is False


def test_connection_count() -> None:
    """Connection count reflects active connections."""
    bus = InMemoryEventBus()
    gateway = WebSocketGateway(event_bus=bus)

    assert gateway.connection_count() == 0
