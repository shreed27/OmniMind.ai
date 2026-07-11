from __future__ import annotations

import asyncio

import pytest

from kernel.bootstrap import Kernel
from kernel.core.exceptions import KernelBootError


def test_kernel_starts_and_registers_services() -> None:
    kernel = Kernel()
    asyncio.get_event_loop().run_until_complete(kernel.start())
    assert "event_bus" in kernel.services
    assert "mission_scheduler" in kernel.services


def test_kernel_missing_service_raises() -> None:
    kernel = Kernel()
    with pytest.raises(KernelBootError):
        get_service("does_not_exist")
