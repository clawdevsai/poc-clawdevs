"""Periodic synchronization tasks.

These tasks run on the worker to keep the control panel in sync with OpenClaw runtime.
"""

import logging
from datetime import datetime, timedelta
from redis import Redis
from rq import Queue
from rq_scheduler import Scheduler

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.services.agent_sync import sync_agents_runtime
from app.services.session_sync import sync_sessions
from app.services.task_sync import sync_tasks

logger = logging.getLogger(__name__)
settings = get_settings()


async def run_sync_agents():
    """Sync agent status from OpenClaw runtime."""
    logger.info("[periodic_sync] Starting agent sync")
    try:
        async with SessionLocal() as session:
            await sync_agents_runtime(session)
            logger.info("[periodic_sync] Agent sync completed")
    except Exception as e:
        logger.error(f"[periodic_sync] Agent sync failed: {e}")
        raise


async def run_sync_sessions():
    """Sync sessions from OpenClaw runtime."""
    logger.info("[periodic_sync] Starting session sync")
    try:
        async with SessionLocal() as session:
            await sync_sessions(session)
            logger.info("[periodic_sync] Session sync completed")
    except Exception as e:
        logger.error(f"[periodic_sync] Session sync failed: {e}")
        raise


async def run_sync_tasks():
    """Sync tasks from GitHub issues."""
    logger.info("[periodic_sync] Starting task sync")
    try:
        async with SessionLocal() as session:
            await sync_tasks(session)
            logger.info("[periodic_sync] Task sync completed")
    except Exception as e:
        logger.error(f"[periodic_sync] Task sync failed: {e}")
        raise


def schedule_periodic_tasks():
    """Schedule periodic sync tasks in RQ scheduler.
    
    This should be called once when the worker starts.
    """
    redis_url = settings.redis_url
    redis_conn = Redis.from_url(redis_url)
    scheduler = Scheduler(connection=redis_conn, queue_name="default")
    
    # Clear existing scheduled jobs for these tasks
    for job in scheduler.get_jobs():
        if job.func_name in [
            "app.tasks.periodic_sync.run_sync_agents",
            "app.tasks.periodic_sync.run_sync_sessions",
            "app.tasks.periodic_sync.run_sync_tasks"
        ]:
            scheduler.cancel(job)
            logger.info(f"[periodic_sync] Cancelled existing job: {job.func_name}")
    
    # Schedule agent sync every 60 seconds
    scheduler.schedule(
        scheduled_time=datetime.utcnow() + timedelta(seconds=10),
        func="app.tasks.periodic_sync:run_sync_agents",
        interval=60,  # seconds
        repeat=None,  # repeat forever
        result_ttl=0,  # don't keep results
    )
    logger.info("[periodic_sync] Scheduled agent sync every 60 seconds")
    
    # Schedule session sync every 60 seconds (offset by 20s)
    scheduler.schedule(
        scheduled_time=datetime.utcnow() + timedelta(seconds=30),
        func="app.tasks.periodic_sync:run_sync_sessions",
        interval=60,  # seconds
        repeat=None,  # repeat forever
        result_ttl=0,  # don't keep results
    )
    logger.info("[periodic_sync] Scheduled session sync every 60 seconds")
    
    # Schedule task sync every 5 minutes (offset by 40s)
    scheduler.schedule(
        scheduled_time=datetime.utcnow() + timedelta(seconds=50),
        func="app.tasks.periodic_sync:run_sync_tasks",
        interval=300,  # 5 minutes
        repeat=None,  # repeat forever
        result_ttl=0,  # don't keep results
    )
    logger.info("[periodic_sync] Scheduled task sync every 5 minutes")
    
    return scheduler
