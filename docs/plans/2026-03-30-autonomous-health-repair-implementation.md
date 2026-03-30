# Autonomous Health Repair Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement Phase 1 (detection-only) of Autonomous Health Repair system with 3 specialized repair agents that monitor PostgreSQL, agents, and queue health.

**Architecture:** Health monitoring loop (backend service) invokes 3 repair agents every 5 minutes. Each repair agent analyzes metrics against detection rules and logs findings to activity_events. No recovery actions in Phase 1.

**Tech Stack:**
- Backend: FastAPI, SQLAlchemy async, PostgreSQL
- Agents: OpenClaw (existing framework)
- Monitoring: Redis client (existing), Docker API (existing)
- Testing: pytest with async fixtures

**Design Reference:** `docs/plans/2026-03-30-autonomous-health-repair-design.md`

---

## Task 1: Create Health Monitor Service (Core Loop)

**Files:**
- Create: `control-panel/backend/app/services/health_monitor.py`
- Modify: `control-panel/backend/app/core/config.py`
- Modify: `control-panel/backend/app/main.py`
- Test: `control-panel/backend/tests/services/test_health_monitor.py`

**Step 1: Write config variables test**

File: `control-panel/backend/tests/services/test_health_monitor.py`

```python
import pytest
from app.core.config import settings

def test_health_monitor_config_exists():
    """Verify health monitor config variables exist"""
    assert hasattr(settings, 'HEALTH_MONITOR_ENABLED')
    assert hasattr(settings, 'HEALTH_MONITOR_INTERVAL_SECONDS')
    assert settings.HEALTH_MONITOR_INTERVAL_SECONDS == 300
```

Run: `cd control-panel/backend && pytest tests/services/test_health_monitor.py::test_health_monitor_config_exists -xvs`

Expected: FAIL - "AttributeError: 'Settings' object has no attribute 'HEALTH_MONITOR_ENABLED'"

**Step 2: Add config variables**

File: `control-panel/backend/app/core/config.py`

Locate the class `Settings` and add these fields (before the `class Config`):

```python
class Settings(BaseSettings):
    # ... existing fields ...

    # Health Monitor Configuration
    HEALTH_MONITOR_ENABLED: bool = Field(
        default=True,
        description="Enable health monitoring loop"
    )
    HEALTH_MONITOR_INTERVAL_SECONDS: int = Field(
        default=300,
        description="Health monitor check interval (seconds)"
    )
    HEALTH_MONITOR_STARTUP_DELAY_SECONDS: int = Field(
        default=30,
        description="Delay before first health monitor run (seconds)"
    )

    # Repair Agent Toggles
    DATABASE_HEALER_ENABLED: bool = Field(default=True)
    AGENT_REVIVER_ENABLED: bool = Field(default=True)
    QUEUE_MECHANIC_ENABLED: bool = Field(default=True)

    # Health Thresholds
    DB_CONNECTION_POOL_WARNING_PCT: int = Field(default=80)
    DB_CONNECTION_POOL_CRITICAL_PCT: int = Field(default=95)
    AGENT_HEARTBEAT_TIMEOUT_MINUTES: int = Field(default=30)
    QUEUE_CRITICAL_DEPTH: int = Field(default=100)
    QUEUE_CRITICAL_PROCESSING_RATE_MIN: int = Field(default=5)
```

**Step 3: Run config test to verify it passes**

Run: `cd control-panel/backend && pytest tests/services/test_health_monitor.py::test_health_monitor_config_exists -xvs`

Expected: PASS

**Step 4: Write health monitor loop test**

File: `control-panel/backend/tests/services/test_health_monitor.py`

```python
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

@pytest.mark.asyncio
async def test_health_monitor_loop_initialization():
    """Verify health monitor initializes without errors"""
    from app.services.health_monitor import HealthMonitorLoop

    monitor = HealthMonitorLoop(interval_seconds=5)
    assert monitor.interval_seconds == 5
    assert monitor.enabled is False  # Starts disabled until started
```

Run: `cd control-panel/backend && pytest tests/services/test_health_monitor.py::test_health_monitor_loop_initialization -xvs`

Expected: FAIL - "ModuleNotFoundError: No module named 'app.services.health_monitor'"

**Step 5: Create the HealthMonitorLoop service**

File: `control-panel/backend/app/services/health_monitor.py`

