"""Tests for Mission Compiler - TASK-16.1"""

from __future__ import annotations

import pytest

from kernel.compiler.compiler import MissionCompiler


@pytest.mark.asyncio
async def test_mission_compilation() -> None:
    """Mission compiler generates MIR from objective."""
    compiler = MissionCompiler()

    mir = await compiler.compile(
        mission_objective="Launch an AI-powered SaaS product in 90 days",
    )

    assert mir.mission_id is not None
    assert mir.objective == "Launch an AI-powered SaaS product in 90 days"
    assert len(mir.department_specs) > 0
    assert len(mir.task_dag) > 0
    assert "budget" in mir.resource_manifest


@pytest.mark.asyncio
async def test_complexity_inference() -> None:
    """Compiler infers mission complexity from objective."""
    compiler = MissionCompiler()

    # Simple objective
    simple_mir = await compiler.compile("Fix bug in login page")
    assert simple_mir.estimated_complexity == "low"

    # Complex objective
    complex_objective = " ".join(["complex"] * 60)  # 60 words
    complex_mir = await compiler.compile(complex_objective)
    assert complex_mir.estimated_complexity == "high"


@pytest.mark.asyncio
async def test_organization_design() -> None:
    """Compiler designs appropriate organization structure."""
    compiler = MissionCompiler()

    mir = await compiler.compile(
        "Research and launch secure AI product with marketing campaign",
    )

    # Should include research, security, marketing departments
    dept_types = [dept["type"] for dept in mir.department_specs]

    assert "engineering" in dept_types
    assert "research" in dept_types or "marketing" in dept_types


@pytest.mark.asyncio
async def test_resource_estimation() -> None:
    """Compiler estimates resource requirements."""
    compiler = MissionCompiler()

    mir = await compiler.compile("Build MVP")

    assert mir.resource_manifest["budget"] > 0
    assert mir.resource_manifest["compute_hours"] > 0


@pytest.mark.asyncio
async def test_success_criteria_generation() -> None:
    """Compiler derives success criteria from objective."""
    compiler = MissionCompiler()

    mir = await compiler.compile("Achieve product-market fit")

    assert len(mir.success_criteria) > 0
    assert all("metric" in criterion for criterion in mir.success_criteria)
    assert all("threshold" in criterion for criterion in mir.success_criteria)
