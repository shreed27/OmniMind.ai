from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable, Coroutine

from kernel.core.event import EventEnvelope
from kernel.core.event_bus import InMemoryEventBus
from kernel.core.exceptions import InvalidTransitionError, KernelBootError
from kernel.core.logging import get_logger
from kernel.core.ports import EventBus
from uuid import UUID

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "Created": {"Queued", "Planning", "Cancelled", "Failed"},
    "Queued": {"Planning", "Cancelled", "Failed"},
    "Planning": {"OrganizationGeneration", "Execution", "Cancelled", "Failed"},
    "OrganizationGeneration": {"Execution", "Planning", "Cancelled", "Failed"},
    "Execution": {"Waiting", "Blocked", "Reviewing", "Reflecting", "Archived", "Cancelled", "Failed"},
    "Waiting": {"Blocked", "Executing", "Reflecting", "Cancelled", "Failed"},
    "Blocked": {"Execution", "Waiting", "Reflecting", "Cancelled", "Failed"},
    "Reviewing": {"Execution", "Reflecting", "Cancelled", "Failed"},
    "Reflecting": {"Learning", "Evolving", "Completed", "Archived", "Cancelled", "Failed"},
    "Learning": {"Evolving", "Completed", "Archived"},
    "Evolving": {"Executing", "Completed", "Archived"},
    "Completed": {"Archived"},
    "Archived": {"Cancelled", "Destroyed"},
    "Cancelled": {"Reflecting"},
    "Failed": {"Reflecting"},
}

TERMINAL_STATES = {"Archived", "Destroyed"}


class MissionState:
    # frozen registry-friendly container

    @staticmethod
    def allowed(current: str, next_state: str) -> bool:
        return next_state in ALLOWED_TRANSITIONS.get(current, set())


class MissionSchedulerService:
    def __init__(self, event_bus: EventBus) -> None:
        self._bus = event_bus
        self._logger = get_logger("mission_scheduler")
        self._states: dict[str, str] = {}

    async def transition(self, mission_id: str, new_state: str, *, trace_id: str | None = None, confidence: float = 0.8, payload: dict[str, Any] | None = None, actor: str = "kernel") -> None:
        current = self._states.get(mission_id, "Created")
        if not MissionState.allowed(current, new_state):
            raise InvalidTransitionError(
                f"Invalid transition from {current} to {new_state}",
                context={"mission_id": mission_id, "from": current, "to": new_state, "actor": actor},
            )

        event = EventEnvelope.create(
            name="MissionStateChanged",
            payload={
                "mission_id": mission_id,
                "from_state": current,
                "to_state": new_state,
                "actor": actor,
                "confidence": confidence,
                "payload": payload or {},
            },
            mission_id=UUID(mission_id) if self._is_uuid(mission_id) else None,
            trace_id=trace_id,
            confidence=confidence,
            source={"service": "kernel", "module": "mission_scheduler", "component": "state_machine"},
        )
        self._states[mission_id] = new_state
        await self._bus.publish(event)
        self._logger.info("Mission %s transition %s -> %s", mission_id, current, new_state)

        if new_state in {"Cancelled", "Failed"}:
            reflection_event = EventEnvelope.create(
                name="ReflectionStarted",
                payload={"mission_id": mission_id, "reason": f"terminal_state:{new_state}", "confidence": confidence},
                mission_id=UUID(mission_id) if self._is_uuid(mission_id) else None,
                trace_id=trace_id,
                confidence=confidence,
                source={"service": "kernel", "module": "mission_scheduler", "component": "reflection_trigger"},
            )
            await self._bus.publish(reflection_event)

    def state(self, mission_id: str) -> str:
        return self._states.get(mission_id, "Created")

    def is_terminal(self, mission_id: str) -> bool:
        return self.state(mission_id) in TERMINAL_STATES

    @staticmethod
    def _is_uuid(value: str) -> bool:
        return len(value) > 0


