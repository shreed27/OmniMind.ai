"""Tests for Resource Ledger Service - TASK-10.1"""

from __future__ import annotations

import pytest

from kernel.core.event_bus import InMemoryEventBus
from kernel.core.exceptions import InvalidTransitionError
from kernel.services.resource_ledger import ResourceLedger, ResourceType


@pytest.mark.asyncio
async def test_credit_increases_balance() -> None:
    """Credit transaction increases balance."""
    bus = InMemoryEventBus()
    ledger = ResourceLedger(event_bus=bus)

    ledger_id = await ledger.credit(
        organization_id="org-1",
        department_id="eng",
        resource_type=ResourceType.BUDGET,
        amount=1000.0,
        reason="initial_allocation",
    )

    assert ledger_id is not None
    assert ledger.balance("org-1", "eng", ResourceType.BUDGET) == 1000.0


@pytest.mark.asyncio
async def test_debit_decreases_balance() -> None:
    """Debit transaction decreases balance."""
    bus = InMemoryEventBus()
    ledger = ResourceLedger(event_bus=bus)

    await ledger.credit(
        organization_id="org-1",
        department_id="eng",
        resource_type=ResourceType.BUDGET,
        amount=1000.0,
    )

    await ledger.debit(
        organization_id="org-1",
        department_id="eng",
        resource_type=ResourceType.BUDGET,
        amount=300.0,
        reason="gpu_allocation",
    )

    assert ledger.balance("org-1", "eng", ResourceType.BUDGET) == 700.0


@pytest.mark.asyncio
async def test_insufficient_balance_raises_error() -> None:
    """Debit with insufficient balance raises InvalidTransitionError."""
    bus = InMemoryEventBus()
    ledger = ResourceLedger(event_bus=bus)

    await ledger.credit(
        organization_id="org-1",
        department_id="eng",
        resource_type=ResourceType.BUDGET,
        amount=100.0,
    )

    with pytest.raises(InvalidTransitionError, match="Insufficient balance"):
        await ledger.debit(
            organization_id="org-1",
            department_id="eng",
            resource_type=ResourceType.BUDGET,
            amount=200.0,
        )


@pytest.mark.asyncio
async def test_reconciliation_matches_balance() -> None:
    """Reconciliation computes correct balance from ledger."""
    bus = InMemoryEventBus()
    ledger = ResourceLedger(event_bus=bus)

    await ledger.credit(organization_id="org-1", department_id="eng", resource_type=ResourceType.COMPUTE, amount=500.0)
    await ledger.debit(organization_id="org-1", department_id="eng", resource_type=ResourceType.COMPUTE, amount=150.0)
    await ledger.credit(organization_id="org-1", department_id="eng", resource_type=ResourceType.COMPUTE, amount=100.0)

    reconciliation = ledger.reconcile("org-1", "eng", ResourceType.COMPUTE)

    assert reconciliation["expected_balance"] == 450.0
    assert reconciliation["actual_balance"] == 450.0
    assert reconciliation["transaction_count"] == 3
    assert reconciliation["balanced"] is True


@pytest.mark.asyncio
async def test_ledger_is_append_only() -> None:
    """Ledger entries are immutable - no UPDATE/DELETE operations."""
    bus = InMemoryEventBus()
    ledger = ResourceLedger(event_bus=bus)

    await ledger.credit(organization_id="org-1", department_id="eng", resource_type=ResourceType.GPU, amount=10.0)

    history = ledger.history("org-1")
    assert len(history) == 1

    # Ledger should have no methods for update or delete
    assert not hasattr(ledger, "update")
    assert not hasattr(ledger, "delete")
    assert not hasattr(ledger, "remove")


@pytest.mark.asyncio
async def test_history_filtering() -> None:
    """History query supports filtering by department and resource type."""
    bus = InMemoryEventBus()
    ledger = ResourceLedger(event_bus=bus)

    await ledger.credit(organization_id="org-1", department_id="eng", resource_type=ResourceType.BUDGET, amount=1000.0)
    await ledger.credit(organization_id="org-1", department_id="marketing", resource_type=ResourceType.BUDGET, amount=500.0)
    await ledger.credit(organization_id="org-1", department_id="eng", resource_type=ResourceType.GPU, amount=5.0)

    eng_history = ledger.history("org-1", department_id="eng")
    assert len(eng_history) == 2

    budget_history = ledger.history("org-1", resource_type=ResourceType.BUDGET)
    assert len(budget_history) == 2

    eng_budget_history = ledger.history("org-1", department_id="eng", resource_type=ResourceType.BUDGET)
    assert len(eng_budget_history) == 1
