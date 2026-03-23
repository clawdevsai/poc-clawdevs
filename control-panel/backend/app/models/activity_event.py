from sqlmodel import SQLModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB


class ActivityEvent(SQLModel, table=True):
    __tablename__ = "activity_events"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    event_type: str = Field(index=True)
    agent_id: Optional[UUID] = Field(default=None, foreign_key="agents.id", index=True)
    user_id: Optional[UUID] = Field(default=None, foreign_key="users.id")
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    payload: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
