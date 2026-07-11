"""
Resource Policy Service - TASK-10.2

Threshold-driven approval enforcement for expensive plans and runtimes.
Automatic escalation on budget exceeded or repeated failures.
"""

from __future__ import annotations

from typing import Any

from kernel.core.event import EventEnvelope
from kernel.core.logging import get_logger
from kernel.core.ports import EventBus
from kernel.services.resource_ledger import ResourceLedger


class ResourcePolicy:
    """
    Resource policy enforcement with threshold-based approval gates.

    Rules:
    - Budget exceeded > 20% requires CFO approval
    - Repeated failures trigger auto-escalation
    - Policy changes visible as Mission Graph nodes
    """

    BUDGET_THRESHOLD_PERCENT = 0.20  # 20%
    FAILURE_THRESHOLD = 3

    def __init__(self, event_bus: EventBus, ledger: ResourceLedger) -> None:
        self._bus = event_bus
        self._ledger = ledger
        self._logger = get_logger("resource_policy")
        self._failure_counts: dict[str, int] = {}  # mission_id -> count

    async def check_budget_threshold(
        self,
        *,
        organization_id: str,
        department_id: str | None,
        requested_amount: float,
        allocated_budget: float,
        mission_id: str | None = None,
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Check if budget request requires CFO approval.

        Returns:
            Dict with {requires_approval: bool, reason: str, severity: str}
        """
        current_balance = self._ledger.balance(organization_id, department_id, "budget")

        # Check if request exceeds threshold
        threshold_amount = allocated_budget * self.BUDGET_THRESHOLD_PERCENT
        percentage = (requested_amount / allocated_budget * 100) if allocated_budget > 0 else 100

        requires_approval = requested_amount > threshold_amount

        result = {
            "requires_approval": requires_approval,
            "requested_amount": requested_amount,
            "current_balance": current_balance,
            "allocated_budget": allocated_budget,
            "threshold_amount": threshold_amount,
            "percentage": percentage,
            "reason": f"Budget request {percentage:.1f}% of allocation" if requires_approval else "Within threshold",
            "severity": "high" if requires_approval else "normal",
            "approver": "CFO" if requires_approval else None,
        }

        if requires_approval:
            # Emit approval request event
            event = EventEnvelope.create(
                name="ApprovalRequested",
                payload={
                    "policy_type": "budget_threshold",
                    "organization_id": organization_id,
                    "department_id": department_id,
                    "mission_id": mission_id,
                    "requested_amount": requested_amount,
                    "threshold_exceeded": True,
                    "required_authority": "CFO",
                    **result,
                },
                mission_id=mission_id,
                organization_id=organization_id,
                department_id=department_id,
                trace_id=trace_id,
                confidence=1.0,
                source={"service": "kernel", "module": "resource_policy", "component": "budget_check"},
            )

            await self._bus.publish(event)
            self._logger.warning(
                "Budget threshold exceeded for %s/%s: %.1f%% of allocation",
                organization_id,
                department_id,
                percentage,
            )

        return result

    async def record_failure(
        self,
        *,
        mission_id: str,
        organization_id: str,
        department_id: str | None = None,
        reason: str | None = None,
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Record failure and check if escalation required.

        Returns:
            Dict with {failure_count, requires_escalation, escalation_path}
        """
        self._failure_counts[mission_id] = self._failure_counts.get(mission_id, 0) + 1
        failure_count = self._failure_counts[mission_id]

        requires_escalation = failure_count >= self.FAILURE_THRESHOLD

        result = {
            "mission_id": mission_id,
            "failure_count": failure_count,
            "threshold": self.FAILURE_THRESHOLD,
            "requires_escalation": requires_escalation,
            "escalation_path": ["Manager", "Executive Board"] if requires_escalation else None,
            "reason": reason,
        }

        if requires_escalation:
            # Emit escalation event
            event = EventEnvelope.create(
                name="ApprovalEscalated",
                payload={
                    "policy_type": "repeated_failure",
                    "mission_id": mission_id,
                    "organization_id": organization_id,
                    "department_id": department_id,
                    "failure_count": failure_count,
                    "escalation_reason": f"Repeated failures ({failure_count})",
                    "escalation_path": result["escalation_path"],
                },
                mission_id=mission_id,
                organization_id=organization_id,
                department_id=department_id,
                trace_id=trace_id,
                confidence=0.7,
                source={"service": "kernel", "module": "resource_policy", "component": "failure_tracking"},
            )

            await self._bus.publish(event)
            self._logger.error(
                "Repeated failure threshold exceeded for mission %s: %d failures",
                mission_id,
                failure_count,
            )

        return result

    async def update_policy(
        self,
        *,
        policy_name: str,
        policy_value: Any,
        organization_id: str,
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Update policy configuration - emits PolicyUpdated event visible in Mission Graph.

        Returns:
            Dict with policy update details
        """
        result = {
            "policy_name": policy_name,
            "policy_value": policy_value,
            "organization_id": organization_id,
            "updated_at": EventEnvelope.now({}),
        }

        # Emit policy change event
        event = EventEnvelope.create(
            name="PolicyUpdated",
            payload={
                "policy_name": policy_name,
                "new_value": policy_value,
                "organization_id": organization_id,
            },
            organization_id=organization_id,
            trace_id=trace_id,
            confidence=1.0,
            source={"service": "kernel", "module": "resource_policy", "component": "policy_update"},
        )

        await self._bus.publish(event)
        self._logger.info("Policy updated: %s = %s for org %s", policy_name, policy_value, organization_id)

        return result

    def reset_failure_count(self, mission_id: str) -> None:
        """Reset failure count for mission (e.g., after successful completion)."""
        if mission_id in self._failure_counts:
            del self._failure_counts[mission_id]
            self._logger.info("Reset failure count for mission %s", mission_id)
