# Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Column, Text, JSON, TypeDecorator
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY

try:
    from pgvector.sqlalchemy import Vector

    HAS_PGVECTOR = True
except ImportError:
    # Fallback for non-PostgreSQL environments (testing)
    Vector = None
    HAS_PGVECTOR = False


class ArrayOrJSON(TypeDecorator):
    """Dialect-aware type that uses PostgreSQL ARRAY when available, JSON otherwise."""

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_ARRAY(Text))
        return dialect.type_descriptor(JSON)


class VectorOrJSON(TypeDecorator):
    """Dialect-aware type that uses pgvector Vector when available, JSON otherwise."""

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql" and HAS_PGVECTOR:
            return dialect.type_descriptor(Vector(1536))
        return dialect.type_descriptor(JSON)


class MemoryEntry(SQLModel, table=True):
    __tablename__ = "memory_entries"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    agent_slug: Optional[str] = Field(default=None, index=True)  # null = shared
    title: str
    body: Optional[str] = None
    entry_type: str = Field(
        default="active", index=True
    )  # active|candidate|global|archived
    tags: Optional[List[str]] = Field(
        default=None,
        sa_column=Column(ArrayOrJSON(), nullable=True),
    )
    source_agents: Optional[List[str]] = Field(
        default=None,
        sa_column=Column(ArrayOrJSON(), nullable=True),
    )

    # Vector embedding fields (for RAG/semantic search)
    # Note: For PostgreSQL, use pgvector.sqlalchemy.Vector; for testing use JSON
    embedding: Optional[List[float]] = Field(
        default=None,
        sa_column=Column(VectorOrJSON()),
    )
    embedding_model: str = Field(
        default="mistral"
    )  # Which model generated the embedding
    chunk_index: int = Field(
        default=0
    )  # For chunked documents (0 = single/first chunk)
    source_file_path: Optional[str] = Field(
        default=None
    )  # Where this memory came from (agent/slug/MEMORY.md)
    embedding_generated_at: Optional[datetime] = Field(
        default=None
    )  # When embedding was created

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
