from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4


class SddArtifact(SQLModel, table=True):
    __tablename__ = "sdd_artifacts"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    agent_id: Optional[UUID] = Field(default=None, foreign_key="agents.id", index=True)
    artifact_type: str = Field(index=True)  # BRIEF|SPEC|CLARIFY|PLAN|TASK|VALIDATE
    title: str
    content: str = Field(default="")
    status: str = Field(default="draft", index=True)  # draft|active|done
    github_issue_number: Optional[int] = None
    github_issue_url: Optional[str] = None
    file_path: Optional[str] = None  # path on PVC if synced from file
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
