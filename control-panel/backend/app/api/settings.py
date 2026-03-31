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

from fastapi import APIRouter
from app.api.deps import CurrentUser
from app.core.config import get_settings
from app.services.llm_runtime_client import llm_runtime_client as openclaw_client
from app.services import container_client

settings = get_settings()
router = APIRouter()


@router.get("/info")
async def get_settings_info(_: CurrentUser):
    cluster_info = container_client.get_cluster_info(namespace=settings.container_namespace)
    gateway_url = (settings.nemoclaw_gateway_url or settings.openclaw_gateway_url).rstrip("/")
    return {
        "gateway_url": gateway_url,
        "cluster_namespace": cluster_info.get("namespace") or settings.container_namespace,
        "container_version": cluster_info.get("version") or "unknown",
    }


@router.get("/gateway-health")
async def get_gateway_health(_: CurrentUser):
    healthy = await openclaw_client.health()
    return {"status": "ok" if healthy else "error"}
