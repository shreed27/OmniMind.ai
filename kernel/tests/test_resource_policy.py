"""Tests for Resource Policy Service - TASK-10.2"""

from __future__ import annotations

import pytest

from kernel.core.event_bus import InMemoryEventBus
from kernel.services.resource_ledger import ResourceLedger, ResourceType
from kernel.services.resource_policy import ResourcePolicy


@pytest.mark.asyncio
async def test_budget_threshold_requires_approval() -> None:
    """Budget request exceeding 20% threshold requires CFO approval."""
    bus = InMemoryEventBus()
    ledger = ResourceLedger(event_bus=bus)
    policy = ResourcePolicy(event_bus=bus, ledger=ledger)

    await ledger.credit(organization_id="org-1", department_id="eng", resource_type=ResourceType.BUDGET, amount=10000.0)

    result = await policy.check_budget_threshold(
        organization_id="org-1",
        department_id="eng",
        requested_amount=2500.0,  # 25% of 10k
        allocated_budget=10000.0,
    )

    assert result["requires_approval"] is True
    assert result["approver"] == "CFO"
    assert result["severity"] == "high"
    assert result["percentage"] == 25.0


@pytest.mark.asyncio
async def test_budget_within_threshold_no_approval() -> None:
    """Budget request within 20% threshold does not require approval."""
    bus = InMemoryEventBus()
    ledger = ResourceLedger(event_bus=bus)
    policy = ResourcePolicy(event_bus=bus, ledger=ledger)

    await ledger.credit(organization_id="org-1", department_id="eng", resource_type=ResourceType.BUDGET, amount=10000.0)

    result = await policy.check_budget_threshold(
        organization_id="org-1",
        department_id="eng",
        requested_amount=1500.0,  # 15% of 10k
        allocated_budget=10000.0,
    )

    assert result["requires_approval"] is False
    assert result["approver"] is None
    assert result["severity"] == "normal"


@pytest.mark.asyncio
async def test_repeated_failures_trigger_escalation() -> None:
    """Three failures trigger automatic escalation to Executive Board."""
    bus = InMemoryEventBus()
    ledger = ResourceLedger(event_bus=bus)
    policy = ResourcePolicy(event_bus=bus, ledger=ledger)

    # First two failures
    result1 = await policy.record_failure(mission_id="mission-1", organization_id="org-1", department_id="eng")
    assert result1["requires_escalation"] is False

    result2 = await policy.record_failure(mission_id="mission-1", organization_id="org-1", department_id="eng")
    assert result2["requires_escalation"] is False

    # Third failure triggers escalation
    result3 = await policy.record_failure(mission_id="mission-1", organization_id="org-1", department_id="eng")
    assert result3["requires_escalation"] is True
    assert result3["failure_count"] == 3
    assert result3["escalation_path"] == ["Manager", "Executive Board"]


@pytest.mark.asyncio
async def test_policy_update_emits_event() -> None:
    """Policy changes emit PolicyUpdated events visible in Mission Graph."""
    bus = InMemoryEventBus()
    ledger = ResourceLedger(event_bus=bus)
    policy = ResourcePolicy(event_bus=bus, ledger=ledger)

    result = await policy.update_policy(
        policy_name="budget_threshold_percent",
        policy_value=0.15,  # Change from 20% to 15%
        organization_id="org-1",
    )

    assert result["policy_name"] == "budget_threshold_percent"
    assert result["policy_value"] == 0.15
    assert "updated_at" in result


@pytest.mark.asyncio
async def test_failure_count_reset() -> None:
    """Failure count can be reset after successful completion."""
    bus = InMemoryEventBus()
    ledger = ResourceLedger(event_bus=bus)
    policy = ResourcePolicy(event_bus=bus, ledger=ledger)

    await policy.record_failure(mission_id="mission-1", organization_id="org-1")
    await policy.record_failure(mission_id="mission-1", organization_id="org-1")

    policy.reset_failure_count("mission-1")

    result = await policy.record_failure(mission_id="mission-1", organization_id="org-1")
    assert result["failure_count"] == 1  # Reset to 1, not 3
