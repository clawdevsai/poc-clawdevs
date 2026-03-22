from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str
    description: Optional[str] = None
    status: str = Field(default="inbox", index=True)  # inbox|in_progress|review|done
    priority: str = Field(default="medium")  # low|medium|high
    assigned_agent_id: Optional[UUID] = Field(default=None, foreign_key="agents.id", index=True)
    github_issue_number: Optional[int] = None
    github_issue_url: Optional[str] = None
    github_repo: Optional[str] = None
    due_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
