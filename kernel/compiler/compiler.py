"""
Mission Compiler - TASK-16.1

Transforms high-level mission into executable MIR.
"""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from kernel.compiler.mission_ir import MissionIR
from kernel.core.logging import get_logger


class MissionCompiler:
    """
    Mission Compiler.

    Responsibilities:
    - Parse mission objective
    - Infer required organization structure
    - Generate task decomposition (DAG)
    - Estimate resource requirements
    - Derive success criteria
    - Output executable MIR
    """

    def __init__(self) -> None:
        self._logger = get_logger("mission_compiler")

    async def compile(self, mission_objective: str, constraints: dict[str, Any] | None = None) -> MissionIR:
        """
        Compile mission objective into MIR.

        Steps:
        1. Analyze objective complexity
        2. Design organization blueprint
        3. Generate department specs
        4. Create task DAG
        5. Estimate resources
        6. Derive success criteria
        """
        constraints = constraints or {}
        mission_id = str(uuid4())

        # Analyze complexity
        complexity = self._infer_complexity(mission_objective)

        # Design organization
        org_blueprint = self._design_organization(mission_objective, complexity)

        # Generate departments
        dept_specs = self._generate_departments(org_blueprint)

        # Create task DAG
        task_dag = self._generate_task_dag(dept_specs)

        # Estimate resources
        resources = self._estimate_resources(complexity, dept_specs)

        # Derive success criteria
        success_criteria = self._derive_success_criteria(mission_objective)

        # Estimate duration
        duration = self._estimate_duration(complexity, len(dept_specs))

        mir = MissionIR(
            mission_id=mission_id,
            objective=mission_objective,
            organization_blueprint=org_blueprint,
            department_specs=dept_specs,
            task_dag=task_dag,
            resource_manifest=resources,
            success_criteria=success_criteria,
            estimated_complexity=complexity,
            estimated_duration_hours=duration,
            confidence=0.75,
        )

        self._logger.info(
            "Mission compiled: %s (complexity=%s, departments=%d, tasks=%d)",
            mission_id,
            complexity,
            len(dept_specs),
            len(task_dag),
        )

        return mir

    def _infer_complexity(self, objective: str) -> str:
        """Infer mission complexity from objective."""
        # Simplified heuristic - production would use LLM
        word_count = len(objective.split())

        if word_count > 50:
            return "high"
        elif word_count > 20:
            return "medium"
        else:
            return "low"

    def _design_organization(self, objective: str, complexity: str) -> dict[str, Any]:
        """Design organization blueprint based on objective."""
        # Default org structure
        org = {
            "ceo": True,
            "executives": ["CTO", "COO", "CFO"],
            "hierarchy_depth": 2 if complexity == "low" else 3,
        }

        # Add specialized executives based on keywords
        if "market" in objective.lower() or "launch" in objective.lower():
            org["executives"].append("CMO")

        if "research" in objective.lower() or "explore" in objective.lower():
            org["executives"].append("CRO")

        if "secure" in objective.lower() or "compliance" in objective.lower():
            org["executives"].append("CSO")
            org["executives"].append("CLO")

        return org

    def _generate_departments(self, org_blueprint: dict[str, Any]) -> list[dict[str, Any]]:
        """Generate department specifications."""
        departments = []

        # Core departments
        departments.append({"type": "engineering", "required": True, "workers": 3})
        departments.append({"type": "qa", "required": True, "workers": 1})

        # Add departments based on executives
        if "CMO" in org_blueprint["executives"]:
            departments.append({"type": "marketing", "required": True, "workers": 2})

        if "CRO" in org_blueprint["executives"]:
            departments.append({"type": "research", "required": True, "workers": 2})

        if "CSO" in org_blueprint["executives"]:
            departments.append({"type": "security", "required": True, "workers": 1})

        if "CLO" in org_blueprint["executives"]:
            departments.append({"type": "legal", "required": False, "workers": 1})

        return departments

    def _generate_task_dag(self, dept_specs: list[dict[str, Any]]) -> dict[str, list[str]]:
        """Generate task dependency DAG."""
        # Simplified DAG - production would analyze objective
        dag = {
            "task-1-planning": [],
            "task-2-research": ["task-1-planning"],
            "task-3-implementation": ["task-2-research"],
            "task-4-testing": ["task-3-implementation"],
            "task-5-deployment": ["task-4-testing"],
        }

        return dag

    def _estimate_resources(self, complexity: str, dept_specs: list[dict[str, Any]]) -> dict[str, Any]:
        """Estimate resource requirements."""
        worker_count = sum(dept.get("workers", 0) for dept in dept_specs)

        base_budget = {"low": 1000, "medium": 5000, "high": 20000}

        return {
            "budget": base_budget.get(complexity, 5000),
            "compute_hours": worker_count * 10,
            "gpu_hours": 0 if complexity == "low" else 5,
            "api_quota": 100000,
        }

    def _derive_success_criteria(self, objective: str) -> list[dict[str, Any]]:
        """Derive success criteria from objective."""
        return [
            {"metric": "mission_completed", "threshold": 1.0, "weight": 0.4},
            {"metric": "quality_score", "threshold": 0.8, "weight": 0.3},
            {"metric": "budget_efficiency", "threshold": 0.9, "weight": 0.2},
            {"metric": "stakeholder_satisfaction", "threshold": 0.85, "weight": 0.1},
        ]

    def _estimate_duration(self, complexity: str, department_count: int) -> float:
        """Estimate mission duration in hours."""
        base_hours = {"low": 2.0, "medium": 8.0, "high": 24.0}

        return base_hours.get(complexity, 8.0) * (department_count / 3.0)
