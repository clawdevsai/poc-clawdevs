from typing import Annotated, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination import Page, paginate
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

from app.core.database import get_session
from app.api.deps import CurrentUser
from app.models import SddArtifact

router = APIRouter()

ARTIFACT_TYPES = ["BRIEF", "SPEC", "CLARIFY", "PLAN", "TASK", "VALIDATE"]


class SddArtifactResponse(BaseModel):
    id: str
    agent_id: str | None
    artifact_type: str
    title: str
    content: str
    status: str
    github_issue_number: int | None
    github_issue_url: str | None
    file_path: str | None
    created_at: datetime
    updated_at: datetime


class CreateSddRequest(BaseModel):
    artifact_type: str
    title: str
    content: str = ""
    agent_id: str | None = None


class UpdateSddRequest(BaseModel):
    content: str | None = None
    status: str | None = None
    title: str | None = None


@router.get("", response_model=Page[SddArtifactResponse])
async def list_artifacts(
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
    artifact_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
):
    query = select(SddArtifact).order_by(SddArtifact.created_at.desc())
    if artifact_type:
        query = query.where(SddArtifact.artifact_type == artifact_type.upper())
    if status:
        query = query.where(SddArtifact.status == status)
    result = await session.exec(query)
    artifacts = result.all()
    return paginate([
        SddArtifactResponse(
            id=str(a.id), agent_id=str(a.agent_id) if a.agent_id else None,
            artifact_type=a.artifact_type, title=a.title, content=a.content,
            status=a.status, github_issue_number=a.github_issue_number,
            github_issue_url=a.github_issue_url, file_path=a.file_path,
            created_at=a.created_at, updated_at=a.updated_at,
        )
        for a in artifacts
    ])


@router.post("", response_model=SddArtifactResponse, status_code=201)
async def create_artifact(
    body: CreateSddRequest,
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    from datetime import datetime, timezone
    if body.artifact_type.upper() not in ARTIFACT_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid artifact_type. Must be one of: {ARTIFACT_TYPES}")
    artifact = SddArtifact(
        artifact_type=body.artifact_type.upper(),
        title=body.title,
        content=body.content,
        agent_id=UUID(body.agent_id) if body.agent_id else None,
        updated_at=datetime.now(timezone.utc),
    )
    session.add(artifact)
    await session.commit()
    await session.refresh(artifact)
    return SddArtifactResponse(
        id=str(artifact.id), agent_id=str(artifact.agent_id) if artifact.agent_id else None,
        artifact_type=artifact.artifact_type, title=artifact.title, content=artifact.content,
        status=artifact.status, github_issue_number=artifact.github_issue_number,
        github_issue_url=artifact.github_issue_url, file_path=artifact.file_path,
        created_at=artifact.created_at, updated_at=artifact.updated_at,
    )


@router.get("/{artifact_id}", response_model=SddArtifactResponse)
async def get_artifact(
    artifact_id: str,
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    result = await session.exec(select(SddArtifact).where(SddArtifact.id == UUID(artifact_id)))
    artifact = result.first()
    if artifact is None:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return SddArtifactResponse(
        id=str(artifact.id), agent_id=str(artifact.agent_id) if artifact.agent_id else None,
        artifact_type=artifact.artifact_type, title=artifact.title, content=artifact.content,
        status=artifact.status, github_issue_number=artifact.github_issue_number,
        github_issue_url=artifact.github_issue_url, file_path=artifact.file_path,
        created_at=artifact.created_at, updated_at=artifact.updated_at,
    )


@router.patch("/{artifact_id}", response_model=SddArtifactResponse)
async def update_artifact(
    artifact_id: str,
    body: UpdateSddRequest,
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    from datetime import datetime, timezone
    result = await session.exec(select(SddArtifact).where(SddArtifact.id == UUID(artifact_id)))
    artifact = result.first()
    if artifact is None:
        raise HTTPException(status_code=404, detail="Artifact not found")
    if body.content is not None:
        artifact.content = body.content
    if body.status is not None:
        artifact.status = body.status
    if body.title is not None:
        artifact.title = body.title
    artifact.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(artifact)
    return SddArtifactResponse(
        id=str(artifact.id), agent_id=str(artifact.agent_id) if artifact.agent_id else None,
        artifact_type=artifact.artifact_type, title=artifact.title, content=artifact.content,
        status=artifact.status, github_issue_number=artifact.github_issue_number,
        github_issue_url=artifact.github_issue_url, file_path=artifact.file_path,
        created_at=artifact.created_at, updated_at=artifact.updated_at,
    )
