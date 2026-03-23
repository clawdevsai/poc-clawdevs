from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4


class Metric(SQLModel, table=True):
    __tablename__ = "metrics"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    agent_id: Optional[UUID] = Field(default=None, foreign_key="agents.id", index=True)
    metric_type: str = Field(index=True)  # tokens_used|tasks_completed|approvals_issued|errors
    value: float
    period_start: datetime = Field(index=True)
    period_end: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