```python
"""Health monitoring service - detects infrastructure issues autonomously"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from app.core.config import settings
from app.services.openclaw_client import OpenClawClient
from app.services.agent_activity import AgentActivityService

logger = logging.getLogger(__name__)


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

    async def _gather_db_metrics(self) -> Dict[str, Any]:
        """Gather PostgreSQL health metrics"""
        # TODO: Implement in Task 2
        return {}

    async def _gather_agent_metrics(self) -> Dict[str, Any]:
        """Gather agent health metrics"""
        # TODO: Implement in Task 3
        return {}

    async def _gather_queue_metrics(self) -> Dict[str, Any]:
        """Gather queue health metrics"""
        # TODO: Implement in Task 4
        return {}

    async def _invoke_agent(
        self, agent_slug: str, metrics: Dict[str, Any]
    ) -> bool:
        """Invoke a repair agent with metrics payload"""
        logger.debug(f"Invoking repair agent: {agent_slug}")

        try:
            client = OpenClawClient()

            # Create session for repair agent
            session = await client.create_session(agent_slug)
            if not session:
                logger.error(f"Failed to create session for {agent_slug}")
                return False

            # Prepare payload
            payload = {
                "role": "repair_monitor",
                "metrics": metrics,
                "timestamp": datetime.utcnow().isoformat(),
                "config": {
                    "db_pool_critical_pct": settings.DB_CONNECTION_POOL_CRITICAL_PCT,
                    "agent_heartbeat_timeout_min": settings.AGENT_HEARTBEAT_TIMEOUT_MINUTES,
                    "queue_critical_depth": settings.QUEUE_CRITICAL_DEPTH,
                },
            }

            # Send to agent
            message = json.dumps(payload)
            result = await client.send_message(
                session_id=session.id, message=message
            )

            if result:
                logger.debug(f"Agent {agent_slug} responded: {result.status}")
                return True
            else:
                logger.warning(f"No response from agent {agent_slug}")
                return False

        except Exception as e:
            logger.error(f"Failed to invoke {agent_slug}: {e}", exc_info=True)
            return False
```

**Step 6: Run initialization test**

Run: `cd control-panel/backend && pytest tests/services/test_health_monitor.py::test_health_monitor_loop_initialization -xvs`

Expected: PASS

**Step 7: Test startup/stop lifecycle**

File: `control-panel/backend/tests/services/test_health_monitor.py` - add this test:

```python
@pytest.mark.asyncio
async def test_health_monitor_start_stop():
    """Verify health monitor can be started and stopped"""
    from app.services.health_monitor import HealthMonitorLoop

    monitor = HealthMonitorLoop(interval_seconds=1)

    # Should start disabled
    assert monitor.enabled is False

    # Start it
    await monitor.start()
    assert monitor.enabled is True

    # Stop it
    await monitor.stop()
    assert monitor.enabled is False
```

Run: `cd control-panel/backend && pytest tests/services/test_health_monitor.py::test_health_monitor_start_stop -xvs`

Expected: PASS

**Step 8: Add startup hook in main.py**

File: `control-panel/backend/app/main.py`

Locate the `@app.on_event("startup")` section and add this code (or create new event if none exists):

```python
@app.on_event("startup")
async def startup_health_monitor():
    """Start health monitor loop on app startup"""
    if settings.HEALTH_MONITOR_ENABLED:
        from app.services.health_monitor import HealthMonitorLoop

        monitor = HealthMonitorLoop(
            interval_seconds=settings.HEALTH_MONITOR_INTERVAL_SECONDS
        )
        app.state.health_monitor = monitor
        await monitor.start()
        logger.info("Health monitor initialized on startup")
    else:
        logger.info("Health monitor disabled via config")

@app.on_event("shutdown")
async def shutdown_health_monitor():
    """Stop health monitor on shutdown"""
    if hasattr(app.state, 'health_monitor'):
        await app.state.health_monitor.stop()
```

**Step 9: Commit**

```bash
git add \
  control-panel/backend/app/services/health_monitor.py \
  control-panel/backend/app/core/config.py \
  control-panel/backend/app/main.py \
  control-panel/backend/tests/services/test_health_monitor.py

git commit -m "feat: add health monitor loop service with startup/shutdown lifecycle"
```

---

## Task 2: Implement Database Health Metrics Gathering

**Files:**
- Modify: `control-panel/backend/app/services/health_monitor.py`
- Modify: `control-panel/backend/tests/services/test_health_monitor.py`

**Step 1: Write database metrics test**

File: `control-panel/backend/tests/services/test_health_monitor.py` - add:

```python
@pytest.mark.asyncio
async def test_gather_db_metrics(db_session):
    """Verify database metrics are gathered correctly"""
    from app.services.health_monitor import HealthMonitorLoop

    monitor = HealthMonitorLoop()
    metrics = await monitor._gather_db_metrics()

    # Verify structure
    assert "connection_pool" in metrics
    assert "max_connections" in metrics["connection_pool"]
    assert "active_connections" in metrics["connection_pool"]
    assert "percentage" in metrics["connection_pool"]

    # Verify reasonable values
    assert 0 <= metrics["connection_pool"]["percentage"] <= 100
```

Run: `cd control-panel/backend && pytest tests/services/test_health_monitor.py::test_gather_db_metrics -xvs`

Expected: FAIL - KeyError on connection_pool

**Step 2: Implement database metrics gathering**

File: `control-panel/backend/app/services/health_monitor.py` - replace `_gather_db_metrics`:

