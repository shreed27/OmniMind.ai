"""
Digital Twin Service - TASK-11.1

Redis-backed hot cache of live organization state.
WebSocket-compatible real-time updates.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from kernel.core.event import EventEnvelope
from kernel.core.logging import get_logger
from kernel.core.ports import EventBus


class DigitalTwinService:
    """
    Maintains live digital twin of organization state.

    Responsibilities:
    - Hot cache of mission/org/dept/worker/task state
    - Sub-second updates via Redis
    - WebSocket-compatible change stream
    - Observatory read model projections
    """

    TTL_MISSION = 48 * 3600  # 48 hours
    TTL_WORKER = 24 * 3600  # 24 hours
    TTL_HOT_STATE = 60  # 60 seconds sliding window

    def __init__(self, event_bus: EventBus, redis_client: Any | None = None) -> None:
        self._bus = event_bus
        self._redis = redis_client
        self._logger = get_logger("digital_twin")
        self._state_cache: dict[str, Any] = {}  # In-memory fallback if Redis unavailable

    async def update_mission_state(
        self,
        *,
        mission_id: str,
        state: str,
        confidence: float,
        current_phase: str,
        progress: float,
        organization_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Update mission hot state."""
        snapshot = {
            "mission_id": mission_id,
            "state": state,
            "confidence": confidence,
            "current_phase": current_phase,
            "progress": progress,
            "organization_id": organization_id,
            "metadata": metadata or {},
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        key = f"omni:twin:mission:{mission_id}"

        if self._redis:
            await self._redis.setex(key, self.TTL_MISSION, json.dumps(snapshot))
        else:
            self._state_cache[key] = snapshot

        # Emit change event
        event = EventEnvelope.create(
            name="DigitalTwinUpdated",
            payload={"entity_type": "mission", "entity_id": mission_id, "snapshot": snapshot},
            mission_id=mission_id,
            organization_id=organization_id,
            confidence=confidence,
            source={"service": "kernel", "module": "digital_twin", "component": "mission_update"},
        )

        await self._bus.publish(event)
        self._logger.debug("Mission state updated: %s -> %s (%.1f%%)", mission_id, state, progress * 100)

    async def update_department_state(
        self,
        *,
        department_id: str,
        organization_id: str,
        mission_id: str,
        status: str,
        workers: list[str],
        tasks: list[str],
        health: str,
        confidence: float,
        resources: dict[str, Any] | None = None,
    ) -> None:
        """Update department hot state."""
        snapshot = {
            "department_id": department_id,
            "organization_id": organization_id,
            "mission_id": mission_id,
            "status": status,
            "workers": workers,
            "tasks": tasks,
            "health": health,
            "confidence": confidence,
            "resources": resources or {},
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        key = f"omni:twin:department:{department_id}"

        if self._redis:
            await self._redis.setex(key, self.TTL_HOT_STATE, json.dumps(snapshot))
        else:
            self._state_cache[key] = snapshot

        event = EventEnvelope.create(
            name="DigitalTwinUpdated",
            payload={"entity_type": "department", "entity_id": department_id, "snapshot": snapshot},
            mission_id=mission_id,
            organization_id=organization_id,
            department_id=department_id,
            confidence=confidence,
            source={"service": "kernel", "module": "digital_twin", "component": "department_update"},
        )

        await self._bus.publish(event)

    async def update_worker_state(
        self,
        *,
        worker_id: str,
        department_id: str,
        organization_id: str,
        mission_id: str,
        status: str,
        current_task_id: str | None,
        confidence: float,
        eta: str | None = None,
    ) -> None:
        """Update worker hot state."""
        snapshot = {
            "worker_id": worker_id,
            "department_id": department_id,
            "organization_id": organization_id,
            "mission_id": mission_id,
            "status": status,
            "current_task_id": current_task_id,
            "confidence": confidence,
            "eta": eta,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        key = f"omni:twin:worker:{worker_id}"

        if self._redis:
            await self._redis.setex(key, self.TTL_WORKER, json.dumps(snapshot))
        else:
            self._state_cache[key] = snapshot

        event = EventEnvelope.create(
            name="DigitalTwinUpdated",
            payload={"entity_type": "worker", "entity_id": worker_id, "snapshot": snapshot},
            mission_id=mission_id,
            organization_id=organization_id,
            department_id=department_id,
            worker_id=worker_id,
            confidence=confidence,
            source={"service": "kernel", "module": "digital_twin", "component": "worker_update"},
        )

        await self._bus.publish(event)

    async def get_mission_snapshot(self, mission_id: str) -> dict[str, Any] | None:
        """Retrieve mission digital twin snapshot."""
        key = f"omni:twin:mission:{mission_id}"

        if self._redis:
            data = await self._redis.get(key)
            return json.loads(data) if data else None
        else:
            return self._state_cache.get(key)

    async def get_organization_snapshot(self, organization_id: str) -> dict[str, Any]:
        """
        Retrieve full organization digital twin.

        Returns:
            Aggregated snapshot with all departments, workers, tasks
        """
        # This is a simplified version - production would aggregate from multiple keys
        snapshot = {
            "organization_id": organization_id,
            "departments": [],
            "workers": [],
            "health": "healthy",
            "iq": 75.0,
            "plasticity": 0.8,
            "snapshot_time": datetime.now(timezone.utc).isoformat(),
        }

        return snapshot

    async def subscribe_to_changes(
        self, mission_id: str | None = None, organization_id: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Get change stream for WebSocket subscription.

        Returns:
            List of recent DigitalTwinUpdated events
        """
        # Placeholder - production would use Redis Streams or pub/sub
        return []

    async def invalidate_cache(self, entity_type: str, entity_id: str) -> None:
        """Invalidate cached digital twin entry."""
        key = f"omni:twin:{entity_type}:{entity_id}"

        if self._redis:
            await self._redis.delete(key)
        else:
            self._state_cache.pop(key, None)

        self._logger.info("Invalidated digital twin cache: %s/%s", entity_type, entity_id)
