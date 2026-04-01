"""Auto-compression hook: Execute semantic optimization tasks on agent output."""

import asyncio
import logging
from typing import Optional

from app.services.semantic_optimization_flags import flags
from app.services.context_metrics import context_tracker
from app.services.query_enhancer import QueryEnhancer
from app.services.semantic_ranker import SemanticRanker
from app.services.adaptive_compressor import AdaptiveCompressor
from app.services.summarizer import IntelligentSummarizer
from app.services.categorizer import MemoryCategorizer
from app.services.anomaly_detector import AnomalyDetector
from app.services.context_suggester import ContextSuggester

logger = logging.getLogger(__name__)


class SemanticOptimizationHook:
    """Execute semantic optimization tasks on agent output."""

    def __init__(self):
        self.query_enhancer = QueryEnhancer()
        self.semantic_ranker = SemanticRanker()
        self.adaptive_compressor = AdaptiveCompressor()
        self.summarizer = IntelligentSummarizer()
        self.categorizer = MemoryCategorizer()
        self.anomaly_detector = AnomalyDetector()
        self.context_suggester = ContextSuggester()

    async def process_agent_output(
        self, output: str, agent_id: str, tool_name: str = ""
    ) -> dict:
        """
        Process agent output through semantic optimization pipeline.

        Args:
            output: Agent tool output
            agent_id: Agent identifier
            tool_name: Name of the tool that produced output

        Returns:
            Dict with optimized output + metrics
        """
        baseline_tokens = len(output.split())
        results = {
            "original_output": output,
            "optimized_output": output,
            "baseline_tokens": baseline_tokens,
            "optimizations_applied": [],
        }

        try:
            # Check for anomalies first (may skip compression if anomaly detected)
            if flags.is_enabled("anomaly_detection", agent_id):
                anomaly_result = await self.anomaly_detector.detect(output, tool_name)
                if anomaly_result.get("anomaly_score", 0) > 0.7:
                    logger.info(f"Anomaly detected in {tool_name} output, skipping compression")
                    return results

            # Adaptive compression (content type aware)
            if flags.is_enabled("adaptive_compression", agent_id):
                compress_result = await self.adaptive_compressor.compress_adaptive(
                    output, tool_name
                )
                results["optimized_output"] = compress_result.get("compressed", output)
                results["optimizations_applied"].append("adaptive_compression")

            # Summarization (if output is long)
            if (
                flags.is_enabled("summarization", agent_id)
                and len(results["optimized_output"].split()) > 200
            ):
                summary_result = await self.summarizer.summarize(
                    results["optimized_output"], max_words=150
                )
                if summary_result.get("summary"):
                    results["optimized_output"] = summary_result["summary"]
                    results["optimizations_applied"].append("summarization")

            # Auto-categorization (for memory storage)
            if flags.is_enabled("categorization", agent_id):
                category_result = await self.categorizer.categorize(
                    results["optimized_output"]
                )
                results["category"] = category_result.get("category", "unknown")
                results["optimizations_applied"].append("categorization")

            # Track metrics
            optimized_tokens = len(results["optimized_output"].split())
            context_tracker.record(
                task_name="auto_compression_pipeline",
                baseline=baseline_tokens,
                optimized=optimized_tokens,
            )
            results["optimized_tokens"] = optimized_tokens
            results["tokens_saved"] = baseline_tokens - optimized_tokens
            results["compression_ratio"] = (
                (baseline_tokens - optimized_tokens) / baseline_tokens
                if baseline_tokens > 0
                else 0.0
            )

        except Exception as e:
            logger.error(f"Error in semantic optimization hook: {e}")
            # On error, return original output
            pass

        return results


# Global singleton
semantic_optimization_hook = SemanticOptimizationHook()


async def apply_semantic_optimization(
    output: str, agent_id: str, tool_name: str = ""
) -> str:
    """
    Convenience function: Apply semantic optimization and return optimized output.

    Usage in agent task execution:
        optimized = await apply_semantic_optimization(tool_output, agent_id, tool_name)
    """
    result = await semantic_optimization_hook.process_agent_output(
        output, agent_id, tool_name
    )
    return result.get("optimized_output", output)
