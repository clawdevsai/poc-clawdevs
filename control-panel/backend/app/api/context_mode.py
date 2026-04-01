"""
Context Mode API Endpoints
==========================

Endpoints for monitoring context-mode compression metrics
and viewing compression statistics.

Accessible at: /api/context-mode/
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from ..hooks.tool_executed import get_compression_metrics

logger = logging.getLogger("openclaw.api.context_mode")

router = APIRouter(prefix="/context-mode", tags=["context-mode"])


@router.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """
    Get context-mode compression metrics.

    Returns:
    {
        "total_executions": 1234,
        "total_compressions": 890,
        "compression_rate": "72.2%",
        "total_original_bytes": 125000000,
        "total_compressed_bytes": 3500000,
        "average_compression_ratio": "2.8%",
        "tokens_saved_estimate": 28750
    }

    This data is used in OpenClaw Control Panel dashboard to visualize:
    - Compression efficiency
    - Tokens saved
    - Cost reduction
    """
    try:
        metrics = get_compression_metrics()

        if not metrics:
            return {
                "status": "no_data",
                "message": "No compression metrics yet (no large tool outputs detected)"
            }

        logger.info("Fetched context-mode metrics", extra=metrics)
        return {
            "status": "success",
            **metrics
        }

    except Exception as e:
        logger.error(f"Error fetching compression metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_summary() -> Dict[str, Any]:
    """
    Get context-mode compression summary for dashboard card.

    Returns human-friendly summary:
    {
        "tokens_saved_per_hour": 12500,
        "estimated_monthly_cost_reduction": "$562",
        "compression_efficiency": "97.2%",
        "status": "active"
    }
    """
    try:
        metrics = get_compression_metrics()

        if not metrics:
            return {
                "status": "initializing",
                "message": "Context-mode compression waiting for large tool outputs"
            }

        # Calculate metrics for display
        tokens_saved = metrics.get("tokens_saved_estimate", 0)

        # Rough estimation: 1 token ≈ 0.15 cents
        monthly_savings = tokens_saved * 30 * 0.0015  # ~0.15 cents per 1K tokens

        compression_efficiency = metrics.get("average_compression_ratio", "N/A")
        if isinstance(compression_efficiency, str) and "%" in compression_efficiency:
            compression_efficiency = compression_efficiency.replace("%", "")
            try:
                compression_efficiency_num = float(compression_efficiency)
                compression_efficiency = f"{(100 - compression_efficiency_num):.1f}%"
            except:
                pass

        return {
            "status": "active",
            "tokens_saved_per_hour": int(tokens_saved / 24) if tokens_saved else 0,
            "estimated_monthly_cost_reduction": f"${monthly_savings:.2f}",
            "compression_efficiency": compression_efficiency,
            "total_compressions": metrics.get("total_compressions", 0),
            "next_hour_estimate": int(tokens_saved / 24) if tokens_saved else 0,
        }

    except Exception as e:
        logger.error(f"Error generating compression summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_status() -> Dict[str, str]:
    """
    Get context-mode compression status.

    Returns:
    {
        "status": "active" | "initializing" | "disabled",
        "message": "Human-friendly status message"
    }
    """
    try:
        metrics = get_compression_metrics()

        if not metrics:
            return {
                "status": "initializing",
                "message": "Context-mode compression active, waiting for large outputs to compress",
                "config_status": "active",
                "hook_status": "tool.executed hook registered"
            }

        return {
            "status": "active",
            "message": f"Context-mode compression active ({metrics.get('total_compressions', 0)} compressions so far)",
            "config_status": "active",
            "hook_status": "tool.executed hook registered",
            "metrics_available": True
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error checking context-mode status: {str(e)}"
        }
