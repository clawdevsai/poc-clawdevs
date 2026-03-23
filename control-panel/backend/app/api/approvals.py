from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from app.core.database import get_session
from app.models import Approval, User
from app.api.deps import get_current_user
from app.services.openclaw_client import openclaw

router = APIRouter()


class ApprovalResponse(BaseModel):
    id: str
    agent_id: Optional[str]
    openclaw_approval_id: Optional[str]
    action_type: str
    payload: Optional[Dict[str, Any]]
    confidence: Optional[float]
    rubric_scores: Optional[Dict[str, Any]]
    status: str
    decided_by_id: Optional[str]
    justification: Optional[str]
    decided_at: Optional[datetime]
    created_at: datetime

    @classmethod
    def from_approval(cls, a: Approval) -> "ApprovalResponse":
        return cls(
            id=str(a.id),
            agent_id=str(a.agent_id) if a.agent_id else None,
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
        )


class DecideRequest(BaseModel):
    decision: str  # "approved" | "rejected"
    justification: str = ""


class ApprovalStats(BaseModel):
    pending: int
    approved: int
    rejected: int
    total: int


@router.get("/stats", response_model=ApprovalStats)
async def get_approval_stats(
    session: AsyncSession = Depends(get_session),
    _=Depends(get_current_user),
):
    from sqlalchemy import func
    from sqlmodel import select

    result = await session.exec(select(Approval))
    approvals = result.all()

    pending = sum(1 for a in approvals if a.status == "pending")
    approved = sum(1 for a in approvals if a.status == "approved")
    rejected = sum(1 for a in approvals if a.status == "rejected")

    return ApprovalStats(
        pending=pending,
        approved=approved,
        rejected=rejected,
        total=len(approvals),
    )


@router.get("", response_model=Page[ApprovalResponse])
async def list_approvals(
    status: Optional[str] = Query(None, description="Filter by status: pending|approved|rejected"),
    session: AsyncSession = Depends(get_session),
    _=Depends(get_current_user),
):
    query = select(Approval).order_by(Approval.created_at.desc())
    if status:
        query = query.where(Approval.status == status)
    result = await paginate(session, query)
    result.items = [ApprovalResponse.from_approval(a) for a in result.items]
    return result


@router.get("/{approval_id}", response_model=ApprovalResponse)
async def get_approval(
    approval_id: UUID,
    session: AsyncSession = Depends(get_session),
    _=Depends(get_current_user),
):
    result = await session.exec(select(Approval).where(Approval.id == approval_id))
    approval = result.first()
    if not approval:
        raise HTTPException(status_code=404, detail="Aprovação não encontrada")
    return ApprovalResponse.from_approval(approval)


@router.post("/{approval_id}/decide", response_model=ApprovalResponse)
async def decide_approval(
    approval_id: UUID,
    body: DecideRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if body.decision not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="decision must be 'approved' or 'rejected'")

    result = await session.exec(select(Approval).where(Approval.id == approval_id))
    approval = result.first()
    if not approval:
        raise HTTPException(status_code=404, detail="Aprovação não encontrada")

    if approval.status != "pending":
        raise HTTPException(status_code=409, detail="Esta aprovação já foi decidida")

    # Call gateway if openclaw_approval_id is set
    if approval.openclaw_approval_id:
        try:
            await openclaw.decide_approval(
                approval.openclaw_approval_id,
                body.decision,
                body.justification,
            )
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Erro ao comunicar com gateway: {e}")

    # Persist decision
    from datetime import datetime
    approval.status = body.decision
    approval.decided_by_id = current_user.id
    approval.justification = body.justification
    approval.decided_at = datetime.utcnow()
    session.add(approval)
    await session.commit()
    await session.refresh(approval)

    return ApprovalResponse.from_approval(approval)
