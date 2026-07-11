"""
Resource Ledger Service - TASK-10.1

Immutable debit/credit records for compute, GPU, budget, API quota.
Append-only ledger with balance computation.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from kernel.core.event import EventEnvelope
from kernel.core.exceptions import InvalidTransitionError
from kernel.core.logging import get_logger
from kernel.core.ports import EventBus


class ResourceType:
    """Canonical resource types."""

    BUDGET = "budget"
    COMPUTE = "compute"
    GPU = "gpu"
    API_QUOTA = "api_quota"
    STORAGE = "storage"
    NETWORK = "network"


class ResourceLedger:
    """
    Append-only immutable ledger for resource allocation tracking.

    Responsibilities:
    - Record debit/credit transactions
    - Compute running balances
    - Prevent double-spend
    - Support reconciliation queries
    """

    def __init__(self, event_bus: EventBus) -> None:
        self._bus = event_bus
        self._logger = get_logger("resource_ledger")
        self._ledger: list[dict[str, Any]] = []
        self._balances: dict[tuple[str, str, str], float] = {}  # (org_id, dept_id, resource_type) -> balance

    async def debit(
        self,
        *,
        organization_id: str,
        department_id: str | None,
        resource_type: str,
        amount: float,
        mission_id: str | None = None,
        approval_id: str | None = None,
        reason: str | None = None,
        trace_id: str | None = None,
    ) -> str:
        """
        Record debit transaction.

        Raises:
            InvalidTransitionError: If insufficient balance
        """
        if amount <= 0:
            raise ValueError("Debit amount must be positive")

        key = (organization_id, department_id or "org", resource_type)
        current_balance = self._balances.get(key, 0.0)

        if current_balance < amount:
            raise InvalidTransitionError(
                f"Insufficient balance for {resource_type}: {current_balance} < {amount}",
                context={
                    "organization_id": organization_id,
                    "department_id": department_id,
                    "resource_type": resource_type,
                    "requested": amount,
                    "available": current_balance,
                },
            )

        new_balance = current_balance - amount
        ledger_id = str(uuid4())

        entry = {
            "ledger_id": ledger_id,
            "organization_id": organization_id,
            "department_id": department_id,
            "mission_id": mission_id,
            "resource_type": resource_type,
            "amount": amount,
            "direction": "debit",
            "balance_after": new_balance,
            "approval_id": approval_id,
            "reason": reason,
            "trace_id": trace_id or str(uuid4()),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        self._ledger.append(entry)
        self._balances[key] = new_balance

        # Emit event
        event = EventEnvelope.create(
            name="ResourceAllocated",
            payload=entry,
            mission_id=mission_id,
            organization_id=organization_id,
            department_id=department_id,
            trace_id=trace_id,
            confidence=1.0,
            source={"service": "kernel", "module": "resource_ledger", "component": "debit"},
        )

        await self._bus.publish(event)
        self._logger.info("Debit recorded: %s %s from %s/%s", amount, resource_type, organization_id, department_id)

        return ledger_id

    async def credit(
        self,
        *,
        organization_id: str,
        department_id: str | None,
        resource_type: str,
        amount: float,
        mission_id: str | None = None,
        approval_id: str | None = None,
        reason: str | None = None,
        trace_id: str | None = None,
    ) -> str:
        """Record credit transaction."""
        if amount <= 0:
            raise ValueError("Credit amount must be positive")

        key = (organization_id, department_id or "org", resource_type)
        current_balance = self._balances.get(key, 0.0)
        new_balance = current_balance + amount
        ledger_id = str(uuid4())

        entry = {
            "ledger_id": ledger_id,
            "organization_id": organization_id,
            "department_id": department_id,
            "mission_id": mission_id,
            "resource_type": resource_type,
            "amount": amount,
            "direction": "credit",
            "balance_after": new_balance,
            "approval_id": approval_id,
            "reason": reason,
            "trace_id": trace_id or str(uuid4()),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        self._ledger.append(entry)
        self._balances[key] = new_balance

        # Emit event
        event = EventEnvelope.create(
            name="ResourceApproved",
            payload=entry,
            mission_id=mission_id,
            organization_id=organization_id,
            department_id=department_id,
            trace_id=trace_id,
            confidence=1.0,
            source={"service": "kernel", "module": "resource_ledger", "component": "credit"},
        )

        await self._bus.publish(event)
        self._logger.info("Credit recorded: %s %s to %s/%s", amount, resource_type, organization_id, department_id)

        return ledger_id

    def balance(self, organization_id: str, department_id: str | None, resource_type: str) -> float:
        """Query current balance."""
        key = (organization_id, department_id or "org", resource_type)
        return self._balances.get(key, 0.0)

    def reconcile(self, organization_id: str, department_id: str | None, resource_type: str) -> dict[str, Any]:
        """
        Reconciliation query - compute balance from ledger entries.

        Returns:
            Dict with expected_balance, actual_balance, transaction_count
        """
        key = (organization_id, department_id or "org", resource_type)

        # Compute from ledger
        computed_balance = 0.0
        transaction_count = 0

        for entry in self._ledger:
            if (
                entry["organization_id"] == organization_id
                and entry["department_id"] == department_id
                and entry["resource_type"] == resource_type
            ):
                transaction_count += 1
                if entry["direction"] == "credit":
                    computed_balance += entry["amount"]
                else:
                    computed_balance -= entry["amount"]

        actual_balance = self._balances.get(key, 0.0)

        return {
            "organization_id": organization_id,
            "department_id": department_id,
            "resource_type": resource_type,
            "expected_balance": computed_balance,
            "actual_balance": actual_balance,
            "transaction_count": transaction_count,
            "balanced": abs(computed_balance - actual_balance) < 1e-9,
        }

    def history(
        self,
        organization_id: str,
        department_id: str | None = None,
        resource_type: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Query ledger history with optional filters."""
        results = []

        for entry in reversed(self._ledger):
            if len(results) >= limit:
                break

            if entry["organization_id"] != organization_id:
                continue

            if department_id is not None and entry["department_id"] != department_id:
                continue

            if resource_type is not None and entry["resource_type"] != resource_type:
                continue

            results.append(entry)

        return results
