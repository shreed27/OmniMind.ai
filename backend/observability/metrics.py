"""
Metrics Collection - TASK-15.1

Prometheus-compatible metrics for kernel and organization health.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from kernel.core.logging import get_logger


class MetricType:
    """Metric types."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"


class MetricsCollector:
    """
    Metrics collector for observability.

    Metrics:
    - Mission success rate
    - Organization IQ
    - Plasticity score
    - Task completion time
    - Event bus throughput
    - Memory usage
    - Reflection quality
    """

    def __init__(self) -> None:
        self._logger = get_logger("metrics")
        self._counters: dict[str, int] = defaultdict(int)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)

    def increment(self, metric_name: str, value: int = 1, labels: dict[str, str] | None = None) -> None:
        """Increment counter metric."""
        key = self._metric_key(metric_name, labels)
        self._counters[key] += value

    def set_gauge(self, metric_name: str, value: float, labels: dict[str, str] | None = None) -> None:
        """Set gauge metric."""
        key = self._metric_key(metric_name, labels)
        self._gauges[key] = value

    def observe(self, metric_name: str, value: float, labels: dict[str, str] | None = None) -> None:
        """Observe histogram value."""
        key = self._metric_key(metric_name, labels)
        self._histograms[key].append(value)

    def _metric_key(self, metric_name: str, labels: dict[str, str] | None) -> str:
        """Generate metric key with labels."""
        if not labels:
            return metric_name

        label_str = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
        return f"{metric_name}{{{label_str}}}"

    def get_metrics(self) -> dict[str, Any]:
        """
        Export metrics in Prometheus format.

        Returns:
            Dict with counters, gauges, histograms
        """
        return {
            "counters": dict(self._counters),
            "gauges": self._gauges,
            "histograms": {k: self._compute_histogram_stats(v) for k, v in self._histograms.items()},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _compute_histogram_stats(self, values: list[float]) -> dict[str, float]:
        """Compute histogram statistics."""
        if not values:
            return {"count": 0, "sum": 0, "avg": 0, "min": 0, "max": 0, "p50": 0, "p95": 0, "p99": 0}

        sorted_values = sorted(values)
        count = len(sorted_values)

        return {
            "count": count,
            "sum": sum(values),
            "avg": sum(values) / count,
            "min": min(values),
            "max": max(values),
            "p50": sorted_values[int(count * 0.5)],
            "p95": sorted_values[int(count * 0.95)] if count > 20 else sorted_values[-1],
            "p99": sorted_values[int(count * 0.99)] if count > 100 else sorted_values[-1],
        }

    def reset(self) -> None:
        """Reset all metrics."""
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()


# Global metrics instance
_metrics = MetricsCollector()


def get_metrics() -> MetricsCollector:
    """Get global metrics collector."""
    return _metrics
