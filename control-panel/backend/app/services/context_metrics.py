"""Track context window metrics: baseline vs optimized."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class ContextMetrics:
    """Track context compression metrics."""

    task_name: str
    baseline_tokens: int  # Original context size
    optimized_tokens: int  # After optimization
    timestamp: datetime

    @property
    def reduction_tokens(self) -> int:
        """Tokens saved by optimization."""
        return max(0, self.baseline_tokens - self.optimized_tokens)

    @property
    def reduction_ratio(self) -> float:
        """Compression ratio (0-1 scale)."""
        if self.baseline_tokens == 0:
            return 0.0
        return self.reduction_tokens / self.baseline_tokens

    @property
    def reduction_percent(self) -> str:
        """Human-readable reduction percentage."""
        return f"{self.reduction_ratio * 100:.1f}%"


class ContextMetricsTracker:
    """Track context optimization metrics across tasks."""

    def __init__(self):
        self.metrics: list[ContextMetrics] = []
        self.task_counters = {
            "query_enhancement": 0,
            "semantic_reranking": 0,
            "adaptive_compression": 0,
            "summarization": 0,
            "categorization": 0,
            "anomaly_detection": 0,
            "context_suggestion": 0,
        }

    def record(self, task_name: str, baseline: int, optimized: int) -> ContextMetrics:
        """Record a context optimization event."""
        metric = ContextMetrics(
            task_name=task_name,
            baseline_tokens=baseline,
            optimized_tokens=optimized,
            timestamp=datetime.utcnow(),
        )
        self.metrics.append(metric)
        self.task_counters[task_name] = self.task_counters.get(task_name, 0) + 1
        return metric

    def get_summary(self) -> dict:
        """Get aggregated metrics across all tasks."""
        if not self.metrics:
            return self._empty_summary()

        total_baseline = sum(m.baseline_tokens for m in self.metrics)
        total_optimized = sum(m.optimized_tokens for m in self.metrics)
        total_saved = sum(m.reduction_tokens for m in self.metrics)

        # Per-task metrics
        per_task = {}
        for task_name in self.task_counters.keys():
            task_metrics = [m for m in self.metrics if m.task_name == task_name]
            if task_metrics:
                baseline = sum(m.baseline_tokens for m in task_metrics)
                optimized = sum(m.optimized_tokens for m in task_metrics)
                per_task[task_name] = {
                    "executions": len(task_metrics),
                    "baseline_tokens": baseline,
                    "optimized_tokens": optimized,
                    "tokens_saved": baseline - optimized,
                    "reduction_ratio": (baseline - optimized) / baseline if baseline > 0 else 0,
                }

        return {
            "total_executions": len(self.metrics),
            "baseline_total_tokens": total_baseline,
            "optimized_total_tokens": total_optimized,
            "tokens_saved_total": total_saved,
            "compression_ratio": (total_saved / total_baseline) if total_baseline > 0 else 0,
            "per_task": per_task,
            "last_updated": self.metrics[-1].timestamp.isoformat() if self.metrics else None,
        }

    def _empty_summary(self) -> dict:
        """Return empty summary when no metrics recorded."""
        return {
            "total_executions": 0,
            "baseline_total_tokens": 0,
            "optimized_total_tokens": 0,
            "tokens_saved_total": 0,
            "compression_ratio": 0.0,
            "per_task": {},
            "last_updated": None,
        }


# Global singleton tracker
context_tracker = ContextMetricsTracker()
