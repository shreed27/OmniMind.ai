"""Tests for Chaos Engineering - TASK-15.3"""

from __future__ import annotations

import pytest

from backend.testing.chaos import ChaosEngine, ChaosScenario


def test_chaos_disabled_by_default() -> None:
    """Chaos engine is disabled by default."""
    chaos = ChaosEngine()

    assert chaos.should_fail() is False


def test_chaos_enable_disable() -> None:
    """Chaos can be enabled and disabled."""
    chaos = ChaosEngine()

    chaos.enable(failure_rate=0.5)
    chaos.disable()

    assert chaos.should_fail() is False


def test_scenario_injection() -> None:
    """Chaos scenarios can be injected."""
    chaos = ChaosEngine()

    chaos.inject_scenario(ChaosScenario.DATABASE_UNAVAILABLE)

    with pytest.raises(ConnectionError, match="Database unavailable"):
        chaos.inject_database_failure()


def test_network_partition_injection() -> None:
    """Network partition can be injected."""
    chaos = ChaosEngine()

    chaos.inject_scenario(ChaosScenario.NETWORK_PARTITION)

    with pytest.raises(TimeoutError, match="Network partition"):
        chaos.inject_network_partition()


def test_slow_response_injection() -> None:
    """Artificial latency can be injected."""
    chaos = ChaosEngine()

    chaos.inject_scenario(ChaosScenario.SLOW_RESPONSE)

    delay = chaos.inject_slow_response("test_operation")

    assert delay > 0


def test_worker_crash_injection() -> None:
    """Worker crash can be injected."""
    chaos = ChaosEngine()

    chaos.inject_scenario(ChaosScenario.WORKER_CRASH)

    with pytest.raises(RuntimeError, match="Worker crash"):
        chaos.inject_worker_crash()
