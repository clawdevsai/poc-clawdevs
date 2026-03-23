from sqlmodel import SQLModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB


class Approval(SQLModel, table=True):
    __tablename__ = "approvals"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    agent_id: Optional[UUID] = Field(default=None, foreign_key="agents.id", index=True)
    openclaw_approval_id: Optional[str] = Field(default=None, index=True)
    action_type: str
    payload: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSONB)
    )
    confidence: Optional[float] = None
    rubric_scores: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSONB)
    )
    status: str = Field(default="pending", index=True)  # pending|approved|rejected
    decided_by_id: Optional[UUID] = Field(default=None, foreign_key="users.id", index=True)
    justification: Optional[str] = None
    decided_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
