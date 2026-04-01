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

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlmodel import select
import logging

from app.core.config import get_settings
from app.core.database import AsyncSessionLocal, run_migrations
from app.core.auth import get_password_hash
from app.models import User
from app.api import auth as auth_api
from app.api import agents as agents_api
from app.api import approvals as approvals_api
from app.api import sessions as sessions_api
from app.api import tasks as tasks_api
from app.api import sdd as sdd_api
from app.api import memory as memory_api
from app.api import crons as crons_api
from app.api import cluster as cluster_api
from app.api import metrics as metrics_api
from app.api import activity_events as activity_events_api
from app.api import ws as ws_api
from app.api import repositories as repositories_api
from app.api import settings as settings_api
from app.api import health as health_api
from app.api import memory_rag as memory_rag_api
from app.api import governance as governance_api
from app.api import chat as chat_api
from app.api import agent_permissions as agent_permissions_api
from app.api import context_mode as context_mode_api
from app.api import context_mode_memory as context_mode_memory_api
from app.services.context_mode_metrics_broadcaster import ContextModeMetricsBroadcaster

settings = get_settings()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def bootstrap_admin():
    async with AsyncSessionLocal() as session:
        result = await session.exec(
            select(User).where(User.username == settings.admin_username)
        )
        if result.first() is None:
            admin = User(
                username=settings.admin_username,
                password_hash=get_password_hash(settings.admin_password),
                role="admin",
            )
            session.add(admin)
            await session.commit()


async def bootstrap_agents():
    from app.services.agent_sync import sync_agents

    try:
        async with AsyncSessionLocal() as session:
            await sync_agents(session)
        logger.info("Agent bootstrap completed successfully")
    except Exception as e:
        logger.error(f"Agent bootstrap failed: {e}", exc_info=True)
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    await run_migrations()
    await bootstrap_admin()
    await bootstrap_agents()

    # Start health monitor
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

    # Start context-mode metrics broadcaster
    metrics_broadcaster = ContextModeMetricsBroadcaster(interval_seconds=30)
    app.state.metrics_broadcaster = metrics_broadcaster
    await metrics_broadcaster.start()

    yield

    # Stop context-mode metrics broadcaster
    if hasattr(app.state, 'metrics_broadcaster'):
        await app.state.metrics_broadcaster.stop()

    # Stop health monitor
    if hasattr(app.state, 'health_monitor'):
        await app.state.health_monitor.stop()


app = FastAPI(
    title="ClawDevs Panel API",
    version="0.1.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routers
app.include_router(auth_api.router, prefix="/auth", tags=["auth"])
app.include_router(agents_api.router, prefix="/agents", tags=["agents"])
app.include_router(approvals_api.router, prefix="/approvals", tags=["approvals"])
app.include_router(sessions_api.router, prefix="/sessions", tags=["sessions"])
app.include_router(tasks_api.router, prefix="/tasks", tags=["tasks"])
app.include_router(
    repositories_api.router, prefix="/repositories", tags=["repositories"]
)
app.include_router(settings_api.router, prefix="/settings", tags=["settings"])
app.include_router(sdd_api.router, prefix="/sdd", tags=["sdd"])
app.include_router(memory_api.router, prefix="/memory", tags=["memory"])
app.include_router(memory_rag_api.router, tags=["memory"])
app.include_router(crons_api.router, prefix="/crons", tags=["crons"])
app.include_router(cluster_api.router, prefix="/cluster", tags=["cluster"])
app.include_router(metrics_api.router, prefix="/metrics", tags=["metrics"])
app.include_router(
    activity_events_api.router, prefix="/activity-events", tags=["activity"]
)
app.include_router(health_api.router, tags=["health"])
app.include_router(governance_api.router, tags=["governance"])
app.include_router(chat_api.router, tags=["chat"])
app.include_router(agent_permissions_api.router, tags=["agent-permissions"])
app.include_router(context_mode_api.router, prefix="/api", tags=["context-mode"])
app.include_router(context_mode_memory_api.router, tags=["context-mode"])

# WebSocket
app.include_router(ws_api.router, tags=["websocket"])


@app.get("/healthz", tags=["health"])
async def health():
    return {"status": "ok"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