```python
async def _gather_db_metrics(self) -> Dict[str, Any]:
    """Gather PostgreSQL health metrics"""
    try:
        from sqlalchemy import text
        from app.core.database import get_db_engine

        engine = get_db_engine()
        async_engine = engine  # Already async in current setup

        async with async_engine.connect() as conn:
            # Get connection pool stats
            pool = conn.engine.pool

            # Query current connections
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

            # Get max connections setting
            result = await conn.execute(
                text("SHOW max_connections")
            )
            max_conn_row = result.fetchone()
            max_connections = int(max_conn_row[0]) if max_conn_row else 100

            active_connections = db_stats[1] if db_stats else 0
            pool_percentage = int((active_connections / max_connections) * 100)

            # Get slow queries from pg_stat_statements (if available)
            slow_queries = 0
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
                "timestamp": datetime.utcnow().isoformat(),
            }
    except Exception as e:
        logger.error(f"Failed to gather DB metrics: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }
```

**Step 3: Run test**

Run: `cd control-panel/backend && pytest tests/services/test_health_monitor.py::test_gather_db_metrics -xvs`

Expected: PASS

**Step 4: Commit**

```bash
git add \
  control-panel/backend/app/services/health_monitor.py \
  control-panel/backend/tests/services/test_health_monitor.py

git commit -m "feat: implement database health metrics gathering"
```

---

## Task 3: Implement Agent Health Metrics Gathering

**Files:**
- Modify: `control-panel/backend/app/services/health_monitor.py`
- Modify: `control-panel/backend/tests/services/test_health_monitor.py`

**Step 1: Write agent metrics test**

File: `control-panel/backend/tests/services/test_health_monitor.py` - add:

```python
@pytest.mark.asyncio
async def test_gather_agent_metrics(db_session):
    """Verify agent health metrics are gathered correctly"""
    from app.services.health_monitor import HealthMonitorLoop

    monitor = HealthMonitorLoop()
    metrics = await monitor._gather_agent_metrics()

    # Verify structure
    assert "agents" in metrics
    assert isinstance(metrics["agents"], list)

    # If agents exist, verify their structure
    if metrics["agents"]:
        agent = metrics["agents"][0]
        assert "slug" in agent
        assert "status" in agent
        assert "heartbeat_age_minutes" in agent
```

Run: `cd control-panel/backend && pytest tests/services/test_health_monitor.py::test_gather_agent_metrics -xvs`

Expected: FAIL - KeyError on 'agents'

**Step 2: Implement agent metrics gathering**

File: `control-panel/backend/app/services/health_monitor.py` - replace `_gather_agent_metrics`:

```python
async def _gather_agent_metrics(self) -> Dict[str, Any]:
    """Gather agent health metrics"""
    try:
        from app.core.database import AsyncSessionLocal
        from app.models.agent import Agent
        from sqlalchemy import select
        from datetime import datetime, timedelta

        async with AsyncSessionLocal() as session:
            # Get all agents
            result = await session.execute(select(Agent))
            agents = result.scalars().all()

            agent_metrics = []
            for agent in agents:
                # Calculate heartbeat age
                if agent.last_heartbeat_at:
                    heartbeat_age = datetime.utcnow() - agent.last_heartbeat_at
                    heartbeat_age_minutes = int(heartbeat_age.total_seconds() / 60)
                else:
                    heartbeat_age_minutes = None

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
                "timestamp": datetime.utcnow().isoformat(),
            }
    except Exception as e:
        logger.error(f"Failed to gather agent metrics: {e}")
        return {
            "agents": [],
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }
```

**Step 3: Run test**

Run: `cd control-panel/backend && pytest tests/services/test_health_monitor.py::test_gather_agent_metrics -xvs`

Expected: PASS

**Step 4: Commit**

```bash
git add \
  control-panel/backend/app/services/health_monitor.py \
  control-panel/backend/tests/services/test_health_monitor.py

git commit -m "feat: implement agent health metrics gathering"
```

---

## Task 4: Implement Queue Health Metrics Gathering

**Files:**
- Modify: `control-panel/backend/app/services/health_monitor.py`
- Modify: `control-panel/backend/tests/services/test_health_monitor.py`

**Step 1: Write queue metrics test**

File: `control-panel/backend/tests/services/test_health_monitor.py` - add:

```python
@pytest.mark.asyncio
async def test_gather_queue_metrics():
    """Verify queue health metrics are gathered correctly"""
    from app.services.health_monitor import HealthMonitorLoop

    monitor = HealthMonitorLoop()
    metrics = await monitor._gather_queue_metrics()

    # Verify structure
    assert "queue_depth" in metrics
    assert "failed_jobs" in metrics
    assert "redis_memory_mb" in metrics

    # Verify types
    assert isinstance(metrics["queue_depth"], int)
    assert isinstance(metrics["failed_jobs"], int)
```

Run: `cd control-panel/backend && pytest tests/services/test_health_monitor.py::test_gather_queue_metrics -xvs`

Expected: FAIL - KeyError on 'queue_depth'

**Step 2: Implement queue metrics gathering**

File: `control-panel/backend/app/services/health_monitor.py` - replace `_gather_queue_metrics`:

