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

from fastapi import APIRouter, HTTPException, status
from app.api.deps import CurrentUser
from app.core.config import get_settings
from app.services import k8s_client

settings = get_settings()
router = APIRouter()


def _ensure_k8s_available() -> None:
    core, _ = k8s_client.get_k8s_clients()
    if core is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Kubernetes client unavailable in backend container. Verify backend image dependencies.",
        )


@router.get("/pods")
async def get_pods(_: CurrentUser):
    _ensure_k8s_available()
    return k8s_client.list_pods(namespace=settings.k8s_namespace)


@router.get("/info")
async def get_cluster_info(_: CurrentUser):
    return k8s_client.get_cluster_info(namespace=settings.k8s_namespace)


@router.get("/events")
async def get_events(_: CurrentUser):
    _ensure_k8s_available()
    return k8s_client.list_events(namespace=settings.k8s_namespace)


@router.get("/pvcs")
async def get_pvcs(_: CurrentUser):
    _ensure_k8s_available()
    return k8s_client.list_pvcs(namespace=settings.k8s_namespace)
