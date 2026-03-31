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

"""Health monitoring service - detects infrastructure issues autonomously"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any

import redis.asyncio as aioredis

from app.core.config import get_settings
from app.services.llm_runtime_client import LlmRuntimeClient as OpenClawClient

logger = logging.getLogger(__name__)
settings = get_settings()


class HealthMonitorLoop:
    """Periodic health check orchestrator that invokes repair agents"""

    def __init__(self, interval_seconds: int = 300):
        self.interval_seconds = interval_seconds
        self.enabled = False
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the health monitor loop"""
        if self.enabled:
            logger.warning("Health monitor already running")
            return

        self.enabled = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info(f"Health monitor started (interval: {self.interval_seconds}s)")

    async def stop(self):
        """Stop the health monitor loop"""
        self.enabled = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Health monitor stopped")

    async def _run_loop(self):
        """Main loop - runs every interval_seconds"""
        try:
            # Initial delay before first run
            await asyncio.sleep(settings.HEALTH_MONITOR_STARTUP_DELAY_SECONDS)

            while self.enabled:
                try:
                    await self._check_health()
                except Exception as e:
                    logger.error(f"Health monitor error: {e}", exc_info=True)

                # Sleep until next interval
                await asyncio.sleep(self.interval_seconds)

        except asyncio.CancelledError:
            logger.info("Health monitor loop cancelled")

    async def _check_health(self):
        """Execute a single health check cycle"""
        logger.debug("Running health check cycle")

        # Gather metrics from infrastructure
        db_metrics = await self._gather_db_metrics()
        agent_metrics = await self._gather_agent_metrics()
        queue_metrics = await self._gather_queue_metrics()

        # Invoke repair agents in parallel
        results = []
        if settings.DATABASE_HEALER_ENABLED:
            results.append(
                asyncio.create_task(
                    self._invoke_agent("database_healer", db_metrics)
                )
            )
        if settings.AGENT_REVIVER_ENABLED:
            results.append(
                asyncio.create_task(
                    self._invoke_agent("agent_reviver", agent_metrics)
                )
            )
        if settings.QUEUE_MECHANIC_ENABLED:
            results.append(
                asyncio.create_task(
                    self._invoke_agent("queue_mechanic", queue_metrics)
                )
            )

        # Wait for all agents to complete
        responses = await asyncio.gather(*results, return_exceptions=True)

        # Log execution
        success_count = sum(
            1 for r in responses if not isinstance(r, Exception) and r
        )
        logger.debug(
            f"Health check complete: {success_count}/{len(results)} agents responded"
        )

    async def _gather_db_metrics(self, engine=None) -> Dict[str, Any]:
        """Gather PostgreSQL health metrics"""
        try:
            from sqlalchemy import text

            if engine is None:
                from app.core.database import engine as default_engine
                engine = default_engine

            async with engine.connect() as conn:
                # Get connection pool stats
                pool = conn.engine.pool

                # Determine database type
                dialect_name = conn.dialect.name

                if dialect_name == "postgresql":
                    # PostgreSQL-specific queries
                    result = await conn.execute(
                        text("""
                            SELECT
                                datname as database,
                                numbackends as active_connections
                            FROM pg_stat_database
                            WHERE datname = current_database()
                        """)
                    )
                    db_stats = result.fetchone()

                    result = await conn.execute(
                        text("SHOW max_connections")
                    )
                    max_conn_row = result.fetchone()
                    max_connections = int(max_conn_row[0]) if max_conn_row else 100

                    active_connections = db_stats[1] if db_stats else 0
                else:
                    # Fallback for SQLite and other databases
                    max_connections = 100
                    active_connections = 1

                pool_percentage = int((active_connections / max_connections) * 100) if max_connections > 0 else 0

                # Get slow queries from pg_stat_statements (if available)
                slow_queries = 0
                if dialect_name == "postgresql":
                    try:
                        result = await conn.execute(
                            text("""
                                SELECT COUNT(*) as slow_count
                                FROM pg_stat_statements
                                WHERE mean_exec_time > 5000  -- 5 seconds
                                LIMIT 1
                            """)
                        )
                        slow_row = result.fetchone()
                        slow_queries = slow_row[0] if slow_row else 0
                    except Exception:
                        # pg_stat_statements extension may not be installed
                        slow_queries = 0

                return {
                    "connection_pool": {
                        "max_connections": max_connections,
                        "active_connections": active_connections,
                        "percentage": pool_percentage,
                    },
                    "slow_queries": slow_queries,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
        except Exception as e:
            logger.error(f"Failed to gather DB metrics: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    async def _gather_agent_metrics(self, session=None) -> Dict[str, Any]:
        """Gather agent health metrics"""
        try:
            from sqlmodel import select
            from app.models import Agent

            if session is None:
                from app.core.database import AsyncSessionLocal
                async with AsyncSessionLocal() as session:
                    return await self._gather_agent_metrics(session=session)

            # Query all agents
            result = await session.exec(select(Agent))
            agents = result.all()

            # Process agent metrics
            agent_metrics = []
            now = datetime.now(timezone.utc)

            for agent in agents:
                # Calculate heartbeat age in minutes
                heartbeat_age_minutes = 0
                if agent.last_heartbeat_at:
                    # Handle both timezone-aware and naive datetimes
                    last_heartbeat = agent.last_heartbeat_at
                    if last_heartbeat.tzinfo is None:
                        last_heartbeat = last_heartbeat.replace(tzinfo=timezone.utc)

                    age_delta = now - last_heartbeat
                    heartbeat_age_minutes = int(age_delta.total_seconds() / 60)

                agent_metrics.append({
                    "slug": agent.slug,
                    "display_name": agent.display_name,
                    "status": agent.status,
                    "runtime_status": agent.runtime_status,
                    "last_heartbeat_at": agent.last_heartbeat_at.isoformat() if agent.last_heartbeat_at else None,
                    "heartbeat_age_minutes": heartbeat_age_minutes,
                    "openclaw_session_id": agent.openclaw_session_id,
                })

            return {
                "agents": agent_metrics,
                "total": len(agents),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to gather agent metrics: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    async def _gather_queue_metrics(self) -> Dict[str, Any]:
        """Gather queue health metrics from Redis/RQ"""
        try:
            # Connect to Redis
            redis_client = aioredis.from_url(settings.redis_url)

            # Get total queue depth (all keys in Redis)
            queue_depth = await redis_client.dbsize()

            # Get memory usage in MB
            info = await redis_client.info()
            redis_memory_bytes = info.get("used_memory", 0)
            redis_memory_mb = redis_memory_bytes // (1024 * 1024) if redis_memory_bytes else 0

            # Count failed jobs in dead-letter queue
            # RQ stores failed jobs with pattern "rq:job:*" and status "failed"
            # For simplicity, we check for keys matching RQ failure patterns
            failed_job_keys = await redis_client.keys("rq:job:*:status:failed")
            failed_jobs = len(failed_job_keys) if failed_job_keys else 0

            # Close the connection
            await redis_client.close()

            return {
                "queue_depth": queue_depth,
                "failed_jobs": failed_jobs,
                "redis_memory_mb": redis_memory_mb,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to gather queue metrics: {e}")
            return {
                "queue_depth": 0,
                "failed_jobs": 0,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    async def _invoke_agent(
        self, agent_slug: str, metrics: Dict[str, Any]
    ) -> bool:
        """Invoke a repair agent with metrics payload"""
        logger.debug(f"Invoking repair agent: {agent_slug}")

        try:
            client = OpenClawClient()

            # Prepare payload
            payload = {
                "role": "repair_monitor",
                "metrics": metrics,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "config": {
                    "db_pool_critical_pct": settings.DB_CONNECTION_POOL_CRITICAL_PCT,
                    "agent_heartbeat_timeout_min": settings.AGENT_HEARTBEAT_TIMEOUT_MINUTES,
                    "queue_critical_depth": settings.QUEUE_CRITICAL_DEPTH,
                },
            }

            # Send to agent using run_agent_turn
            message = json.dumps(payload)
            result = await client.run_agent_turn(
                agent_slug=agent_slug, message=message
            )

            if result:
                logger.debug(f"Agent {agent_slug} responded: {result[:100]}")
                return True
            else:
                logger.warning(f"No response from agent {agent_slug}")
                return False

        except Exception as e:
            logger.error(f"Failed to invoke {agent_slug}: {e}", exc_info=True)
            return False
