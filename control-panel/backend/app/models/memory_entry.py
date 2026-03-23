from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import ARRAY, TEXT


class MemoryEntry(SQLModel, table=True):
    __tablename__ = "memory_entries"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    agent_id: Optional[UUID] = Field(default=None, foreign_key="agents.id", index=True)  # null = shared
    entry_type: str = Field(default="active", index=True)  # active|candidate|global|archived
    content: str
    tags: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(TEXT), nullable=True))
    source_agents: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(TEXT), nullable=True))
    promoted_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
