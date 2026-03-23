from typing import Annotated
from fastapi import APIRouter, Depends
from app.api.deps import CurrentUser
from app.core.config import get_settings
from app.services import k8s_client

settings = get_settings()
router = APIRouter()


@router.get("/pods")
async def get_pods(_: CurrentUser):
    return k8s_client.list_pods(namespace=settings.k8s_namespace)


@router.get("/events")
async def get_events(_: CurrentUser):
    return k8s_client.list_events(namespace=settings.k8s_namespace)


@router.get("/pvcs")
async def get_pvcs(_: CurrentUser):
    return k8s_client.list_pvcs(namespace=settings.k8s_namespace)
