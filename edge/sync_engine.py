"""
Edge Sync Engine - TASK-12.3

Conflict-free cloud↔edge synchronization.
Supports merge, replace, branch, replay strategies.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from kernel.core.event import EventEnvelope
from kernel.core.logging import get_logger
from kernel.core.ports import EventBus


class SyncStrategy:
    """Sync conflict resolution strategies."""

    MERGE = "merge"  # Merge both versions
    CLOUD_WINS = "cloud_wins"  # Replace edge with cloud
    EDGE_WINS = "edge_wins"  # Replace cloud with edge
    BRANCH = "branch"  # Create mission branch for edge version
    MANUAL = "manual"  # Request human resolution


class EdgeSyncEngine:
    """
    Edge↔Cloud synchronization engine.

    Responsibilities:
    - Detect conflicts via hash comparison
    - Apply resolution strategies
    - Emit synchronization events
    - Update Mission Graph
    """

    def __init__(self, event_bus: EventBus) -> None:
        self._bus = event_bus
        self._logger = get_logger("edge_sync")
        self._conflicts: list[dict[str, Any]] = []

    async def synchronize(
        self,
        *,
        mission_id: str,
        edge_artifacts: list[dict[str, Any]],
        cloud_artifacts: list[dict[str, Any]],
        strategy: str = SyncStrategy.MERGE,
    ) -> dict[str, Any]:
        """
        Synchronize edge and cloud state.

        Returns:
            Sync result with conflicts and resolutions
        """
        conflicts = await self._detect_conflicts(edge_artifacts, cloud_artifacts)

        resolutions = []
        for conflict in conflicts:
            resolution = await self._resolve_conflict(conflict, strategy)
            resolutions.append(resolution)

        # Emit sync events
        event = EventEnvelope.create(
            name="SynchronizationCompleted",
            payload={
                "mission_id": mission_id,
                "edge_count": len(edge_artifacts),
                "cloud_count": len(cloud_artifacts),
                "conflicts": len(conflicts),
                "resolutions": resolutions,
                "strategy": strategy,
            },
            mission_id=mission_id,
            confidence=0.9 if not conflicts else 0.7,
            source={"service": "edge", "module": "sync_engine", "component": "synchronize"},
        )

        await self._bus.publish(event)

        self._logger.info(
            "Sync completed for mission %s: %d conflicts, strategy=%s",
            mission_id,
            len(conflicts),
            strategy,
        )

        return {
            "mission_id": mission_id,
            "conflicts_detected": len(conflicts),
            "resolutions": resolutions,
            "strategy": strategy,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def _detect_conflicts(
        self, edge_artifacts: list[dict[str, Any]], cloud_artifacts: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Detect conflicts between edge and cloud artifacts."""
        conflicts = []

        # Build lookup by artifact_id
        cloud_by_id = {artifact.get("artifact_id"): artifact for artifact in cloud_artifacts}

        for edge_artifact in edge_artifacts:
            artifact_id = edge_artifact.get("artifact_id")

            if artifact_id not in cloud_by_id:
                # New artifact created on edge - no conflict
                continue

            cloud_artifact = cloud_by_id[artifact_id]

            # Compare hashes
            edge_hash = self._compute_hash(edge_artifact)
            cloud_hash = self._compute_hash(cloud_artifact)

            if edge_hash != cloud_hash:
                conflicts.append(
                    {
                        "artifact_id": artifact_id,
                        "edge_hash": edge_hash,
                        "cloud_hash": cloud_hash,
                        "edge_version": edge_artifact.get("version"),
                        "cloud_version": cloud_artifact.get("version"),
                        "edge_artifact": edge_artifact,
                        "cloud_artifact": cloud_artifact,
                    }
                )

        self._conflicts = conflicts
        return conflicts

    async def _resolve_conflict(self, conflict: dict[str, Any], strategy: str) -> dict[str, Any]:
        """Resolve single conflict using strategy."""
        artifact_id = conflict["artifact_id"]

        if strategy == SyncStrategy.CLOUD_WINS:
            resolution = {
                "artifact_id": artifact_id,
                "strategy": strategy,
                "action": "use_cloud",
                "winner": "cloud",
            }

        elif strategy == SyncStrategy.EDGE_WINS:
            resolution = {
                "artifact_id": artifact_id,
                "strategy": strategy,
                "action": "use_edge",
                "winner": "edge",
            }

        elif strategy == SyncStrategy.MERGE:
            # Attempt merge (simplified - production would have complex merge logic)
            merged = {**conflict["cloud_artifact"], **conflict["edge_artifact"]}
            resolution = {
                "artifact_id": artifact_id,
                "strategy": strategy,
                "action": "merged",
                "merged_artifact": merged,
            }

        elif strategy == SyncStrategy.BRANCH:
            resolution = {
                "artifact_id": artifact_id,
                "strategy": strategy,
                "action": "create_branch",
                "edge_branch": f"edge-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            }

        else:  # MANUAL
            resolution = {
                "artifact_id": artifact_id,
                "strategy": strategy,
                "action": "escalate",
                "requires_approval": True,
            }

        return resolution

    def _compute_hash(self, artifact: dict[str, Any]) -> str:
        """Compute deterministic hash of artifact."""
        # Remove metadata fields that change without content changes
        content = {k: v for k, v in artifact.items() if k not in ["updated_at", "version"]}
        canonical = json.dumps(content, sort_keys=True)
        return hashlib.sha256(canonical.encode()).hexdigest()

    async def get_pending_conflicts(self) -> list[dict[str, Any]]:
        """Retrieve unresolved conflicts."""
        return self._conflicts

    async def resolve_manual_conflict(
        self, conflict_id: str, resolution: dict[str, Any], approved_by: str
    ) -> None:
        """Manually resolve conflict with human approval."""
        event = EventEnvelope.create(
            name="EdgeSyncResolved",
            payload={
                "conflict_id": conflict_id,
                "resolution": resolution,
                "approved_by": approved_by,
            },
            confidence=1.0,
            source={"service": "edge", "module": "sync_engine", "component": "manual_resolution"},
        )

        await self._bus.publish(event)

        self._logger.info("Manual conflict resolution: %s by %s", conflict_id, approved_by)
