"""Test context window metrics tracking."""

import pytest
from app.services.context_metrics import ContextMetrics, ContextMetricsTracker


def test_context_metrics_calculation():
    """Test context metric calculations."""
    metric = ContextMetrics(
        task_name="query_enhancement",
        baseline_tokens=1000,
        optimized_tokens=300,
        timestamp=None,
    )

    assert metric.reduction_tokens == 700
    assert metric.reduction_ratio == pytest.approx(0.7)
    assert metric.reduction_percent == "70.0%"


def test_context_metrics_zero_baseline():
    """Test with zero baseline (edge case)."""
    metric = ContextMetrics(
        task_name="query_enhancement",
        baseline_tokens=0,
        optimized_tokens=0,
        timestamp=None,
    )

    assert metric.reduction_ratio == 0.0
    assert metric.reduction_percent == "0.0%"


def test_tracker_empty_summary():
    """Test tracker with no metrics."""
    tracker = ContextMetricsTracker()
    summary = tracker.get_summary()

    assert summary["total_executions"] == 0
    assert summary["baseline_total_tokens"] == 0
    assert summary["compression_ratio"] == 0.0


def test_tracker_record_single():
    """Test recording a single metric."""
    tracker = ContextMetricsTracker()
    metric = tracker.record("query_enhancement", 1000, 300)

    assert metric.baseline_tokens == 1000
    assert metric.reduction_ratio == pytest.approx(0.7)

    summary = tracker.get_summary()
    assert summary["total_executions"] == 1
    assert summary["baseline_total_tokens"] == 1000
    assert summary["optimized_total_tokens"] == 300
    assert summary["tokens_saved_total"] == 700


def test_tracker_record_multiple():
    """Test recording multiple metrics from different tasks."""
    tracker = ContextMetricsTracker()

    tracker.record("query_enhancement", 1000, 300)
    tracker.record("summarization", 2000, 500)
    tracker.record("query_enhancement", 1500, 450)

    summary = tracker.get_summary()
    assert summary["total_executions"] == 3
    assert summary["baseline_total_tokens"] == 4500
    assert summary["tokens_saved_total"] == 2750
    assert summary["compression_ratio"] == pytest.approx(2750 / 4500)

    # Per-task metrics
    assert summary["per_task"]["query_enhancement"]["executions"] == 2
    assert summary["per_task"]["query_enhancement"]["baseline_tokens"] == 2500
    assert summary["per_task"]["summarization"]["executions"] == 1
