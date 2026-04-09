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
Context Mode Metrics Broadcaster
=================================

Periodically fetches context-mode compression metrics and broadcasts them
to all connected WebSocket clients in the "context-mode-metrics" channel.
"""

import asyncio
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import FastAPI

logger = logging.getLogger("openclaw.services.context_mode_metrics_broadcaster")


class ContextModeMetricsBroadcaster:
    """Broadcasts context-mode metrics updates to WebSocket clients."""

    def __init__(self, interval_seconds: float = 30):
        self.interval_seconds = interval_seconds
        self.running = False
        self._task = None

    async def start(self):
        """Start broadcasting metrics."""
        if self.running:
            logger.warning("Metrics broadcaster already running")
            return

        self.running = True
        self._task = asyncio.create_task(self._broadcast_loop())
        logger.info(
            f"Context-mode metrics broadcaster started (interval={self.interval_seconds}s)"
        )

    async def stop(self):
        """Stop broadcasting metrics."""
        if not self.running:
            return

        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Context-mode metrics broadcaster stopped")

    async def _broadcast_loop(self):
        """Main broadcast loop."""
        from app.api.context_mode import build_monitoring_payload
        from app.api.ws import manager
        from app.core.database import AsyncSessionLocal
        from app.services.context_metrics import (
            compute_overview_metrics,
            DEFAULT_WINDOW_MINUTES,
        )

        while self.running:
            try:
                await asyncio.sleep(self.interval_seconds)

                async with AsyncSessionLocal() as session:
                    payload = await build_monitoring_payload(session)
                    overview = await compute_overview_metrics(
                        session, DEFAULT_WINDOW_MINUTES
                    )
                    payload.update(
                        {
                            "tokens_consumed_total": overview["tokens_consumed_total"],
                            "tokens_consumed_avg_per_task": overview[
                                "tokens_consumed_avg_per_task"
                            ],
                            "backlog_count": overview["backlog_count"],
                            "tasks_in_progress": overview["tasks_in_progress"],
                            "tasks_completed": overview["tasks_completed"],
                        }
                    )
                payload["type"] = "context-mode-metrics"

                await manager.broadcast("context-mode-metrics", payload)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics broadcast loop: {e}", exc_info=True)
