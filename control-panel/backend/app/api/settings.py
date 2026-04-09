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

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import CurrentUser
from app.core.config import get_settings
from app.core.database import get_session
from app.services.openclaw_client import openclaw_client
from app.services import container_client
from app.services.runtime_settings import RuntimeSettingsService

settings = get_settings()
router = APIRouter()


class AgentUpdateRequest(BaseModel):
    agent_id: str | None = None
    agent_slug: str | None = None
    enabled: bool


class RuntimeSettingsUpdateRequest(BaseModel):
    limits: dict | None = None
    flags: dict | None = None
    model_provider: str | None = None
    model_name: str | None = None
    agent_updates: list[AgentUpdateRequest] | None = None
    thresholds: dict | None = None
    confirm_text: str | None = None


@router.get("/info")
async def get_settings_info(_: AdminUser):
    cluster_info = container_client.get_cluster_info(namespace=settings.container_namespace)
    return {
        "gateway_url": settings.openclaw_gateway_url,
        "cluster_namespace": cluster_info.get("namespace") or settings.container_namespace,
        "container_version": cluster_info.get("version") or "unknown",
    }


@router.get("/gateway-health")
async def get_gateway_health(_: AdminUser):
    healthy = await openclaw_client.health()
    return {"status": "ok" if healthy else "error"}


@router.get("/runtime")
async def get_runtime_settings(
    _: CurrentUser,
    session: AsyncSession = Depends(get_session),
):
    service = RuntimeSettingsService(session, settings)
    return await service.get_settings()


@router.put("/runtime")
async def update_runtime_settings(
    body: RuntimeSettingsUpdateRequest,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_session),
):
    service = RuntimeSettingsService(session, settings)
    try:
        payload = body.model_dump(exclude_unset=True)
        payload["agent_updates"] = (
            [item.model_dump() for item in body.agent_updates]
            if body.agent_updates is not None
            else None
        )
        result = await service.update_settings(payload, current_user)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return result
