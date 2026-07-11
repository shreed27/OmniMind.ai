from __future__ import annotations

import pytest

from kernel.services.organization_manager import OrganizationManagerService


def test_create_sets_registered() -> None:
    bus = __import__("kernel.core.event_bus", fromlist=["EventBus"]).EventBus()
    service = OrganizationManagerService(event_bus=bus)
    org = service.create("org-1", "mission-1")
    assert org.state == "Registered"


def test_snapshot_returns_dict() -> None:
    bus = __import__("kernel.core.event_bus", fromlist=["EventBus"]).EventBus()
    service = OrganizationManagerService(event_bus=bus)
    service.create("org-1", "mission-1")
    snap = service.snapshot("org-1")
    assert snap["organization_id"] == "org-1"
