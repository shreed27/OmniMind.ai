"""
Counterfactual Analysis - TASK-17.1

"What if" scenario simulation without modifying production.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from kernel.core.logging import get_logger


class CounterfactualEngine:
    """
    Counterfactual simulation engine.

    Enables "what if" analysis:
    - What if research finished sooner?
    - What if budget doubled?
    - What if legal approved earlier?

    Simulations run in isolated branches - never modify production.
    """

    def __init__(self) -> None:
        self._logger = get_logger("counterfactual")
        self._simulations: dict[str, Any] = {}

    async def simulate(
        self,
        *,
        mission_id: str,
        scenario: str,
        assumptions: dict[str, Any],
        mission_snapshot: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Run counterfactual simulation.

        Args:
            mission_id: Original mission ID
            scenario: Scenario description
            assumptions: Alternative assumptions to test
            mission_snapshot: Current mission state

        Returns:
            Simulation results with predicted timeline/cost/confidence
        """
        simulation_id = str(uuid4())

        # Create isolated branch for simulation
        branch_id = f"sim-{simulation_id[:8]}"

        # Apply alternative assumptions
        modified_snapshot = self._apply_assumptions(mission_snapshot, assumptions)

        # Predict outcomes
        predictions = self._predict_outcomes(modified_snapshot, assumptions)

        # Compare with baseline
        comparison = self._compare_with_baseline(mission_snapshot, predictions)

        result = {
            "simulation_id": simulation_id,
            "mission_id": mission_id,
            "scenario": scenario,
            "branch_id": branch_id,
            "assumptions": assumptions,
            "predictions": predictions,
            "comparison": comparison,
            "confidence": 0.7,  # Simulations have lower confidence
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        self._simulations[simulation_id] = result

        self._logger.info(
            "Counterfactual simulation: %s for mission %s (scenario=%s)",
            simulation_id,
            mission_id,
            scenario,
        )

        return result

    def _apply_assumptions(self, snapshot: dict[str, Any], assumptions: dict[str, Any]) -> dict[str, Any]:
        """Apply alternative assumptions to snapshot."""
        modified = snapshot.copy()

        # Apply changes
        for key, value in assumptions.items():
            if key in modified:
                modified[key] = value

        return modified

    def _predict_outcomes(self, modified_snapshot: dict[str, Any], assumptions: dict[str, Any]) -> dict[str, Any]:
        """Predict mission outcomes under alternative assumptions."""
        # Simplified prediction - production would use ML model
        return {
            "predicted_timeline_hours": 16.0,
            "predicted_cost": 8000.0,
            "predicted_success_probability": 0.85,
            "predicted_organization_changes": assumptions.get("organization_changes", []),
            "predicted_bottlenecks": [],
        }

    def _compare_with_baseline(self, baseline: dict[str, Any], predictions: dict[str, Any]) -> dict[str, Any]:
        """Compare simulation predictions with baseline."""
        baseline_timeline = baseline.get("estimated_duration_hours", 20.0)
        predicted_timeline = predictions["predicted_timeline_hours"]

        timeline_delta = predicted_timeline - baseline_timeline
        timeline_improvement = (timeline_delta / baseline_timeline) * 100

        return {
            "timeline_delta_hours": timeline_delta,
            "timeline_improvement_percent": timeline_improvement,
            "cost_delta": 0.0,  # Placeholder
            "success_probability_delta": 0.0,  # Placeholder
        }

    async def discard_simulation(self, simulation_id: str) -> None:
        """
        Discard simulation branch.

        Production is never modified.
        """
        if simulation_id in self._simulations:
            del self._simulations[simulation_id]
            self._logger.info("Simulation discarded: %s", simulation_id)

    async def promote_simulation(self, simulation_id: str) -> dict[str, Any]:
        """
        Promote simulation to production (requires CEO approval).

        Returns:
            Merge request details
        """
        if simulation_id not in self._simulations:
            raise ValueError(f"Simulation not found: {simulation_id}")

        simulation = self._simulations[simulation_id]

        merge_request = {
            "simulation_id": simulation_id,
            "branch_id": simulation["branch_id"],
            "requires_approval": True,
            "approver": "CEO",
            "predictions": simulation["predictions"],
        }

        self._logger.warning("Simulation promotion requested: %s (requires CEO approval)", simulation_id)

        return merge_request