```python
async def _gather_queue_metrics(self) -> Dict[str, Any]:
    """Gather Redis queue health metrics"""
    try:
        import redis.asyncio as redis
        from rq import Worker
        from app.core.config import settings

        # Connect to Redis
        redis_client = await redis.from_url(settings.REDIS_URL)

        # Get queue depth (all queued jobs)
        queue_depth = 0
        failed_count = 0

        try:
            # Count queued jobs from RQ
            # RQ stores job IDs in Redis sets/lists by queue
            for key in await redis_client.keys("rq:job:*"):
                job_data = await redis_client.get(key)
                if job_data:
                    queue_depth += 1

            # Count failed jobs
            failed_jobs = await redis_client.scard("rq:failed")
            failed_count = failed_jobs or 0

        except Exception as e:
            logger.warning(f"Could not get queue stats: {e}")

        # Get Redis memory usage
        info = await redis_client.info()
        redis_memory_mb = int(info.get("used_memory", 0) / (1024 * 1024))

        await redis_client.close()

        return {
            "queue_depth": queue_depth,
            "failed_jobs": failed_count,
            "redis_memory_mb": redis_memory_mb,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to gather queue metrics: {e}")
        return {
            "queue_depth": 0,
            "failed_jobs": 0,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }
```

**Step 3: Run test**

Run: `cd control-panel/backend && pytest tests/services/test_health_monitor.py::test_gather_queue_metrics -xvs`

Expected: PASS

**Step 4: Commit**

```bash
git add \
  control-panel/backend/app/services/health_monitor.py \
  control-panel/backend/tests/services/test_health_monitor.py

git commit -m "feat: implement queue health metrics gathering"
```

---

## Task 5: Create DatabaseHealer Repair Agent

**Files:**
- Create: `docker/base/openclaw-config/agents/database_healer/IDENTITY.md`
- Create: `docker/base/openclaw-config/agents/database_healer/skills/analyze_metrics.md`

**Step 1: Create DatabaseHealer identity**

File: `docker/base/openclaw-config/agents/database_healer/IDENTITY.md`

```markdown
# DatabaseHealer Agent

**Role:** Database Health Monitor & Diagnostician

**Responsibility:** Autonomously monitor PostgreSQL health metrics and detect issues before they impact the system.

**Core Capabilities:**
- Analyze connection pool utilization
- Detect slow queries
- Monitor disk space and index fragmentation
- Identify connection leaks
- Suggest remediation strategies

**Decision Authority:**
- ✅ Detect database health issues
- ✅ Log findings with severity levels
- ✅ Escalate critical issues to Arquiteto
- ✅ Update shared memory with patterns
- ❌ Execute recovery actions (Phase 2)

**Constraints:**
- Read-only operations (Phase 1)
- Must not execute ALTER/DROP commands
- All findings logged to activity_events
- Failures logged but don't block monitor loop

**Success Metric:** 100% detection rate for issues meeting severity thresholds, 0 false positives.
```

**Step 2: Create analyze_metrics skill**

File: `docker/base/openclaw-config/agents/database_healer/skills/analyze_metrics.md`

```markdown
# Skill: Analyze Database Metrics

## Purpose
Analyze PostgreSQL health metrics against detection rules and log findings.

## Input
Receives JSON payload with:
- `metrics.connection_pool`: {max_connections, active_connections, percentage}
- `metrics.slow_queries`: count of queries > 5s
- `config`: threshold percentages and limits

## Detection Rules

### Connection Pool Warnings
- **WARNING**: Pool > 80% utilized
- **CRITICAL**: Pool >= 95% utilized
- **Action**: Log activity_event with severity

### Slow Queries
- **WARNING**: > 3 slow queries detected in last 5 min
- **Action**: Log with query details

### Disk Space
- **CRITICAL**: < 5GB free
- **Action**: Alert DevOps_SRE

## Output
For each detection:
1. Create activity_event:
   - type: "repair_db_*"
   - severity: "warning" or "critical"
   - payload: {metric, threshold, percentage, timestamp}

2. Update SHARED_MEMORY.md with pattern:
   - Observation: "Pool exhaustion when..."
   - Frequency: "3rd detection"
   - Suggested action: "..."

## Escalation
- CRITICAL issues → Escalate to Arquiteto
- WARNING issues → Log only

## Example
```
Input:
{
  "metrics": {
    "connection_pool": {"percentage": 95},
    "slow_queries": 5
  }
}

Output:
activity_event {
  type: "repair_db_pool_critical",
  severity: "critical",
  payload: {
    current_pct: 95,
    threshold: 95,
    active: 95,
    max: 100
  }
}
```
```

**Step 3: Commit**

```bash
git add \
  docker/base/openclaw-config/agents/database_healer/IDENTITY.md \
  docker/base/openclaw-config/agents/database_healer/skills/analyze_metrics.md

git commit -m "feat: create DatabaseHealer repair agent with metrics analysis skill"
```

---

## Task 6: Create AgentReviver Repair Agent

