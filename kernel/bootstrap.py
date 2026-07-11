from __future__ import annotations

import logging
import signal
import sys
from typing import Any

from kernel.core.config import get_kernel_settings
from kernel.core.event_bus import InMemoryEventBus
from kernel.core.exceptions import KernelBootError
from kernel.core.logging import get_logger
from kernel.services.department_manager import DepartmentManagerService
from kernel.services.mission_scheduler import MissionSchedulerService
from kernel.services.organization_manager import OrganizationManagerService
from kernel.services.worker_scheduler import WorkerSchedulerService


REQUIRED_SERVICES: list[str] = [
    "event_bus",
    "mission_scheduler",
    "organization_manager",
    "department_manager",
    "worker_scheduler",
]


class Kernel:
    def __init__(self) -> None:
        self._event_bus = InMemoryEventBus()
        self._mission_scheduler = MissionSchedulerService(self._event_bus)
        self._organization_manager = OrganizationManagerService(self._event_bus)
        self._department_manager = DepartmentManagerService(self._event_bus)
        self._worker_scheduler = WorkerSchedulerService(self._event_bus)
        self._logger = get_logger("kernel")
        self._shutdown = False

    @property
    def services(self) -> dict[str, Any]:
        return {
            "event_bus": self._event_bus,
            "mission_scheduler": self._mission_scheduler,
            "organization_manager": self._organization_manager,
            "department_manager": self._department_manager,
            "worker_scheduler": self._worker_scheduler,
        }

    async def start(self) -> None:
        self._register_signal_handlers()
        required_missing = [name for name in REQUIRED_SERVICES if self.services.get(name) is None]
        if required_missing:
            raise KernelBootError(f"Missing required services: {required_missing}")
        self._logger.info("Kernel started with services: %s", ",".join(self.services.keys()))

    async def stop(self) -> None:
        self._shutdown = True
        await self._event_bus.disconnect()
        self._logger.info("Kernel stopped")

    def _register_signal_handlers(self) -> None:
        try:
            signal.signal(signal.SIGTERM, lambda *_args: sys.exit(0))
            signal.signal(signal.SIGINT, lambda *_args: sys.exit(0))
        except Exception:  # pragma: no cover - Windows signal compatibility
            pass


def create_kernel() -> Kernel:
    return Kernel()


def get_service(name: str) -> Any:
    kernel = _current_kernel()
    service = kernel.services.get(name)
    if service is None:
        raise KernelBootError(f"Service not registered: {name}")
    return service


def _current_kernel() -> Kernel:
    if getattr(_current_kernel, "_instance", None) is None:
        _current_kernel._instance = create_kernel()  # type: ignore[attr-defined]
    return _current_kernel._instance  # type: ignore[attr-defined]
