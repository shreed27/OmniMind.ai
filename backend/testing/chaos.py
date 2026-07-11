"""
Chaos Engineering - TASK-15.3

Inject failures to test resilience and recovery.
"""

from __future__ import annotations

import random
from typing import Any

from kernel.core.logging import get_logger


class ChaosScenario:
    """Chaos testing scenarios."""

    NETWORK_PARTITION = "network_partition"
    DATABASE_UNAVAILABLE = "database_unavailable"
    SLOW_RESPONSE = "slow_response"
    MEMORY_PRESSURE = "memory_pressure"
    WORKER_CRASH = "worker_crash"
    EVENT_LOSS = "event_loss"


class ChaosEngine:
    """
    Chaos engineering engine for resilience testing.

    Injects controlled failures to validate:
    - Automatic retries
    - Fallback mechanisms
    - Data consistency during failures
    - Recovery time
    """

    def __init__(self) -> None:
        self._logger = get_logger("chaos")
        self._enabled = False
        self._failure_rate = 0.1  # 10% failure rate
        self._active_scenarios: set[str] = set()

    def enable(self, failure_rate: float = 0.1) -> None:
        """Enable chaos testing."""
        self._enabled = True
        self._failure_rate = failure_rate
        self._logger.warning("Chaos engineering enabled with %.1f%% failure rate", failure_rate * 100)

    def disable(self) -> None:
        """Disable chaos testing."""
        self._enabled = False
        self._active_scenarios.clear()
        self._logger.info("Chaos engineering disabled")

    def inject_scenario(self, scenario: str) -> None:
        """Activate chaos scenario."""
        self._active_scenarios.add(scenario)
        self._logger.warning("Chaos scenario activated: %s", scenario)

    def should_fail(self, operation: str = "default") -> bool:
        """
        Determine if operation should fail.

        Returns:
            True if chaos failure should be injected
        """
        if not self._enabled:
            return False

        return random.random() < self._failure_rate

    def inject_database_failure(self) -> Exception:
        """Inject database unavailability."""
        if ChaosScenario.DATABASE_UNAVAILABLE in self._active_scenarios:
            raise ConnectionError("Chaos: Database unavailable")

        if self.should_fail():
            raise ConnectionError("Chaos: Transient database failure")

        return None  # No failure

    def inject_network_partition(self) -> Exception | None:
        """Inject network partition."""
        if ChaosScenario.NETWORK_PARTITION in self._active_scenarios:
            raise TimeoutError("Chaos: Network partition")

        if self.should_fail():
            raise TimeoutError("Chaos: Transient network failure")

        return None

    def inject_slow_response(self, operation: str) -> float:
        """
        Inject artificial latency.

        Returns:
            Additional delay in seconds
        """
        if ChaosScenario.SLOW_RESPONSE in self._active_scenarios:
            delay = random.uniform(5.0, 15.0)
            self._logger.warning("Chaos: Injecting %.2fs delay for %s", delay, operation)
            return delay

        if self.should_fail():
            delay = random.uniform(1.0, 3.0)
            return delay

        return 0.0

    def inject_worker_crash(self) -> Exception | None:
        """Inject worker crash."""
        if ChaosScenario.WORKER_CRASH in self._active_scenarios:
            raise RuntimeError("Chaos: Worker crash")

        if self.should_fail():
            raise RuntimeError("Chaos: Worker transient failure")

        return None

    async def validate_recovery(self, operation: callable) -> dict[str, Any]:
        """
        Validate recovery from injected failure.

        Returns:
            Recovery metrics
        """
        import time

        start = time.time()
        attempts = 0
        max_attempts = 5

        while attempts < max_attempts:
            attempts += 1
            try:
                await operation()
                recovery_time = time.time() - start

                return {
                    "recovered": True,
                    "attempts": attempts,
                    "recovery_time_ms": recovery_time * 1000,
                }
            except Exception as exc:
                self._logger.warning("Recovery attempt %d failed: %s", attempts, exc)
                await asyncio.sleep(0.5 * attempts)  # Exponential backoff

        return {
            "recovered": False,
            "attempts": attempts,
            "recovery_time_ms": (time.time() - start) * 1000,
        }


# Global chaos engine
_chaos = ChaosEngine()


def get_chaos_engine() -> ChaosEngine:
    """Get global chaos engine."""
    return _chaos