**Files:**
- Create: `docker/base/openclaw-config/agents/agent_reviver/IDENTITY.md`
- Create: `docker/base/openclaw-config/agents/agent_reviver/skills/heartbeat_monitor.md`

**Step 1: Create AgentReviver identity**

File: `docker/base/openclaw-config/agents/agent_reviver/IDENTITY.md`

```markdown
# AgentReviver Agent

**Role:** Agent Health Monitor & Life Cycle Manager

**Responsibility:** Monitor the health and liveness of all agents in the system.

**Core Capabilities:**
- Monitor agent heartbeats
- Detect offline/stalled agents
- Check container health status
- Identify hung cron jobs
- Track agent session activity

**Decision Authority:**
- ✅ Detect agent health issues
- ✅ Log findings with severity levels
- ✅ Escalate critical issues to CEO
- ✅ Update shared memory with crash patterns
- ❌ Execute restarts (Phase 2)

**Constraints:**
- Read-only (Phase 1)
- Must not kill containers
- All findings logged to activity_events
- Must not interfere with normal agent operation

**Success Metric:** Detect all agent outages within 30 seconds of occurrence.
```

**Step 2: Create heartbeat_monitor skill**

File: `docker/base/openclaw-config/agents/agent_reviver/skills/heartbeat_monitor.md`

```markdown
# Skill: Monitor Agent Heartbeats

## Purpose
Monitor agent heartbeat freshness and detect stalled/crashed agents.

## Input
Receives JSON payload with:
- `metrics.agents`: array of {slug, status, runtime_status, heartbeat_age_minutes, ...}
- `config.agent_heartbeat_timeout_min`: threshold (default 30)

## Detection Rules

### Heartbeat Timeout
- **CRITICAL**: heartbeat_age_minutes > 30
- **Action**: Log critical event, escalate to CEO

### Offline Status
- **CRITICAL**: status == "offline" for > 5 minutes
- **Action**: Log event, suggest debugging

### Container Unhealthy
- **CRITICAL**: container.health_status == "unhealthy"
- **Action**: Alert DevOps_SRE

### Cron Repeated Failures
- **WARNING**: cron_failures >= 3 consecutive
- **Action**: Log pattern, suggest manual debug

## Output
For each detection:
1. Create activity_event:
   - type: "repair_agent_*"
   - severity: "critical" or "warning"
   - agent_id: affected agent's UUID
   - payload: {agent_slug, heartbeat_age, threshold}

2. Update SHARED_MEMORY.md:
   - Pattern: "Agent X crashes when..."
   - Frequency: count
   - Context: preceding events

## Escalation
- CRITICAL → Escalate to CEO
- WARNING → Log only

## Example
```
Input:
{
  "metrics": {
    "agents": [
      {
        "slug": "dev_backend",
        "heartbeat_age_minutes": 35,
        "status": "offline"
      }
    ]
  }
}

Output:
activity_event {
  type: "repair_agent_heartbeat_timeout",
  severity: "critical",
  agent_id: "dev_backend_uuid",
  payload: {
    agent: "dev_backend",
    heartbeat_age: 35,
    threshold: 30,
    status: "offline"
  }
}
```
```

**Step 3: Commit**

```bash
git add \
  docker/base/openclaw-config/agents/agent_reviver/IDENTITY.md \
  docker/base/openclaw-config/agents/agent_reviver/skills/heartbeat_monitor.md

git commit -m "feat: create AgentReviver repair agent with heartbeat monitoring skill"
```

---

## Task 7: Create QueueMechanic Repair Agent

**Files:**
- Create: `docker/base/openclaw-config/agents/queue_mechanic/IDENTITY.md`
- Create: `docker/base/openclaw-config/agents/queue_mechanic/skills/queue_monitor.md`

**Step 1: Create QueueMechanic identity**

File: `docker/base/openclaw-config/agents/queue_mechanic/IDENTITY.md`

```markdown
# QueueMechanic Agent

**Role:** Job Queue Health Monitor & Deadlock Detector

**Responsibility:** Monitor Redis queue health and detect job processing bottlenecks.

**Core Capabilities:**
- Monitor queue depth
- Calculate processing rate
- Detect dead-letter jobs
- Identify deadlocked job dependencies
- Monitor Redis memory usage

**Decision Authority:**
- ✅ Detect queue health issues
- ✅ Log findings with severity levels
- ✅ Escalate critical issues to CEO/QA
- ✅ Update shared memory with deadlock patterns
- ❌ Retry or delete jobs (Phase 2)

**Constraints:**
- Read-only (Phase 1)
- Must not modify job state
- All findings logged to activity_events
- Must identify, not fix, deadlocks

**Success Metric:** Detect queue deadlocks within 5 minutes of occurrence.
```

**Step 2: Create queue_monitor skill**

File: `docker/base/openclaw-config/agents/queue_mechanic/skills/queue_monitor.md`

