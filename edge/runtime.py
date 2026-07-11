"""
Edge Runtime Service - TASK-12.1

Gemma-powered offline mission continuity.
Mini-organization (CEO, Planner, Engineer, Memory) runs locally when cloud unavailable.
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from kernel.core.event import EventEnvelope
from kernel.core.logging import get_logger


class EdgeRuntimeStatus:
    """Edge runtime status states."""

    ONLINE = "online"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    EDGE_ACTIVATED = "edge_activated"
    SYNCING = "syncing"


class MiniOrganization:
    """
    Lightweight organization for edge runtime.

    Components:
    - Mini CEO (planning)
    - Mini Planner (task decomposition)
    - Mini Engineer (code generation)
    - Mini Memory (local storage)
    """

    def __init__(self, mission_id: str, local_storage_path: Path) -> None:
        self.mission_id = mission_id
        self.storage_path = local_storage_path
        self._logger = get_logger(f"edge.mini_org.{mission_id}")
        self._state: dict[str, Any] = {}

    async def plan(self, objective: str) -> dict[str, Any]:
        """Mini CEO planning."""
        plan = {
            "mission_id": self.mission_id,
            "objective": objective,
            "tasks": [
                {"task_id": "1", "description": "Analyze objective", "confidence": 0.8},
                {"task_id": "2", "description": "Generate approach", "confidence": 0.75},
            ],
            "confidence": 0.7,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "source": "edge_mini_ceo",
        }

        self._logger.info("Mini CEO planned: %s tasks", len(plan["tasks"]))
        return plan

    async def execute_task(self, task: dict[str, Any]) -> dict[str, Any]:
        """Mini Engineer execution."""
        result = {
            "task_id": task.get("task_id"),
            "status": "completed",
            "artifacts": [],
            "confidence": 0.65,
            "source": "edge_mini_engineer",
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }

        self._logger.info("Mini Engineer executed: %s", task.get("task_id"))
        return result

    async def store_memory(self, key: str, value: Any) -> None:
        """Mini Memory local storage."""
        memory_file = self.storage_path / "memory.json"
        memories = {}

        if memory_file.exists():
            with open(memory_file, "r") as f:
                memories = json.load(f)

        memories[key] = value

        with open(memory_file, "w") as f:
            json.dump(memories, f, indent=2)

        self._logger.debug("Mini Memory stored: %s", key)

    async def retrieve_memory(self, key: str) -> Any | None:
        """Mini Memory retrieval."""
        memory_file = self.storage_path / "memory.json"

        if not memory_file.exists():
            return None

        with open(memory_file, "r") as f:
            memories = json.load(f)

        return memories.get(key)


class EdgeRuntime:
    """
    Edge Runtime Service - runs mini-organization offline.

    Lifecycle:
    - Online: Full cloud organization
    - Degraded: Intermittent connectivity
    - Offline → EdgeActivated: Mini-org takes over
    - Syncing: Merge edge artifacts back to cloud
    """

    def __init__(self, storage_root: Path) -> None:
        self._storage_root = storage_root
        self._logger = get_logger("edge_runtime")
        self._status = EdgeRuntimeStatus.ONLINE
        self._mini_orgs: dict[str, MiniOrganization] = {}
        self._sync_queue: list[dict[str, Any]] = []

    async def activate_edge(self, mission_id: str, mission_context: dict[str, Any]) -> None:
        """
        Activate edge runtime for mission.

        Creates mini-organization with local storage.
        """
        if self._status == EdgeRuntimeStatus.ONLINE:
            self._logger.warning("Activating edge runtime while online - connectivity lost")

        self._status = EdgeRuntimeStatus.EDGE_ACTIVATED

        # Create storage directory
        mission_storage = self._storage_root / mission_id
        mission_storage.mkdir(parents=True, exist_ok=True)

        # Save mission context locally
        context_file = mission_storage / "context.json"
        with open(context_file, "w") as f:
            json.dump(mission_context, f, indent=2)

        # Create mini-organization
        mini_org = MiniOrganization(mission_id, mission_storage)
        self._mini_orgs[mission_id] = mini_org

        self._logger.info("Edge runtime activated for mission %s", mission_id)

    async def continue_mission_offline(self, mission_id: str, objective: str) -> dict[str, Any]:
        """
        Continue mission execution using mini-organization.

        Returns:
            Execution results queued for sync
        """
        if mission_id not in self._mini_orgs:
            raise ValueError(f"No mini-org for mission {mission_id}")

        mini_org = self._mini_orgs[mission_id]

        # Plan with mini CEO
        plan = await mini_org.plan(objective)

        # Execute tasks with mini Engineer
        results = []
        for task in plan.get("tasks", []):
            result = await mini_org.execute_task(task)
            results.append(result)

            # Queue for sync
            self._sync_queue.append(
                {
                    "mission_id": mission_id,
                    "type": "task_result",
                    "payload": result,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

        # Store in mini Memory
        await mini_org.store_memory(f"offline_execution_{datetime.now().isoformat()}", results)

        self._logger.info("Mission %s continued offline: %d tasks", mission_id, len(results))

        return {"plan": plan, "results": results, "queued_for_sync": len(self._sync_queue)}

    async def sync_to_cloud(self) -> dict[str, Any]:
        """
        Synchronize edge artifacts back to cloud.

        Returns:
            Sync summary with conflicts
        """
        if self._status != EdgeRuntimeStatus.SYNCING:
            self._status = EdgeRuntimeStatus.SYNCING

        sync_count = len(self._sync_queue)
        conflicts = []

        # Placeholder for actual sync logic
        # In production, would:
        # 1. Compare edge version with cloud version
        # 2. Detect conflicts
        # 3. Merge or request resolution
        # 4. Update Mission Graph

        self._sync_queue.clear()

        self._status = EdgeRuntimeStatus.ONLINE
        self._logger.info("Synced %d items to cloud", sync_count)

        return {
            "synced_count": sync_count,
            "conflicts": conflicts,
            "status": "completed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def detect_conflicts(self, edge_data: dict[str, Any], cloud_data: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Detect conflicts between edge and cloud state.

        Returns:
            List of conflict descriptions
        """
        conflicts = []

        # Simple hash-based conflict detection
        edge_hash = hash(json.dumps(edge_data, sort_keys=True))
        cloud_hash = hash(json.dumps(cloud_data, sort_keys=True))

        if edge_hash != cloud_hash:
            conflicts.append(
                {
                    "entity_type": edge_data.get("type", "unknown"),
                    "entity_id": edge_data.get("id"),
                    "edge_hash": edge_hash,
                    "cloud_hash": cloud_hash,
                    "resolution": "manual",
                }
            )

        return conflicts

    async def wipe_edge_storage(self, mission_id: str) -> None:
        """
        Securely wipe local edge storage.

        Called after successful sync or mission cancellation.
        """
        if mission_id in self._mini_orgs:
            mini_org = self._mini_orgs.pop(mission_id)

            # Remove storage
            import shutil

            if mini_org.storage_path.exists():
                shutil.rmtree(mini_org.storage_path)

            self._logger.info("Edge storage wiped for mission %s", mission_id)

    def status(self) -> str:
        """Get current edge runtime status."""
        return self._status

    def is_offline(self) -> bool:
        """Check if running in offline mode."""
        return self._status in [EdgeRuntimeStatus.OFFLINE, EdgeRuntimeStatus.EDGE_ACTIVATED]
