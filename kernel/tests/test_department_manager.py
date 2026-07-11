from __future__ import annotations

from kernel.services.department_manager import DepartmentManagerService


def test_department_manager_create() -> None:
    service = DepartmentManagerService(event_bus=__import__("kernel.core.event_bus", fromlist=["InMemoryEventBus"]).InMemoryEventBus())
    dept = __import__("asyncio").get_event_loop().run_until_complete(service.create("dept-1", "org-1", name="Engineering"))
    assert dept.department_id == "dept-1"
    assert dept.name == "Engineering"
