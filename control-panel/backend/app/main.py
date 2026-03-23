from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from app.core.config import get_settings
from app.api import auth as auth_router
from app.api import agents as agents_router
from app.api import approvals as approvals_router
from app.core.database import AsyncSessionLocal
from app.services.agent_sync import sync_agents


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: sync agents from OpenClaw config
    try:
        async with AsyncSessionLocal() as session:
            await sync_agents(session)
    except Exception:
        pass  # Don't fail startup if sync fails (e.g. no DB connection yet)
    yield


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="ClawDevs AI Control Panel",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
    app.include_router(agents_router.router, prefix="/agents", tags=["agents"])
    app.include_router(approvals_router.router, prefix="/approvals", tags=["approvals"])

    add_pagination(app)

    @app.get("/healthz", tags=["health"])
    async def healthz():
        return {"status": "ok"}

    return app


app = create_app()
