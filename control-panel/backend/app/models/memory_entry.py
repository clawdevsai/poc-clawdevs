from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import Text


class MemoryEntry(SQLModel, table=True):
    __tablename__ = "memory_entries"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    agent_slug: Optional[str] = Field(default=None, index=True)  # null = shared
    title: str
    body: Optional[str] = None
    entry_type: str = Field(default="active", index=True)  # active|candidate|global|archived
    tags: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(Text), nullable=True))
    source_agents: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(Text), nullable=True))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
