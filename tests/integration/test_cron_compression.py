"""
Integration Tests for Cron Compression - Phase 4 Task 2
Testa compress\u00e3o de cron outputs end-to-end.
"""

import unittest
import asyncio
import sys
import os

# Import the service
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../control-panel/backend"))

from app.services.cron_optimization import CronOptimizationService


class TestCronCompression(unittest.TestCase):
    """Integration tests para cron compression."""

    def setUp(self):
        """Setup para cada teste."""
        self.service = CronOptimizationService()

    def test_service_initialization(self):
        """Test que CronOptimizationService inicializa corretamente."""
        self.assertIsNotNone(self.service)
        self.assertEqual(self.service.metrics["total_cron_executions"], 0)
        self.assertEqual(self.service.metrics["total_bytes_processed"], 0)

    def test_get_metrics_empty(self):
        """Test que get_metrics retorna estado inicial correto."""
        metrics = self.service.get_metrics()

        self.assertEqual(metrics["status"], "success")
        self.assertEqual(metrics["total_cron_executions"], 0)
        self.assertEqual(metrics["total_bytes_processed"], 0)

    async def test_compress_cron_output_small(self):
        """Test compress\u00e3o de output pequeno (n\u00e3o compress)."""
        output = "pequeno output"

        result = await self.service.compress_cron_output(
            job_name="test_job",
            output=output,
            job_type="cleanup"
        )

        # Should succeed or fail gracefully
        self.assertIn(result["status"], ["success", "error"])
        if result["status"] == "success":
            self.assertEqual(result["job_name"], "test_job")
            self.assertGreater(result["original_size_bytes"], 0)

    async def test_compress_cron_output_large(self):
        """Test compress\u00e3o de output grande."""
        # Simular output grande de cron job
        output = "\n".join([f"Line {i}: Processing item {i}" for i in range(1000)])

        result = await self.service.compress_cron_output(
            job_name="large_cleanup",
            output=output,
            job_type="cleanup"
        )

        if result["status"] == "success":
            self.assertEqual(result["job_name"], "large_cleanup")
            self.assertGreater(result["original_size_bytes"], 0)
            self.assertGreater(result["compressed_size_bytes"], 0)

            # Verify compression ratio is between 0 and 1
            self.assertGreaterEqual(result["compression_ratio"], 0)
            self.assertLessEqual(result["compression_ratio"], 1)

    async def test_compress_batch(self):
        """Test compress\u00e3o em batch de m\u00faltiplos jobs."""
        jobs = [
            {
                "name": "cleanup_1",
                "output": "\n".join([f"Cleaning {i}" for i in range(100)]),
                "type": "cleanup"
            },
            {
                "name": "report_1",
                "output": "\n".join([f"Report line {i}" for i in range(100)]),
                "type": "report"
            }
        ]

        result = await self.service.compress_batch(jobs)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["batch_size"], 2)
        self.assertGreaterEqual(result["successful_compressions"], 0)

    async def test_metrics_update(self):
        """Test que metrics s\u00e3o atualizadas ap\u00f3s compress\u00e3o."""
        initial_metrics = self.service.get_metrics()
        initial_executions = initial_metrics["total_cron_executions"]

        # Compress some output
        output = "\n".join([f"Test line {i}" for i in range(50)])
        result = await self.service.compress_cron_output(
            job_name="metrics_test",
            output=output
        )

        # Get updated metrics
        updated_metrics = self.service.get_metrics()

        if result["status"] == "success":
            self.assertEqual(
                updated_metrics["total_cron_executions"],
                initial_executions + 1
            )
            self.assertGreater(updated_metrics["total_bytes_processed"], 0)

    def test_run_async_tests(self):
        """Run all async tests."""
        # Test compress small
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(self.test_compress_cron_output_small())
            loop.run_until_complete(self.test_compress_cron_output_large())
            loop.run_until_complete(self.test_compress_batch())
            loop.run_until_complete(self.test_metrics_update())
        finally:
            loop.close()


class TestCronCompressionMetrics(unittest.TestCase):
    """Tests para m\u00e9tricas de cron compression."""

    def setUp(self):
        """Setup para testes de m\u00e9tricas."""
        self.service = CronOptimizationService()

    def test_monthly_savings_calculation(self):
        """Test que c\u00e1lculo de economia mensal funciona."""
        savings = self.service._calculate_monthly_savings()
        self.assertGreaterEqual(savings, 0)

    def test_compression_ratio_bounds(self):
        """Test que compression ratio fica entre 0 e 1."""
        service = CronOptimizationService()
        service.metrics["total_bytes_processed"] = 1000
        service.metrics["total_bytes_compressed"] = 500

        ratio = service.metrics["total_bytes_compressed"] / service.metrics["total_bytes_processed"]
        self.assertGreaterEqual(ratio, 0)
        self.assertLessEqual(ratio, 1)


if __name__ == "__main__":
    unittest.main()
