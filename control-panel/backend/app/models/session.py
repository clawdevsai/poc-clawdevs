from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4


class Session(SQLModel, table=True):
    __tablename__ = "sessions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    agent_id: Optional[UUID] = Field(default=None, foreign_key="agents.id", index=True)
    openclaw_session_id: str = Field(index=True)
    channel_type: Optional[str] = None  # telegram|cli|agent-to-agent
    channel_peer: Optional[str] = None
    message_count: int = Field(default=0)
    token_count: int = Field(default=0)
    started_at: Optional[datetime] = None
    last_active_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
