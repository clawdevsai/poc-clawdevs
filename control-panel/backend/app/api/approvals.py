from typing import Annotated, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination import Page, paginate
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_session
from app.api.deps import CurrentUser
from app.models import Approval, Agent, ActivityEvent

router = APIRouter()


class ApprovalResponse(BaseModel):
    id: str
    agent_id: str | None
    agent_slug: str | None
    openclaw_approval_id: str | None
    action_type: str
    payload: dict | None
    confidence: float | None
    rubric_scores: dict | None
    status: str
    decided_by_id: str | None
    justification: str | None
    decided_at: datetime | None
    created_at: datetime


class DecideRequest(BaseModel):
    decision: str  # approved|rejected
    justification: str = ""


class ApprovalStats(BaseModel):
    pending: int
    approved: int
    rejected: int


@router.get("", response_model=Page[ApprovalResponse])
async def list_approvals(
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
    status: Optional[str] = Query(None),
):
    query = select(Approval).order_by(Approval.created_at.desc())
    if status:
        query = query.where(Approval.status == status)
    result = await session.exec(query)
    approvals = result.all()

    # Fetch agent slugs
    agent_slugs: dict[str, str] = {}
    if approvals:
        agent_ids = {str(a.agent_id) for a in approvals if a.agent_id}
        if agent_ids:
            agents_result = await session.exec(select(Agent))
            for ag in agents_result.all():
                agent_slugs[str(ag.id)] = ag.slug

    items = []
    for a in approvals:
        items.append(ApprovalResponse(
            id=str(a.id),
            agent_id=str(a.agent_id) if a.agent_id else None,
            agent_slug=agent_slugs.get(str(a.agent_id)) if a.agent_id else None,
            openclaw_approval_id=a.openclaw_approval_id,
            action_type=a.action_type,
            payload=a.payload,
            confidence=a.confidence,
            rubric_scores=a.rubric_scores,
            status=a.status,
            decided_by_id=str(a.decided_by_id) if a.decided_by_id else None,
            justification=a.justification,
            decided_at=a.decided_at,
            created_at=a.created_at,
        ))
    return paginate(items)


@router.get("/stats", response_model=ApprovalStats)
async def approval_stats(
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    result = await session.exec(select(Approval))
    all_approvals = result.all()
    return ApprovalStats(
        pending=sum(1 for a in all_approvals if a.status == "pending"),
        approved=sum(1 for a in all_approvals if a.status == "approved"),
        rejected=sum(1 for a in all_approvals if a.status == "rejected"),
    )


@router.get("/{approval_id}", response_model=ApprovalResponse)
async def get_approval(
    approval_id: str,
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    from uuid import UUID
    result = await session.exec(
        select(Approval).where(Approval.id == UUID(approval_id))
    )
    approval = result.first()
    if approval is None:
        raise HTTPException(status_code=404, detail="Approval not found")
    return ApprovalResponse(
        id=str(approval.id),
        agent_id=str(approval.agent_id) if approval.agent_id else None,
        agent_slug=None,
        openclaw_approval_id=approval.openclaw_approval_id,
        action_type=approval.action_type,
        payload=approval.payload,
        confidence=approval.confidence,
        rubric_scores=approval.rubric_scores,
        status=approval.status,
        decided_by_id=str(approval.decided_by_id) if approval.decided_by_id else None,
        justification=approval.justification,
        decided_at=approval.decided_at,
        created_at=approval.created_at,
    )


@router.post("/{approval_id}/decide", response_model=ApprovalResponse)
async def decide_approval(
    approval_id: str,
    body: DecideRequest,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    from uuid import UUID
    from datetime import datetime, timezone
    from app.services.openclaw_client import openclaw_client

    if body.decision not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="decision must be 'approved' or 'rejected'")

    result = await session.exec(
        select(Approval).where(Approval.id == UUID(approval_id))
    )
    approval = result.first()
    if approval is None:
        raise HTTPException(status_code=404, detail="Approval not found")
    if approval.status != "pending":
        raise HTTPException(status_code=409, detail="Approval already decided")

    # Try to notify gateway (best-effort — never fails the endpoint)
    if approval.openclaw_approval_id:
        try:
            await openclaw_client.decide_approval(
                approval.openclaw_approval_id, body.decision, body.justification
            )
        except Exception:
            pass  # Gateway unavailable is not a blocker for local persistence

    approval.status = body.decision
    approval.decided_by_id = current_user.id
    approval.justification = body.justification
    approval.decided_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(approval)

    # Log activity
    event = ActivityEvent(
        event_type=f"approval.{body.decision}",
        user_id=current_user.id,
        entity_type="approval",
        entity_id=approval_id,
        payload={"justification": body.justification},
    )
    session.add(event)
    await session.commit()

    return ApprovalResponse(
        id=str(approval.id),
        agent_id=str(approval.agent_id) if approval.agent_id else None,
        agent_slug=None,
        openclaw_approval_id=approval.openclaw_approval_id,
        action_type=approval.action_type,
        payload=approval.payload,
        confidence=approval.confidence,
        rubric_scores=approval.rubric_scores,
        status=approval.status,
        decided_by_id=str(approval.decided_by_id) if approval.decided_by_id else None,
        justification=approval.justification,
        decided_at=approval.decided_at,
        created_at=approval.created_at,
    )
