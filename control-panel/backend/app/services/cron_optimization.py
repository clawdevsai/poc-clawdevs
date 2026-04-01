"""
Cron Job Output Compression - Phase 4 Task 2
Implementa compress\u00e3o de outputs de cron jobs usando context-mode.

Provides:
- Batch compression handler para cron outputs
- Tag-based invalidation
- Metrics collection
"""

import json
import subprocess
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path


class CronOptimizationService:
    """Service para comprimir outputs de cron jobs com context-mode."""

    def __init__(self):
        """Inicializa Cron Optimization Service."""
        self.compression_history: List[Dict[str, Any]] = []
        self.metrics = {
            "total_cron_executions": 0,
            "total_bytes_processed": 0,
            "total_bytes_compressed": 0,
            "average_compression_ratio": 0.0,
        }

    async def compress_cron_output(
        self,
        job_name: str,
        output: str,
        job_type: str = "cleanup",
    ) -> Dict[str, Any]:
        """Comprimir output de um cron job.

        Args:
            job_name: Nome do cron job (ex: daily_cleanup)
            output: Output do cron job para comprimir
            job_type: Tipo de job (cleanup, report, analytics)

        Returns:
            Dict com resultado da compress\u00e3o:
            {
                'status': 'success' | 'error',
                'job_name': str,
                'original_size_bytes': int,
                'compressed_size_bytes': int,
                'compression_ratio': float,
                'compressed_at': datetime,
                'compressed_output': str
            }
        """
        try:
            original_size = len(output.encode('utf-8'))

            # Call context-mode via subprocess para compress\u00e3o
            proc = subprocess.run(
                ["npx", "context-mode", "execute", "--lang=shell", "--mode=compress"],
                input=output.encode(),
                capture_output=True,
                timeout=3,
                cwd="/control-panel/backend"
            )

            if proc.returncode == 0:
                compressed_output = proc.stdout.decode()
                compressed_size = len(compressed_output.encode('utf-8'))
                ratio = 1.0 - (compressed_size / original_size) if original_size > 0 else 0.0

                # Update metrics
                self.metrics["total_cron_executions"] += 1
                self.metrics["total_bytes_processed"] += original_size
                self.metrics["total_bytes_compressed"] += compressed_size

                # Recalculate average ratio
                if self.metrics["total_bytes_processed"] > 0:
                    self.metrics["average_compression_ratio"] = (
                        1.0 - (
                            self.metrics["total_bytes_compressed"]
                            / self.metrics["total_bytes_processed"]
                        )
                    )

                result = {
                    "status": "success",
                    "job_name": job_name,
                    "job_type": job_type,
                    "original_size_bytes": original_size,
                    "compressed_size_bytes": compressed_size,
                    "compression_ratio": ratio,
                    "compressed_at": datetime.now().isoformat(),
                    "compressed_output": compressed_output,
                }

                self.compression_history.append(result)
                return result
            else:
                error_msg = proc.stderr.decode()
                return {
                    "status": "error",
                    "job_name": job_name,
                    "error": f"ctx_execute failed: {error_msg}",
                    "original_size_bytes": original_size,
                }

        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "job_name": job_name,
                "error": "Timeout durante compress\u00e3o",
                "original_size_bytes": len(output.encode('utf-8')),
            }
        except Exception as e:
            return {
                "status": "error",
                "job_name": job_name,
                "error": str(e),
                "original_size_bytes": len(output.encode('utf-8')),
            }

    async def compress_batch(
        self,
        jobs: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        """Comprimir m\u00faltiplos cron outputs em batch.

        Args:
            jobs: Lista de jobs [{"name": "cleanup", "output": "...", "type": "cleanup"}]

        Returns:
            Dict com resultados agregados
        """
        results = []
        total_original = 0
        total_compressed = 0

        for job in jobs:
            result = await self.compress_cron_output(
                job_name=job.get("name", "unknown"),
                output=job.get("output", ""),
                job_type=job.get("type", "generic"),
            )
            results.append(result)

            if result["status"] == "success":
                total_original += result["original_size_bytes"]
                total_compressed += result["compressed_size_bytes"]

        overall_ratio = (
            1.0 - (total_compressed / total_original) if total_original > 0 else 0.0
        )

        return {
            "status": "success",
            "batch_size": len(jobs),
            "successful_compressions": sum(1 for r in results if r["status"] == "success"),
            "total_original_bytes": total_original,
            "total_compressed_bytes": total_compressed,
            "overall_compression_ratio": overall_ratio,
            "results": results,
            "processed_at": datetime.now().isoformat(),
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get cron compression metrics.

        Returns:
            Dict com m\u00e9tricas de compress\u00e3o
        """
        return {
            "status": "success",
            "total_cron_executions": self.metrics["total_cron_executions"],
            "total_bytes_processed": self.metrics["total_bytes_processed"],
            "total_bytes_compressed": self.metrics["total_bytes_compressed"],
            "average_compression_ratio": self.metrics["average_compression_ratio"],
            "tokens_saved_estimate": (
                self.metrics["total_bytes_compressed"] // 4
            ),  # 4 bytes per token
            "estimated_monthly_savings": self._calculate_monthly_savings(),
        }

    def _calculate_monthly_savings(self) -> float:
        """Calcular economia mensal estimada."""
        # Assume $0.000001 per token saved
        tokens_saved = self.metrics["total_bytes_compressed"] // 4
        # Estimate 30 cron executions per month
        monthly_tokens_saved = tokens_saved * 30
        return monthly_tokens_saved * 0.000001


# Singleton instance
_service: Optional[CronOptimizationService] = None


def get_cron_optimization_service() -> CronOptimizationService:
    """Get or create cron optimization service singleton."""
    global _service
    if _service is None:
        _service = CronOptimizationService()
    return _service
