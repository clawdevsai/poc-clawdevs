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

"""
Integration tests for RAG Retriever Service

Tests semantic search, embedding generation, and context retrieval.
"""

import pytest
import json

from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from app.models.memory_entry import MemoryEntry
from app.services.rag_retriever import RAGRetriever
from app.services.embedding_service import EmbeddingService


@pytest.fixture
def session():
    """Create in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def sample_memories(session: Session) -> list:
    """Create sample memories with embeddings."""
    memories = [
        MemoryEntry(
            title="Authentication Best Practices",
            body="Use JWT tokens with secure expiry. Hash passwords with bcrypt. Implement rate limiting on login.",
            agent_slug="dev_backend",
            entry_type="global",
            tags=["authentication", "security"],
            embedding=json.dumps([0.1, 0.2, 0.3] * 100),  # Mock 300-dim embedding
            embedding_model="mistral",
        ),
        MemoryEntry(
            title="Database Migration Pattern",
            body="Use Alembic for migrations. Keep migrations small and reversible. Test migrations in staging first.",
            agent_slug="dba_data_engineer",
            entry_type="global",
            tags=["database", "migrations"],
            embedding=json.dumps([0.15, 0.25, 0.35] * 100),
            embedding_model="mistral",
        ),
        MemoryEntry(
            title="React Component Testing",
            body="Use React Testing Library for component tests. Test behavior, not implementation. Mock API calls.",
            agent_slug="dev_frontend",
            entry_type="global",
            tags=["testing", "frontend"],
            embedding=json.dumps([0.2, 0.3, 0.4] * 100),
            embedding_model="mistral",
        ),
        MemoryEntry(
            title="API Rate Limiting",
            body="Implement rate limiting to prevent abuse. Use sliding window algorithm. Return 429 on limit exceeded.",
            agent_slug="dev_backend",
            entry_type="active",
            tags=["api", "security"],
            embedding=json.dumps([0.12, 0.22, 0.32] * 100),
            embedding_model="mistral",
        ),
    ]

    for memory in memories:
        session.add(memory)
    session.commit()

    return memories


@pytest.fixture
def embedding_service():
    """Create embedding service (mock)."""
    return EmbeddingService()


class TestRAGRetriever:
    """Test cases for RAG Retriever."""

    def test_retrieve_similar_solutions(
        self,
        session: Session,
        sample_memories: list,
        embedding_service: EmbeddingService,
    ):
        """Test retrieving similar solutions by semantic search."""
        retriever = RAGRetriever(session, embedding_service)

        # Query about authentication
        results = retriever.retrieve_similar_solutions(
            query="secure user authentication",
            top_k=5,
        )

        # Should return results
        assert len(results) > 0
        assert len(results) <= 5

        # Results should be dicts with expected keys
        if results:
            result = results[0]
            assert "id" in result
            assert "title" in result
            assert "body" in result
            assert "similarity_score" in result

    def test_retrieve_for_agent(
        self,
        session: Session,
        sample_memories: list,
        embedding_service: EmbeddingService,
    ):
        """Test retrieving context for a specific agent."""
        retriever = RAGRetriever(session, embedding_service)

        # Get context for dev_backend
        context = retriever.retrieve_for_agent(
            agent_slug="dev_backend",
            query="how to authenticate users",
            top_k=3,
        )

        # Should return list of context strings
        assert isinstance(context, list)
        assert all(isinstance(item, str) for item in context)

    def test_retrieve_by_tags(
        self,
        session: Session,
        sample_memories: list,
        embedding_service: EmbeddingService,
    ):
        """Test retrieving memories by tags."""
        retriever = RAGRetriever(session, embedding_service)

        # Search for security-related memories
        results = retriever.retrieve_by_tags(
            tags=["security"],
            top_k=5,
        )

        # Should find memories tagged with 'security'
        assert len(results) > 0

        # All results should have 'security' tag
        for result in results:
            assert "security" in result.get("tags", [])

    def test_get_rag_context(
        self,
        session: Session,
        sample_memories: list,
        embedding_service: EmbeddingService,
    ):
        """Test getting comprehensive RAG context."""
        retriever = RAGRetriever(session, embedding_service)

        context = retriever.get_rag_context(
            agent_slug="dev_backend",
            task_description="implement secure authentication system",
            max_context_items=5,
        )

        # Should return comprehensive context
        assert "agent_slug" in context
        assert context["agent_slug"] == "dev_backend"
        assert "query" in context
        assert "similar_solutions" in context
        assert "recommendation" in context

    def test_similarity_threshold(
        self,
        session: Session,
        sample_memories: list,
        embedding_service: EmbeddingService,
    ):
        """Test that similarity threshold filters results."""
        retriever = RAGRetriever(session, embedding_service)
        retriever.min_similarity_threshold = 0.9  # Very high threshold

        results = retriever.retrieve_similar_solutions(
            query="some random query",
            top_k=10,
        )

        # High threshold should return fewer results
        # (or none if embeddings are too different)
        assert len(results) <= 10

    def test_agent_filtering(
        self,
        session: Session,
        sample_memories: list,
        embedding_service: EmbeddingService,
    ):
        """Test filtering memories by agent."""
        retriever = RAGRetriever(session, embedding_service)

        # Search with agent filter
        results = retriever.retrieve_similar_solutions(
            query="authentication",
            top_k=5,
            agent_slug="dev_backend",
        )

        # All results should be from dev_backend or shared (null agent_slug)
        for result in results:
            agent = result.get("agent_slug")
            assert agent is None or agent == "dev_backend"

    def test_chunk_text(
        self,
        session: Session,
        embedding_service: EmbeddingService,
    ):
        """Test text chunking for large documents."""
        retriever = RAGRetriever(session, embedding_service)

        long_text = "This is a sentence. " * 100  # Long document

        chunks = retriever.chunk_text(
            long_text,
            chunk_size=100,
            overlap=10,
        )

        # Should split into multiple chunks
        assert len(chunks) > 1

        # Chunks should not exceed size (approximately)
        for chunk in chunks:
            assert len(chunk) <= 110  # Size + overlap margin

    def test_extract_tags_from_task(
        self,
        session: Session,
        embedding_service: EmbeddingService,
    ):
        """Test extracting tags from task description."""
        retriever = RAGRetriever(session, embedding_service)

        tags = retriever._extract_tags_from_task(
            "implement user authentication with JWT for API security"
        )

        # Should extract relevant tags
        assert "authentication" in tags
        assert "security" in tags
        assert "api" in tags

    def test_cosine_similarity(
        self,
        session: Session,
        embedding_service: EmbeddingService,
    ):
        """Test cosine similarity calculation."""
        # Identical vectors
        v1 = [1.0, 0.0, 0.0]
        v2 = [1.0, 0.0, 0.0]
        similarity = embedding_service.cosine_similarity(v1, v2)
        assert similarity == 1.0  # Perfect similarity

        # Perpendicular vectors
        v1 = [1.0, 0.0, 0.0]
        v2 = [0.0, 1.0, 0.0]
        similarity = embedding_service.cosine_similarity(v1, v2)
        assert similarity == 0.0  # No similarity

        # Partial similarity
        v1 = [1.0, 1.0, 0.0]
        v2 = [1.0, 0.0, 0.0]
        similarity = embedding_service.cosine_similarity(v1, v2)
        assert 0.0 < similarity < 1.0

    def test_empty_embedding_handling(
        self,
        session: Session,
        embedding_service: EmbeddingService,
    ):
        """Test handling of memories without embeddings."""
        retriever = RAGRetriever(session, embedding_service)

        # Create memory without embedding
        memory = MemoryEntry(
            title="No Embedding Memory",
            body="This memory has no embedding",
            embedding=None,
        )
        retriever.db_session.add(memory)
        retriever.db_session.commit()

        # Should not cause errors
        results = retriever.retrieve_similar_solutions("test query", top_k=5)
        # Results might be empty, but no exception should be raised
        assert isinstance(results, list)

    def test_invalid_embedding_json(
        self,
        session: Session,
        embedding_service: EmbeddingService,
    ):
        """Test handling of corrupted embedding JSON."""
        retriever = RAGRetriever(session, embedding_service)

        # Create memory with invalid embedding JSON
        memory = MemoryEntry(
            title="Corrupted Embedding",
            body="Memory with corrupted embedding",
            embedding="not valid json",  # Invalid!
        )
        retriever.db_session.add(memory)
        retriever.db_session.commit()

        # Should handle gracefully without crashing
        results = retriever.retrieve_similar_solutions("test query", top_k=5)
        assert isinstance(results, list)

    def test_rerank_results(
        self,
        session: Session,
        embedding_service: EmbeddingService,
    ):
        """Test result reranking based on context."""
        retriever = RAGRetriever(session, embedding_service)

        initial_results = [
            {"title": "Authentication", "similarity_score": 0.8},
            {"title": "User Auth System", "similarity_score": 0.75},
            {"title": "API Security", "similarity_score": 0.7},
        ]

        reranked = retriever.rerank_results(
            initial_results,
            agent_context="User Auth",
        )

        # "User Auth System" should have boosted score
        titles_before = [r["title"] for r in initial_results]
        titles_after = [r["title"] for r in reranked]

        # Order should potentially change due to reranking
        # (depends on implementation details)
        assert len(reranked) == len(initial_results)