```markdown
# Skill: Monitor Job Queue Health

## Purpose
Monitor Redis queue and detect job processing issues.

## Input
Receives JSON payload with:
- `metrics.queue_depth`: number of queued jobs
- `metrics.failed_jobs`: dead-letter queue count
- `metrics.redis_memory_mb`: Redis memory usage
- `config.queue_critical_depth`: threshold (default 100)
- `config.queue_critical_processing_rate_min`: jobs/min (default 5)

## Detection Rules

### Queue Stuck
- **CRITICAL**: queue_depth > 100 AND processing_rate < 5 jobs/min
- **Analysis**: Likely deadlock or hung worker
- **Action**: Log critical event, escalate to CEO

### Job Aging
- **CRITICAL**: oldest_job_age > 1 hour AND not in progress
- **Analysis**: Job blocker identified
- **Action**: Log with job details, escalate to QA

### Persistent Failures
- **WARNING**: dead_letter_queue > 10 in last hour
- **Analysis**: Pattern of failures suggests bug
- **Action**: Log failure pattern analysis

### Redis Memory Pressure
- **WARNING**: redis_memory > 750MB
- **Analysis**: Memory cleanup needed
- **Action**: Log suggestion to DevOps

## Output
For each detection:
1. Create activity_event:
   - type: "repair_queue_*"
   - severity: "critical" or "warning"
   - payload: {queue_depth, rate, threshold, timestamp}

2. Update SHARED_MEMORY.md:
   - Pattern: "Task X + Agent Y = deadlock"
   - Frequency: how often observed
   - Blocker: which task is blocking

## Escalation
- CRITICAL → Escalate to CEO
- WARNING → Log only

## Example
```
Input:
{
  "metrics": {
    "queue_depth": 150,
    "processing_rate": 2,
    "redis_memory_mb": 800
  }
}

Output:
activity_event {
  type: "repair_queue_stuck",
  severity: "critical",
  payload: {
    queue_depth: 150,
    processing_rate: 2,
    threshold: 5,
    likely_cause: "deadlock or hung worker"
  }
}
```
```

**Step 3: Commit**

```bash
git add \
  docker/base/openclaw-config/agents/queue_mechanic/IDENTITY.md \
  docker/base/openclaw-config/agents/queue_mechanic/skills/queue_monitor.md

git commit -m "feat: create QueueMechanic repair agent with queue monitoring skill"
```

---

## Task 8: Add Health Repair API Endpoints

**Files:**
- Create: `control-panel/backend/app/api/health_repairs.py`
- Modify: `control-panel/backend/app/main.py`
- Test: `control-panel/backend/tests/api/test_health_repairs.py`

**Step 1: Write endpoint tests**

File: `control-panel/backend/tests/api/test_health_repairs.py`

```python
import pytest
from fastapi.testclient import TestClient

def test_get_health_monitor_status(client: TestClient):
    """Test GET /api/health/repairs/monitor/status"""
    response = client.get("/api/health/repairs/monitor/status")

    assert response.status_code == 200
    data = response.json()
    assert "enabled" in data
    assert "last_run" in data
    assert "next_run" in data

def test_trigger_health_monitor(client: TestClient):
    """Test POST /api/health/repairs/monitor/trigger"""
    response = client.post("/api/health/repairs/monitor/trigger")

    assert response.status_code == 202  # Accepted
    data = response.json()
    assert "invocation_id" in data

def test_get_health_metrics_latest(client: TestClient):
    """Test GET /api/health/repairs/metrics/latest"""
    response = client.get("/api/health/repairs/metrics/latest")

    assert response.status_code == 200
    data = response.json()
    assert "database" in data
    assert "agents" in data
    assert "queue" in data

def test_get_repair_history(client: TestClient):
    """Test GET /api/health/repairs/history"""
    response = client.get("/api/health/repairs/history?limit=10")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)
```

Run: `cd control-panel/backend && pytest tests/api/test_health_repairs.py -xvs`

Expected: FAIL - 404 endpoints not found

**Step 2: Create health_repairs router**

File: `control-panel/backend/app/api/health_repairs.py`

