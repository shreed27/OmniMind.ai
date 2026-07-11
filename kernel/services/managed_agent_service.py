from __future__ import annotations

from typing import Any

from kernel.core.event import EventBus


class ManagedAgentService:
    def __init__(self, event_bus: EventBus) -> None:
        self._bus = event_bus

    async def execute(self, capability: str, payload: dict[str, Any]) -> dict[str, Any]:
        return {"capability": capability, "exit_status": 0}
