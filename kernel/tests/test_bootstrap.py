from __future__ import annotations

import asyncio

import pytest

from kernel.bootstrap import Kernel
from kernel.core.exceptions import KernelBootError


@pytest.mark.asyncio()
async def test_kernel_starts_and_registers_services() -> None:
    kernel = Kernel()
    await kernel.start()
    await kernel.stop()
    assert "event_bus" in kernel.services
    assert "mission_scheduler" in kernel.services


@pytest.mark.asyncio()
async def test_kernel_missing_service_raises() -> None:
    kernel = Kernel()
    with pytest.raises(KernelBootError):
        await kernel.start()
    await kernel.stop()
