"""
Mission Intermediate Representation (MIR) - TASK-16.1

Abstract representation of mission execution plan.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class MissionIR:
    """
    Mission Intermediate Representation.

    Compiled from high-level objective into:
    - Organization structure
    - Department assignments
    - Task decomposition
    - Resource requirements
    - Success criteria
    """

    mission_id: str
    objective: str
    organization_blueprint: dict[str, Any]
    department_specs: list[dict[str, Any]] = field(default_factory=list)
    task_dag: dict[str, list[str]] = field(default_factory=dict)  # task_id -> dependencies
    resource_manifest: dict[str, Any] = field(default_factory=dict)
    success_criteria: list[dict[str, Any]] = field(default_factory=list)
    estimated_complexity: str = "medium"
    estimated_duration_hours: float = 0.0
    confidence: float = 0.8
    compiled_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Serialize MIR to dict."""
        return {
            "mission_id": self.mission_id,
            "objective": self.objective,
            "organization_blueprint": self.organization_blueprint,
            "department_specs": self.department_specs,
            "task_dag": self.task_dag,
            "resource_manifest": self.resource_manifest,
            "success_criteria": self.success_criteria,
            "estimated_complexity": self.estimated_complexity,
            "estimated_duration_hours": self.estimated_duration_hours,
            "confidence": self.confidence,
            "compiled_at": self.compiled_at,
        }