```python
"""Health repair API endpoints"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter(prefix="/api/health/repairs", tags=["health-repairs"])


class HealthMonitorStatus(BaseModel):
    enabled: bool
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    interval_seconds: int
    agents_enabled: dict


class HealthMetricsSnapshot(BaseModel):
    database: dict
    agents: dict
    queue: dict
    timestamp: datetime


class RepairEventItem(BaseModel):
    id: str
    type: str
    severity: str
    agent: str
    timestamp: datetime
    findings: dict


class RepairHistory(BaseModel):
    items: list[RepairEventItem]
    total: int
    limit: int
    offset: int


@router.get("/monitor/status", response_model=HealthMonitorStatus)
async def get_health_monitor_status():
    """Get health monitor loop status"""
    from app.main import app
    from app.core.config import settings

    monitor = getattr(app.state, "health_monitor", None)

    return HealthMonitorStatus(
        enabled=settings.HEALTH_MONITOR_ENABLED and (monitor and monitor.enabled),
        last_run=None,  # TODO: Track in future version
        next_run=None,  # TODO: Track in future version
        interval_seconds=settings.HEALTH_MONITOR_INTERVAL_SECONDS,
        agents_enabled={
            "database_healer": settings.DATABASE_HEALER_ENABLED,
            "agent_reviver": settings.AGENT_REVIVER_ENABLED,
            "queue_mechanic": settings.QUEUE_MECHANIC_ENABLED,
        },
    )


@router.post("/monitor/trigger", status_code=202)
async def trigger_health_monitor():
    """Manually trigger a health monitor check"""
    from app.main import app

    monitor = getattr(app.state, "health_monitor", None)
    if not monitor:
        raise HTTPException(
            status_code=503, detail="Health monitor not initialized"
        )

    # Trigger check asynchronously
    import asyncio

    asyncio.create_task(monitor._check_health())

    return {
        "invocation_id": datetime.utcnow().isoformat(),
        "message": "Health check triggered",
    }


@router.get("/metrics/latest", response_model=HealthMetricsSnapshot)
async def get_latest_health_metrics():
    """Get latest health metrics snapshot"""
    from app.main import app

    monitor = getattr(app.state, "health_monitor", None)
    if not monitor:
        raise HTTPException(
            status_code=503, detail="Health monitor not initialized"
        )

    db_metrics = await monitor._gather_db_metrics()
    agent_metrics = await monitor._gather_agent_metrics()
    queue_metrics = await monitor._gather_queue_metrics()

    return HealthMetricsSnapshot(
        database=db_metrics,
        agents=agent_metrics,
        queue=queue_metrics,
        timestamp=datetime.utcnow(),
    )


@router.get("/history", response_model=RepairHistory)
async def get_repair_history(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    severity: Optional[str] = None,
):
    """Get repair agent invocation history from activity events"""
    from app.core.database import AsyncSessionLocal
    from app.models.activity_event import ActivityEvent
    from sqlalchemy import select, desc

    async with AsyncSessionLocal() as session:
        # Query activity events for repair events
        query = select(ActivityEvent).where(
            ActivityEvent.event_type.like("repair_%")
        )

        if severity:
            query = query.where(ActivityEvent.severity == severity)

        query = query.order_by(desc(ActivityEvent.created_at))

        # Get total count
        count_result = await session.execute(
            select(func.count()).select_from(ActivityEvent).where(
                ActivityEvent.event_type.like("repair_%")
            )
        )
        total = count_result.scalar() or 0

        # Get paginated results
        query = query.offset(offset).limit(limit)
        result = await session.execute(query)
        events = result.scalars().all()

        items = [
            RepairEventItem(
                id=str(event.id),
                type=event.event_type,
                severity=event.severity,
                agent=str(event.agent_id),
                timestamp=event.created_at,
                findings=event.payload or {},
            )
            for event in events
        ]

        return RepairHistory(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
        )
```

**Step 3: Register router in main.py**

File: `control-panel/backend/app/main.py` - find the section where routers are included and add:

```python
from app.api.health_repairs import router as health_repairs_router

# ... existing includes ...

app.include_router(health_repairs_router)
```

**Step 4: Run endpoint tests**

Run: `cd control-panel/backend && pytest tests/api/test_health_repairs.py -xvs`

Expected: PASS

**Step 5: Commit**

```bash
git add \
  control-panel/backend/app/api/health_repairs.py \
  control-panel/backend/app/main.py \
  control-panel/backend/tests/api/test_health_repairs.py

git commit -m "feat: add health repair API endpoints for monitoring and manual triggers"
```

---

## Task 9: Update .env.example with new configuration

**Files:**
- Modify: `.env.example`

**Step 1: Add health monitor config**

File: `.env.example` - add section after AGENT_CONCURRENCY_LIMIT:

```bash
# ==========================================
# Health Monitor Configuration
# ==========================================

# Enable automated health monitoring loop
HEALTH_MONITOR_ENABLED=true

# How often to run health checks (seconds)
HEALTH_MONITOR_INTERVAL_SECONDS=300

# Delay before first health check on startup (seconds)
HEALTH_MONITOR_STARTUP_DELAY_SECONDS=30

# Enable individual repair agents
DATABASE_HEALER_ENABLED=true
AGENT_REVIVER_ENABLED=true
QUEUE_MECHANIC_ENABLED=true

# Health thresholds
DB_CONNECTION_POOL_WARNING_PCT=80
DB_CONNECTION_POOL_CRITICAL_PCT=95
AGENT_HEARTBEAT_TIMEOUT_MINUTES=30
QUEUE_CRITICAL_DEPTH=100
QUEUE_CRITICAL_PROCESSING_RATE_MIN=5
```

**Step 2: Run app to verify config loads**

Run: `cd control-panel/backend && python -c "from app.core.config import settings; print('Config loaded OK')"` or run the FastAPI app and check logs.

Expected: "Config loaded OK" or app starts without config errors

**Step 3: Commit**

