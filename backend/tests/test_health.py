"""Tests for Health Checks - TASK-15.1"""

from __future__ import annotations

import pytest

from backend.observability.health import HealthChecker, HealthStatus


@pytest.mark.asyncio
async def test_health_check() -> None:
    """Health check aggregates component status."""
    checker = HealthChecker()

    health = await checker.check_health()

    assert "status" in health
    assert "components" in health
    assert "timestamp" in health


@pytest.mark.asyncio
async def test_liveness_probe() -> None:
    """Liveness probe returns True when service is running."""
    checker = HealthChecker()

    is_alive = await checker.liveness()

    assert is_alive is True


@pytest.mark.asyncio
async def test_readiness_probe() -> None:
    """Readiness probe returns True when ready for traffic."""
    checker = HealthChecker()

    is_ready = await checker.readiness()

    assert is_ready is True


@pytest.mark.asyncio
async def test_component_health_breakdown() -> None:
    """Health check includes individual component status."""
    checker = HealthChecker()

    health = await checker.check_health()

    assert "postgres" in health["components"]
    assert "neo4j" in health["components"]
    assert "redis" in health["components"]
    assert "qdrant" in health["components"]
