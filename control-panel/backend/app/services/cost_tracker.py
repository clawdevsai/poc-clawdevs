# Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Cost Tracker - Manages and enforces cost budgets

Tracks token usage and ensures costs stay within
tier-based budgets per agent and task.
"""

import logging
from typing import Any, Optional, Dict, Tuple
from uuid import UUID
from datetime import datetime, timedelta, UTC

from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.task import Task
from app.models.agent import Agent
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class CostTracker:
    """Track and enforce cost budgets."""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def estimate_task_cost(
        self,
        task_type: str,
        complexity: str,
        estimated_tokens: int = 5000,
    ) -> Dict[str, float]:
        """
        Estimate cost for a task based on complexity.

        Args:
            task_type: Type of task
            complexity: Complexity level (simple, medium, complex)
            estimated_tokens: Expected token count

        Returns:
            Dict with local, medium, premium cost estimates
        """
        # Estimate tokens based on complexity
        if complexity == "simple":
            tokens = 2000
        elif complexity == "medium":
            tokens = 10000
        else:
            tokens = 50000

        estimates = {
            "local": self._calculate_cost(tokens, "ollama"),
            "medium": self._calculate_cost(tokens, "claude-3-haiku"),
            "premium": self._calculate_cost(tokens, "claude-3-opus"),
        }

        return estimates

    async def track_actual_cost(
        self,
        task_id: UUID,
        tokens_used: int,
        model: str,
    ) -> None:
        """
        Track actual cost for a completed task.

        Args:
            task_id: Task that was executed
            tokens_used: Number of tokens consumed
            model: Model used
        """
        task = (
            await self.db_session.exec(select(Task).where(Task.id == task_id))
        ).first()
        if not task:
            logger.warning(f"Task {task_id} not found for cost tracking")
            return

        cost = self._calculate_cost(tokens_used, model)
        task.actual_cost = cost

        logger.info(f"Task {task_id}: {tokens_used} tokens on {model} = ${cost:.4f}")

        self.db_session.add(task)
        await self.db_session.commit()

    async def check_budget_available(
        self,
        agent_id: UUID,
        task_tier: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if agent has budget available for task tier.

        Args:
            agent_id: Agent requesting resources
            task_tier: Tier of task (local, medium, premium)

        Returns:
            (is_available, warning_message)
        """
        agent = (
            await self.db_session.exec(select(Agent).where(Agent.id == agent_id))
        ).first()

        if not agent:
            return False, "Agent not found"

        # Get agent's tasks from this month
        month_ago = datetime.now(UTC) - timedelta(days=30)
        statement = select(Task).where(
            (col(Task.assigned_agent_id) == agent_id)
            & (col(Task.created_at) >= month_ago)
            & (col(Task.actual_cost).is_not(None))
        )

        tasks = (await self.db_session.exec(statement)).all()
        total_spent = sum(float(t.actual_cost or 0) for t in tasks)

        settings = get_settings()
        budget = settings.cost_tier_budgets[task_tier]["max_monthly"]
        remaining = budget - total_spent

        if remaining <= 0:
            return False, f"Budget exhausted for {task_tier} tier (${budget})"

        if remaining < budget * 0.2:  # Less than 20% left
            return (
                True,
                f"Warning: Only ${remaining:.2f} remaining in {task_tier} budget",
            )

        return True, None

    async def warn_on_cost_overrun(
        self,
        task_id: UUID,
        threshold: float = 1.5,
    ) -> Optional[str]:
        """
        Warn if task cost exceeds estimated by threshold.

        Args:
            task_id: Task to check
            threshold: Alert if actual > estimated * threshold

        Returns:
            Warning message if overrun detected
        """
        task = (
            await self.db_session.exec(select(Task).where(Task.id == task_id))
        ).first()
        if not task or not task.estimated_cost or not task.actual_cost:
            return None

        ratio = task.actual_cost / task.estimated_cost
        if ratio > threshold:
            message = (
                f"Task {task_id} cost overrun: "
                f"estimated ${task.estimated_cost:.2f}, "
                f"actual ${task.actual_cost:.2f} ({ratio:.1f}x)"
            )
            logger.warning(message)
            return message

        return None

    async def get_agent_spending(
        self,
        agent_id: UUID,
        days: int = 30,
    ) -> Dict[str, float]:
        """
        Get agent's spending summary.

        Args:
            agent_id: Agent to check
            days: Look back period

        Returns:
            Dict with spending by tier and total
        """
        cutoff_date = datetime.now(UTC) - timedelta(days=days)
        statement = select(Task).where(
            (col(Task.assigned_agent_id) == agent_id)
            & (col(Task.created_at) >= cutoff_date)
            & (col(Task.actual_cost).is_not(None))
        )

        tasks = (await self.db_session.exec(statement)).all()

        spending = {
            "local": 0.0,
            "medium": 0.0,
            "premium": 0.0,
            "total": 0.0,
            "task_count": len(tasks),
        }

        for task in tasks:
            tier = task.cost_tier or "medium"
            spending[tier] += float(task.actual_cost or 0)
            spending["total"] += float(task.actual_cost or 0)

        return spending

    async def get_team_spending(
        self,
        days: int = 30,
    ) -> Dict[str, float]:
        """
        Get team-wide spending summary.

        Args:
            days: Look back period

        Returns:
            Dict with total spending and breakdown
        """
        cutoff_date = datetime.now(UTC) - timedelta(days=days)
        statement = select(Task).where(
            (col(Task.created_at) >= cutoff_date) & (col(Task.actual_cost).is_not(None))
        )

        tasks = (await self.db_session.exec(statement)).all()

        spending = {
            "local": 0.0,
            "medium": 0.0,
            "premium": 0.0,
            "total": 0.0,
            "task_count": len(tasks),
        }

        for task in tasks:
            tier = task.cost_tier or "medium"
            spending[tier] += float(task.actual_cost or 0)
            spending["total"] += float(task.actual_cost or 0)

        # Calculate daily average
        spending["daily_average"] = spending["total"] / max(days, 1)

        return spending

    def _calculate_cost(self, tokens: int, model: str) -> float:
        """
        Calculate cost for tokens and model.

        Args:
            tokens: Number of tokens
            model: Model name

        Returns:
            Cost in USD
        """
        settings = get_settings()
        cost_per_1m = settings.token_costs_per_model.get(
            model, 0.003
        )  # Default to medium cost
        cost = (tokens / 1_000_000) * cost_per_1m
        return round(cost, 4)

    async def get_cost_recommendation(
        self,
        task_type: str,
        complexity: str,
    ) -> Dict[str, Any]:
        """
        Get cost recommendation for task.

        Args:
            task_type: Type of task
            complexity: Complexity level

        Returns:
            Dict with recommendation and reasoning
        """
        estimates = await self.estimate_task_cost(task_type, complexity)

        # Recommend based on complexity
        if complexity == "simple" or task_type in ["unit_test", "linting"]:
            recommended_tier = "local"
            reasoning = "Simple task, use free local models"
        elif complexity == "medium":
            recommended_tier = "medium"
            reasoning = "Medium complexity, balanced cost/quality"
        else:
            recommended_tier = "premium"
            reasoning = "Complex task, use most capable model"

        return {
            "recommended_tier": recommended_tier,
            "reasoning": reasoning,
            "estimated_costs": estimates,
            "warning": (
                "Premium tier can be expensive. " "Ensure complexity justifies cost."
                if recommended_tier == "premium"
                else None
            ),
        }