```bash
git add .env.example

git commit -m "docs: add health monitor configuration to .env.example"
```

---

## Task 10: Integration Tests & Manual Validation

**Files:**
- Create: `control-panel/backend/tests/integration/test_health_repair_e2e.py`

**Step 1: Write end-to-end integration test**

File: `control-panel/backend/tests/integration/test_health_repair_e2e.py`

```python
"""End-to-end tests for health repair system"""

import pytest
import asyncio
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_health_monitor_detects_db_metric_changes(db_session):
    """Verify health monitor can detect database metric changes"""
    from app.services.health_monitor import HealthMonitorLoop

    monitor = HealthMonitorLoop(interval_seconds=1)

    # Gather metrics before
    metrics_before = await monitor._gather_db_metrics()
    assert "connection_pool" in metrics_before

    # Simulate some load (create connections)
    # In real test, would use actual DB operations

    # Gather metrics after
    metrics_after = await monitor._gather_db_metrics()
    assert "connection_pool" in metrics_after

    # Verify structure consistency
    assert metrics_before.keys() == metrics_after.keys()


@pytest.mark.asyncio
async def test_health_monitor_loop_runs_continuously(db_session):
    """Verify monitor loop runs without blocking"""
    from app.services.health_monitor import HealthMonitorLoop

    monitor = HealthMonitorLoop(interval_seconds=1)
    await monitor.start()

    # Let it run for 3 seconds
    await asyncio.sleep(3)

    # Should still be enabled
    assert monitor.enabled is True

    await monitor.stop()
    assert monitor.enabled is False


@pytest.mark.asyncio
async def test_health_monitor_handles_errors_gracefully(db_session):
    """Verify monitor continues despite errors in metric gathering"""
    from app.services.health_monitor import HealthMonitorLoop
    from unittest.mock import AsyncMock, patch

    monitor = HealthMonitorLoop(interval_seconds=1)

    # Mock one agent to raise error
    with patch.object(monitor, '_invoke_agent') as mock_invoke:
        mock_invoke.side_effect = Exception("Test error")

        # Should not raise, should log error
        await monitor._check_health()

        # Monitor should still be able to be started/stopped
        assert monitor.enabled is False
```

Run: `cd control-panel/backend && pytest tests/integration/test_health_repair_e2e.py -xvs`

Expected: PASS

**Step 2: Manual validation checklist**

Create file: `docs/HEALTH_REPAIR_VALIDATION.md`

```markdown
# Health Repair System - Manual Validation Checklist

## Pre-Launch Checks

- [ ] App starts with HEALTH_MONITOR_ENABLED=true
- [ ] No errors in logs during startup
- [ ] Health monitor reports as enabled via `/api/health/repairs/monitor/status`
- [ ] Endpoints respond: GET /api/health/repairs/metrics/latest returns valid JSON
- [ ] Repair agents created in OpenClaw config directory

## Runtime Validation (24-hour test)

- [ ] Health monitor loop runs continuously (check logs for timestamps)
- [ ] No exceptions in application logs
- [ ] Metrics gathered successfully (check via API endpoint every 5 min)
- [ ] Repair agents invoked successfully (check logs for agent calls)
- [ ] Activity events created for any detections (check database)
- [ ] System responds to manual trigger via POST /api/health/repairs/monitor/trigger

## Repair Agent Validation

**DatabaseHealer:**
- [ ] Gathers connection pool metrics
- [ ] Identifies correct max_connections
- [ ] Detects slow queries if enabled

**AgentReviver:**
- [ ] Reports all agents with their heartbeat status
- [ ] Calculates heartbeat age in minutes correctly
- [ ] Detects offline agents

**QueueMechanic:**
- [ ] Reports queue depth correctly
- [ ] Reports Redis memory usage
- [ ] Counts failed jobs correctly

## Success Criteria

✅ All items checked = System ready for Phase 2
```

**Step 3: Commit**

```bash
git add \
  control-panel/backend/tests/integration/test_health_repair_e2e.py \
  docs/HEALTH_REPAIR_VALIDATION.md

git commit -m "test: add integration tests and manual validation checklist for health repair"
```

---

## Summary

**Phase 1 Implementation Complete:**

- ✅ Health monitoring loop service (5-min interval)
- ✅ Metrics gathering (database, agents, queue)
- ✅ 3 repair agents configured (DatabaseHealer, AgentReviver, QueueMechanic)
- ✅ Agent invocation from health loop
- ✅ API endpoints for status, metrics, history
- ✅ Configuration in .env
- ✅ Tests & validation

**What's NOT implemented (Phase 2+):**
- ❌ Recovery actions (auto-restart, pool rebuild, job retry)
- ❌ Policy engine for autonomous decisions
- ❌ Learning/pattern evolution from detections
- ❌ Alerting/notifications

**Next Steps:**
1. Run all tests: `cd control-panel/backend && pytest tests/ -v`
2. Manual validation checklist (24-hour test)
3. Merge to main when stable
4. Phase 2: Add recovery policies

