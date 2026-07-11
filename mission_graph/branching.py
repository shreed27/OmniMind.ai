"""
Mission Graph Branching - TASK-4.4

Branch, merge, and rollback operations for Mission Graph.
Implements Git-like version control for organizational state.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from mission_graph.edges import Edge
from mission_graph.node import MissionGraphNode


class MissionGraphBranching:
    """
    Mission Graph branching operations.

    Provides:
    - Branch: Create immutable fork for parallel exploration
    - Merge: Combine branches with conflict detection
    - Rollback: Revert to previous state without deleting history
    """

    def __init__(self, writer: Any, edge_writer: Any) -> None:
        self._writer = writer
        self._edge_writer = edge_writer
        self._branches: dict[str, dict[str, Any]] = {}  # branch_name -> metadata

    def create_branch(
        self,
        *,
        mission_id: str,
        branch_name: str,
        from_node_id: str,
        created_by: str,
        reason: str | None = None,
    ) -> dict[str, Any]:
        """
        Create immutable branch fork.

        Args:
            mission_id: Mission ID
            branch_name: New branch name (must be unique)
            from_node_id: Node to branch from
            created_by: Creator ID (worker/department/user)
            reason: Optional reason for branching

        Returns:
            Branch metadata including branch_id

        Raises:
            ValueError: If branch already exists or node not found
        """
        if branch_name in self._branches:
            raise ValueError(f"Branch '{branch_name}' already exists")

        if from_node_id not in self._writer._nodes:
            raise ValueError(f"Node '{from_node_id}' not found")

        branch_id = str(uuid4())
        timestamp = datetime.utcnow().isoformat() + "Z"

        # Create branch record node
        branch_node = MissionGraphNode(
            node_id=branch_id,
            node_type="Branch",
            payload={
                "mission_id": mission_id,
                "branch_name": branch_name,
                "from_node_id": from_node_id,
                "created_by": created_by,
                "reason": reason,
                "timestamp": timestamp,
                "confidence": 1.0,
                "status": "active",
            },
        )

        # Write branch node
        self._writer.append(branch_node)

        # Create FORKED_FROM edge
        fork_edge = Edge(
            edge_id=str(uuid4()),
            source=branch_id,
            target=from_node_id,
            type="FORKED_FROM",
        )
        self._edge_writer.append(fork_edge)

        # Store branch metadata
        self._branches[branch_name] = {
            "branch_id": branch_id,
            "mission_id": mission_id,
            "head_node_id": from_node_id,
            "created_at": timestamp,
            "created_by": created_by,
            "status": "active",
        }

        return {
            "branch_id": branch_id,
            "branch_name": branch_name,
            "from_node_id": from_node_id,
            "created_at": timestamp,
            "status": "active",
        }

    def merge_branch(
        self,
        *,
        mission_id: str,
        source_branch: str,
        target_branch: str,
        merged_by: str,
        strategy: str = "auto",
        conflict_resolution: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Merge source branch into target branch.

        Args:
            mission_id: Mission ID
            source_branch: Branch to merge from
            target_branch: Branch to merge into
            merged_by: Who initiated merge
            strategy: Merge strategy ("auto", "manual", "ours", "theirs")
            conflict_resolution: Manual conflict resolutions

        Returns:
            Merge result with merge_node_id and conflicts

        Raises:
            ValueError: If branches don't exist or can't be merged
        """
        if source_branch not in self._branches:
            raise ValueError(f"Source branch '{source_branch}' not found")

        if target_branch not in self._branches:
            raise ValueError(f"Target branch '{target_branch}' not found")

        source_meta = self._branches[source_branch]
        target_meta = self._branches[target_branch]

        # Detect conflicts
        conflicts = self._detect_conflicts(source_branch, target_branch)

        # Resolve conflicts based on strategy
        if conflicts and strategy == "auto":
            # Auto strategy fails on conflicts
            return {
                "status": "conflict",
                "conflicts": conflicts,
                "message": "Automatic merge failed due to conflicts. Use manual strategy.",
            }

        resolved_conflicts = []
        if conflicts:
            if strategy == "manual" and conflict_resolution:
                resolved_conflicts = self._apply_conflict_resolution(
                    conflicts,
                    conflict_resolution,
                )
            elif strategy == "ours":
                resolved_conflicts = [
                    {**c, "resolution": "target_wins"} for c in conflicts
                ]
            elif strategy == "theirs":
                resolved_conflicts = [
                    {**c, "resolution": "source_wins"} for c in conflicts
                ]

        # Create merge node
        merge_id = str(uuid4())
        timestamp = datetime.utcnow().isoformat() + "Z"

        merge_node = MissionGraphNode(
            node_id=merge_id,
            node_type="Merge",
            payload={
                "mission_id": mission_id,
                "source_branch": source_branch,
                "target_branch": target_branch,
                "merged_by": merged_by,
                "strategy": strategy,
                "conflicts": conflicts,
                "resolved_conflicts": resolved_conflicts,
                "timestamp": timestamp,
                "confidence": 1.0 if not conflicts else 0.8,
            },
        )

        self._writer.append(merge_node)

        # Create MERGED_INTO edges
        source_edge = Edge(
            edge_id=str(uuid4()),
            source=source_meta["head_node_id"],
            target=merge_id,
            type="MERGED_INTO",
        )
        target_edge = Edge(
            edge_id=str(uuid4()),
            source=target_meta["head_node_id"],
            target=merge_id,
            type="MERGED_INTO",
        )

        self._edge_writer.append(source_edge)
        self._edge_writer.append(target_edge)

        # Update target branch head
        self._branches[target_branch]["head_node_id"] = merge_id

        # Mark source branch as merged
        self._branches[source_branch]["status"] = "merged"

        return {
            "merge_node_id": merge_id,
            "status": "merged" if not conflicts or resolved_conflicts else "conflict",
            "conflicts": conflicts,
            "resolved_conflicts": resolved_conflicts,
            "timestamp": timestamp,
        }

    def rollback(
        self,
        *,
        mission_id: str,
        branch_name: str,
        target_node_id: str,
        rolled_back_by: str,
        reason: str | None = None,
    ) -> dict[str, Any]:
        """
        Rollback to target node without deleting history.

        Creates rollback record and resets branch head.
        Original history remains immutable.

        Args:
            mission_id: Mission ID
            branch_name: Branch to rollback
            target_node_id: Node to rollback to
            rolled_back_by: Who initiated rollback
            reason: Optional reason

        Returns:
            Rollback metadata

        Raises:
            ValueError: If branch or node not found
        """
        if branch_name not in self._branches:
            raise ValueError(f"Branch '{branch_name}' not found")

        if target_node_id not in self._writer._nodes:
            raise ValueError(f"Target node '{target_node_id}' not found")

        branch_meta = self._branches[branch_name]
        current_head = branch_meta["head_node_id"]

        # Create rollback record node
        rollback_id = str(uuid4())
        timestamp = datetime.utcnow().isoformat() + "Z"

        rollback_node = MissionGraphNode(
            node_id=rollback_id,
            node_type="Rollback",
            payload={
                "mission_id": mission_id,
                "branch_name": branch_name,
                "from_node_id": current_head,
                "to_node_id": target_node_id,
                "rolled_back_by": rolled_back_by,
                "reason": reason,
                "timestamp": timestamp,
                "confidence": 1.0,
            },
        )

        self._writer.append(rollback_node)

        # Create edges to record rollback operation
        from_edge = Edge(
            edge_id=str(uuid4()),
            source=rollback_id,
            target=current_head,
            type="SUPERSEDES",
        )
        to_edge = Edge(
            edge_id=str(uuid4()),
            source=rollback_id,
            target=target_node_id,
            type="FORKED_FROM",
        )

        self._edge_writer.append(from_edge)
        self._edge_writer.append(to_edge)

        # Update branch head to target node
        self._branches[branch_name]["head_node_id"] = target_node_id

        return {
            "rollback_node_id": rollback_id,
            "branch_name": branch_name,
            "from_node_id": current_head,
            "to_node_id": target_node_id,
            "timestamp": timestamp,
            "status": "rolled_back",
        }

    def get_branch_info(self, branch_name: str) -> dict[str, Any] | None:
        """Get branch metadata."""
        return self._branches.get(branch_name)

    def list_branches(self, mission_id: str) -> list[dict[str, Any]]:
        """List all branches for a mission."""
        return [
            {
                "branch_name": name,
                **metadata,
            }
            for name, metadata in self._branches.items()
            if metadata["mission_id"] == mission_id
        ]

    def _detect_conflicts(
        self,
        source_branch: str,
        target_branch: str,
    ) -> list[dict[str, Any]]:
        """
        Detect conflicts between branches.

        Conflicts occur when:
        - Same node modified in both branches
        - Incompatible state changes
        - Dependency violations
        """
        conflicts = []

        source_meta = self._branches[source_branch]
        target_meta = self._branches[target_branch]

        # Find all nodes in each branch since fork point
        source_nodes = self._get_branch_nodes(source_branch)
        target_nodes = self._get_branch_nodes(target_branch)

        # Check for overlapping node modifications
        source_node_ids = {n.node_id for n in source_nodes}
        target_node_ids = {n.node_id for n in target_nodes}

        overlap = source_node_ids & target_node_ids

        for node_id in overlap:
            conflicts.append(
                {
                    "node_id": node_id,
                    "conflict_type": "node_modified_in_both_branches",
                    "source_branch": source_branch,
                    "target_branch": target_branch,
                },
            )

        return conflicts

    def _get_branch_nodes(self, branch_name: str) -> list[MissionGraphNode]:
        """Get all nodes in a branch."""
        if branch_name not in self._branches:
            return []

        branch_meta = self._branches[branch_name]
        mission_id = branch_meta["mission_id"]

        # Get all nodes for this mission on this branch
        nodes = [
            node
            for node in self._writer._nodes.values()
            if node.payload.get("mission_id") == mission_id
            and node.payload.get("branch", "main") == branch_name
        ]

        return nodes

    def _apply_conflict_resolution(
        self,
        conflicts: list[dict[str, Any]],
        resolutions: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Apply manual conflict resolutions."""
        resolved = []

        for conflict in conflicts:
            node_id = conflict["node_id"]

            if node_id in resolutions:
                resolved.append(
                    {
                        **conflict,
                        "resolution": resolutions[node_id],
                        "resolved": True,
                    },
                )
            else:
                resolved.append(
                    {
                        **conflict,
                        "resolved": False,
                    },
                )

        return resolved
