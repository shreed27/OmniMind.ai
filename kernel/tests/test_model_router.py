"""Tests for Model Router - TASK-14.4"""

from __future__ import annotations

import pytest

from kernel.services.model_router import ModelRouter, ModelTier


def test_model_selection_by_complexity() -> None:
    """Model router selects appropriate tier based on complexity."""
    router = ModelRouter()

    # High complexity -> Frontier
    selection_high = router.select_model(task_complexity="high")
    assert selection_high["tier"] == ModelTier.FRONTIER

    # Medium complexity -> Performance
    selection_medium = router.select_model(task_complexity="medium")
    assert selection_medium["tier"] == ModelTier.PERFORMANCE

    # Low complexity -> Efficient
    selection_low = router.select_model(task_complexity="low")
    assert selection_low["tier"] == ModelTier.EFFICIENT


def test_budget_constraint_filtering() -> None:
    """Model router respects budget constraints."""
    router = ModelRouter()

    # Budget constraint filters expensive models
    selection = router.select_model(
        task_complexity="high",
        budget_constraint=5.00,  # Max $5 per 1M tokens
    )

    assert router.COST_PER_1M_TOKENS[selection["primary_model"]] <= 5.00


def test_fallback_chain() -> None:
    """Model selection includes fallback chain."""
    router = ModelRouter()

    selection = router.select_model(task_complexity="medium")

    assert "fallback_chain" in selection
    assert len(selection["fallback_chain"]) >= 1
    assert selection["primary_model"] == selection["fallback_chain"][0]


@pytest.mark.asyncio
async def test_execute_with_fallback() -> None:
    """Router executes task with fallback on failure."""
    router = ModelRouter()

    task = {"prompt": "Test task"}
    fallback_chain = ["claude-sonnet-4.5", "claude-haiku-4"]

    result, model_used = await router.execute_with_fallback(task, fallback_chain)

    assert model_used in fallback_chain
    assert "response" in result
