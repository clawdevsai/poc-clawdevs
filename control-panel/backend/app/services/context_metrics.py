"""Track context window metrics: baseline vs optimized."""

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta, UTC

from sqlalchemy import func
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Agent, Approval, Metric, Session, Task


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

DEFAULT_WINDOW_MINUTES = 30
WINDOW_MINUTES_OPTIONS = {30, 60, 360, 1440}


def _to_naive_utc(dt: datetime | None) -> datetime | None:
    """Convert any datetime to naive UTC datetime."""
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt.astimezone(UTC).replace(tzinfo=None)
    return dt


def validate_window_minutes(
    window_minutes: int | None,
    *,
    allow_none: bool = False,
) -> int | None:
    """Validate allowed time window values for monitoring queries."""
    if window_minutes is None:
        if allow_none:
            return None
        raise ValueError("window_minutes is required")
    if window_minutes not in WINDOW_MINUTES_OPTIONS:
        raise ValueError(
            f"window_minutes must be one of {sorted(WINDOW_MINUTES_OPTIONS)}"
        )
    return window_minutes


async def compute_overview_metrics(
    session: AsyncSession,
    window_minutes: int,
) -> dict:
    """Compute overview metrics for monitoring dashboards."""
    window_since = _to_naive_utc(
        datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
    )
    since_24h = _to_naive_utc(datetime.now(timezone.utc) - timedelta(hours=24))

    agents_result = await session.exec(
        select(Agent).where(col(Agent.status).in_(["online", "working"]))
    )
    active_agents = len(agents_result.all())

    approvals_result = await session.exec(
        select(Approval).where(Approval.status == "pending")
    )
    pending_approvals = len(approvals_result.all())

    open_tasks_result = await session.exec(
        select(Task).where(col(Task.status).in_(["inbox", "in_progress", "review"]))
    )
    open_tasks = len(open_tasks_result.all())

    metrics_result = await session.exec(
        select(Metric).where(
            col(Metric.metric_type) == "tokens_used",
            col(Metric.period_start) >= since_24h,
        )
    )
    tokens_24h = sum(m.value for m in metrics_result.all())

    status_counts_result = await session.exec(
        select(Task.status, func.count(Task.id))
        .where(col(Task.updated_at) >= window_since)
        .group_by(Task.status)
    )
    status_counts = {status: count for status, count in status_counts_result.all()}

    backlog_count = int(status_counts.get("inbox", 0) or 0)
    tasks_in_progress = int(status_counts.get("in_progress", 0) or 0)
    tasks_completed = int(status_counts.get("done", 0) or 0)

    tokens_result = await session.exec(
        select(func.coalesce(func.sum(Session.token_count), 0)).where(
            func.coalesce(Session.last_active_at, Session.created_at) >= window_since
        )
    )
    tokens_consumed_total = float(tokens_result.one() or 0)
    tokens_consumed_avg_per_task = tokens_consumed_total / max(tasks_completed, 1)

    return {
        "active_agents": active_agents,
        "pending_approvals": pending_approvals,
        "open_tasks": open_tasks,
        "tokens_24h": float(tokens_24h),
        "tokens_consumed_total": tokens_consumed_total,
        "tokens_consumed_avg_per_task": float(tokens_consumed_avg_per_task),
        "backlog_count": backlog_count,
        "tasks_in_progress": tasks_in_progress,
        "tasks_completed": tasks_completed,
    }
