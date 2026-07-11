"""Tests for Metrics Collection - TASK-15.1"""

from __future__ import annotations

from backend.observability.metrics import MetricsCollector


def test_counter_increment() -> None:
    """Counter metrics increment correctly."""
    metrics = MetricsCollector()

    metrics.increment("missions_created")
    metrics.increment("missions_created")
    metrics.increment("missions_created", value=3)

    exported = metrics.get_metrics()

    assert exported["counters"]["missions_created"] == 5


def test_gauge_setting() -> None:
    """Gauge metrics can be set."""
    metrics = MetricsCollector()

    metrics.set_gauge("organization_iq", 75.5)
    metrics.set_gauge("plasticity_score", 0.82)

    exported = metrics.get_metrics()

    assert exported["gauges"]["organization_iq"] == 75.5
    assert exported["gauges"]["plasticity_score"] == 0.82


def test_histogram_observation() -> None:
    """Histogram metrics compute statistics."""
    metrics = MetricsCollector()

    for i in range(100):
        metrics.observe("task_completion_time_ms", float(i))

    exported = metrics.get_metrics()
    histogram = exported["histograms"]["task_completion_time_ms"]

    assert histogram["count"] == 100
    assert histogram["min"] == 0.0
    assert histogram["max"] == 99.0
    assert 40 <= histogram["p50"] <= 60
    assert histogram["p95"] >= 90


def test_labeled_metrics() -> None:
    """Metrics support labels."""
    metrics = MetricsCollector()

    metrics.increment("tasks_completed", labels={"department": "engineering"})
    metrics.increment("tasks_completed", labels={"department": "marketing"})
    metrics.increment("tasks_completed", labels={"department": "engineering"})

    exported = metrics.get_metrics()

    assert exported["counters"]['tasks_completed{department="engineering"}'] == 2
    assert exported["counters"]['tasks_completed{department="marketing"}'] == 1


def test_metrics_reset() -> None:
    """Metrics can be reset."""
    metrics = MetricsCollector()

    metrics.increment("test_counter")
    metrics.set_gauge("test_gauge", 100.0)

    metrics.reset()

    exported = metrics.get_metrics()

    assert len(exported["counters"]) == 0
    assert len(exported["gauges"]) == 0
