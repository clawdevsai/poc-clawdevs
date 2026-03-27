#!/usr/bin/env python3

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

"""Worker entry point with periodic task scheduling.

This script starts the RQ worker and schedules periodic sync tasks.
"""

import sys
import os
import logging
import signal

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from redis import Redis
from rq import Worker, Queue

from app.core.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

settings = get_settings()

# Global reference for shutdown handling
scheduler = None


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"[worker] Received signal {signum}, shutting down...")
    if scheduler:
        logger.info("[worker] Stopping scheduler...")
    sys.exit(0)


# Register signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


def main():
    """Start the worker with periodic task scheduling."""
    redis_url = settings.redis_url
    logger.info(f"[worker] Connecting to Redis at {redis_url}")

    redis_conn = Redis.from_url(redis_url)

    # Test connection
    try:
        redis_conn.ping()
        logger.info("[worker] Redis connection OK")
    except Exception as e:
        logger.error(f"[worker] Redis connection failed: {e}")
        sys.exit(1)

    # Schedule periodic tasks
    try:
        logger.info("[worker] Setting up periodic tasks...")
        from app.tasks.periodic_sync import schedule_periodic_tasks

        global scheduler
        scheduler = schedule_periodic_tasks()
        logger.info("[worker] Periodic tasks scheduled successfully")
    except Exception as e:
        logger.error(f"[worker] Failed to schedule periodic tasks: {e}")
        # Continue anyway - worker can still process jobs

    # Start worker
    logger.info("[worker] Starting RQ worker...")
    queues = [Queue("default", connection=redis_conn)]
    worker = Worker(queues, connection=redis_conn)
    worker.work(with_scheduler=True)


if __name__ == "__main__":
    main()
