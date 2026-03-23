from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4


class Agent(SQLModel, table=True):
    __tablename__ = "agents"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    slug: str = Field(unique=True, index=True)
    display_name: str
    role: str
    avatar_url: Optional[str] = None
    status: str = Field(default="unknown")  # active|inactive|error|unknown
    current_model: Optional[str] = None
    openclaw_session_id: Optional[str] = None
    last_heartbeat_at: Optional[datetime] = None
    cron_expression: Optional[str] = None
    cron_last_run_at: Optional[datetime] = None
    cron_next_run_at: Optional[datetime] = None
    cron_status: str = Field(default="idle")  # idle|running|error
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
