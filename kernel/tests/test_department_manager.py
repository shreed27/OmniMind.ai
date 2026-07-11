import pytest
from kernel.services.department_manager import DepartmentManagerService


def test_create_and_get() -> None:
    bus = __import__("kernel.core.event_bus", fromlist=["InMemoryEventBus"]).InMemoryEventBus()
    service = DepartmentManagerService(event_bus=bus)
    dept = __import__("asyncio").get_event_loop().run_until_complete(service.create("dept-1", "org-1", name="Engineering"))
    assert dept.name == "Engineering"
    assert service.get("dept-1").department_id == "dept-1"
