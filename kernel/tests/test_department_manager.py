from __future__ import annotations

import pytest

from kernel.services.department_manager import DepartmentManagerService


def test_create_and_get() -> None:
    bus = __import__("kernel.core.event_bus", fromlist=["EventBus"]).EventBus()
    service = DepartmentManagerService(event_bus=bus)
    dept = service.create("dept-1", "org-1", name="Engineering")
    assert dept.name == "Engineering"
    assert service.get("dept-1").department_id == "dept-1"
