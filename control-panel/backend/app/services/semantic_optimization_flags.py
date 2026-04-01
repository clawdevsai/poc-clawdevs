"""Semantic Optimization Feature Flags - Week 4 Rollout Strategy."""

from app.core.config import get_settings


class SemanticOptimizationFlags:
    """Feature flag manager for semantic optimization tasks."""

    # Task names to env var mapping
    TASK_FLAGS = {
        "query_enhancement": "SEMANTIC_OPT_QUERY_ENHANCEMENT",
        "semantic_reranking": "SEMANTIC_OPT_SEMANTIC_RERANKING",
        "adaptive_compression": "SEMANTIC_OPT_ADAPTIVE_COMPRESSION",
        "summarization": "SEMANTIC_OPT_SUMMARIZATION",
        "categorization": "SEMANTIC_OPT_CATEGORIZATION",
        "anomaly_detection": "SEMANTIC_OPT_ANOMALY_DETECTION",
        "context_suggestion": "SEMANTIC_OPT_CONTEXT_SUGGESTION",
    }

    def __init__(self):
        self.settings = get_settings()
        self.canary_agents = self._parse_canary_agents()

    def _parse_canary_agents(self) -> set[str]:
        """Parse comma-separated canary agent list."""
        canary_str = self.settings.SEMANTIC_OPT_CANARY_AGENTS
        if not canary_str:
            return set()
        return {agent.strip() for agent in canary_str.split(",") if agent.strip()}

    def is_enabled(self, task_name: str, agent_id: str | None = None) -> bool:
        """
        Check if a task is enabled for an agent.

        Args:
            task_name: Task identifier (e.g., 'query_enhancement')
            agent_id: Agent ID (for canary deployments)

        Returns:
            True if task is enabled for the agent
        """
        if task_name not in self.TASK_FLAGS:
            return False

        flag_name = self.TASK_FLAGS[task_name]
        is_enabled = getattr(self.settings, flag_name, False)

        # If not enabled globally, check canary deployment
        if not is_enabled and agent_id:
            return agent_id in self.canary_agents

        return is_enabled

    def get_all_status(self) -> dict[str, dict]:
        """Get status of all feature flags."""
        return {
            task: {
                "enabled": getattr(self.settings, flag_name, False),
                "flag_name": flag_name,
            }
            for task, flag_name in self.TASK_FLAGS.items()
        }

    def get_canary_agents(self) -> list[str]:
        """Get list of canary agents."""
        return sorted(list(self.canary_agents))


# Singleton instance
flags = SemanticOptimizationFlags()
