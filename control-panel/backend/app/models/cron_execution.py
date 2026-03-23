from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4


class CronExecution(SQLModel, table=True):
    __tablename__ = "cron_executions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    agent_id: UUID = Field(foreign_key="agents.id", index=True)
    started_at: datetime
    finished_at: Optional[datetime] = None
    exit_code: Optional[int] = None
    log_tail: Optional[str] = None  # last N lines of log
    trigger_type: str = Field(default="scheduled")  # scheduled|manual
    created_at: datetime = Field(default_factory=datetime.utcnow)
