"""Test semantic optimization auto-compression hook."""

import pytest
from unittest.mock import AsyncMock, patch

from app.hooks.semantic_optimization_hook import SemanticOptimizationHook


@pytest.mark.asyncio
class TestSemanticOptimizationHook:
    """Test auto-compression hook for agent output."""

    async def test_process_output_no_features_enabled(self):
        """When all features disabled, should return original output."""
        hook = SemanticOptimizationHook()

        with patch("app.hooks.semantic_optimization_hook.flags") as mock_flags:
            mock_flags.is_enabled.return_value = False

            output = "This is test output with some content"
            result = await hook.process_agent_output(output, "dev_backend", "test_tool")

            assert result["original_output"] == output
            assert result["optimized_output"] == output
            assert result["optimizations_applied"] == []

    async def test_process_output_compression_enabled(self):
        """When compression enabled, should compress output."""
        hook = SemanticOptimizationHook()

        with patch("app.hooks.semantic_optimization_hook.flags") as mock_flags:
            with patch.object(hook, "adaptive_compressor") as mock_compressor:
                mock_flags.is_enabled.return_value = True
                mock_compressor.compress_adaptive = AsyncMock(
                    return_value={"compressed": "Compressed output"}
                )

                output = "Original long output with lots of content"
                result = await hook.process_agent_output(output, "dev_backend", "test_tool")

                assert result["optimized_output"] == "Compressed output"
                assert "adaptive_compression" in result["optimizations_applied"]

    async def test_process_output_with_anomaly(self):
        """When anomaly detected, should skip compression."""
        hook = SemanticOptimizationHook()

        with patch("app.hooks.semantic_optimization_hook.flags") as mock_flags:
            with patch.object(hook, "anomaly_detector") as mock_detector:
                mock_flags.is_enabled.return_value = True
                mock_detector.detect = AsyncMock(return_value={"anomaly_score": 0.9})

                output = "Anomalous output"
                result = await hook.process_agent_output(output, "dev_backend", "tool")

                assert result["optimized_output"] == output
                assert result["optimizations_applied"] == []

    async def test_process_output_tracks_metrics(self):
        """Should track compression metrics."""
        hook = SemanticOptimizationHook()

        with patch("app.hooks.semantic_optimization_hook.flags") as mock_flags:
            with patch("app.hooks.semantic_optimization_hook.context_tracker") as mock_tracker:
                with patch.object(hook, "adaptive_compressor") as mock_compressor:
                    mock_flags.is_enabled.return_value = True
                    mock_compressor.compress_adaptive = AsyncMock(
                        return_value={"compressed": "Short"}
                    )

                    output = "This is a longer output with more words"
                    result = await hook.process_agent_output(output, "dev_backend", "tool")

                    assert "tokens_saved" in result
                    assert "compression_ratio" in result
                    mock_tracker.record.assert_called_once()

    async def test_process_output_error_handling(self):
        """Should handle errors gracefully and return original output."""
        hook = SemanticOptimizationHook()

        with patch("app.hooks.semantic_optimization_hook.flags") as mock_flags:
            with patch.object(hook, "adaptive_compressor") as mock_compressor:
                mock_flags.is_enabled.return_value = True
                mock_compressor.compress_adaptive = AsyncMock(side_effect=Exception("Error"))

                output = "Test output"
                result = await hook.process_agent_output(output, "dev_backend", "tool")

                # Should still return original on error
                assert result["optimized_output"] == output
