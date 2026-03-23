from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
from sqlmodel import select

from app.core.config import get_settings
from app.core.database import AsyncSessionLocal
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
from app.api import ws as ws_api

settings = get_settings()


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
    async with AsyncSessionLocal() as session:
        await sync_agents(session)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await bootstrap_admin()
    await bootstrap_agents()
    yield


app = FastAPI(
    title="ClawDevs Panel API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://clawdevs-panel-frontend:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

add_pagination(app)

# API routers
app.include_router(auth_api.router, prefix="/auth", tags=["auth"])
app.include_router(agents_api.router, prefix="/agents", tags=["agents"])
app.include_router(approvals_api.router, prefix="/approvals", tags=["approvals"])
app.include_router(sessions_api.router, prefix="/sessions", tags=["sessions"])
app.include_router(tasks_api.router, prefix="/tasks", tags=["tasks"])
app.include_router(sdd_api.router, prefix="/sdd", tags=["sdd"])
app.include_router(memory_api.router, prefix="/memory", tags=["memory"])
app.include_router(crons_api.router, prefix="/crons", tags=["crons"])
app.include_router(cluster_api.router, prefix="/cluster", tags=["cluster"])
app.include_router(metrics_api.router, prefix="/metrics", tags=["metrics"])

# WebSocket
app.include_router(ws_api.router, tags=["websocket"])


@app.get("/healthz", tags=["health"])
async def health():
    return {"status": "ok"}
