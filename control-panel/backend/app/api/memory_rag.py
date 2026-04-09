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
Memory RAG API Endpoints

Provides semantic memory search and retrieval for agent decision-making.
Agents can query for relevant past solutions and patterns.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlmodel import col
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.api.deps import CurrentUser
from app.services.rag_retriever import RAGRetriever
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/memory/rag", tags=["memory_rag"])


@router.get("/search")
async def search_memories(
    _: CurrentUser,
    query: str = Query(..., min_length=3, max_length=1000, description="Search query"),
    top_k: int = Query(5, ge=1, le=20, description="Number of results"),
    agent_slug: Optional[str] = Query(None, description="Filter to specific agent"),
    session_key: Optional[str] = Query(
        None,
        max_length=512,
        description="Prioritize memories from the same chat session",
    ),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Semantic search across all memories.

    Returns most similar solutions for the given query.

    **Example:**
    ```
    GET /api/memory/rag/search?query=how+to+handle+database+migrations&top_k=5
    ```

    Returns:
    - Similar memories with similarity scores
    - Up to 5 most relevant results
    - Formatted for agent consumption
    """
    retriever = RAGRetriever(session)

    results = await retriever.retrieve_similar_solutions(
        query=query,
        top_k=top_k,
        agent_slug=agent_slug,
        session_key=session_key,
    )

    return {
        "query": query,
        "agent_slug": agent_slug,
        "session_key": session_key,
        "results_count": len(results),
        "top_k_requested": top_k,
        "results": results,
    }


@router.get("/agent/{agent_slug}/context")
async def get_agent_rag_context(
    agent_slug: str,
    _: CurrentUser,
    task_description: str = Query(..., min_length=10, max_length=1000),
    session_key: Optional[str] = Query(
        None,
        max_length=512,
        description="Prioritize memories from the same chat session",
    ),
    max_items: int = Query(5, ge=1, le=20),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Get comprehensive RAG context for an agent's task.

    Combines semantic search and pattern matching to provide
    relevant historical context and similar solutions.

    **Example:**
    ```
    GET /api/memory/rag/agent/dev_backend/context?task_description=implement+user+authentication&max_items=5
    ```

    Returns:
    - Similar solutions to guide implementation
    - Relevant patterns from past tasks
    - Recommendation for approach
    """
    retriever = RAGRetriever(session)

    context = await retriever.get_rag_context(
        agent_slug=agent_slug,
        task_description=task_description,
        session_key=session_key,
        max_context_items=max_items,
    )

    return context


@router.get("/tags")
async def search_by_tags(
    _: CurrentUser,
    tags: List[str] = Query(..., min_items=1, description="Tags to search for"),
    top_k: int = Query(5, ge=1, le=20),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Search memories by tags.

    Returns memories tagged with any of the provided tags.

    **Example:**
    ```
    GET /api/memory/rag/tags?tags=authentication&tags=security&top_k=5
    ```
    """
    retriever = RAGRetriever(session)

    results = await retriever.retrieve_by_tags(
        tags=tags,
        top_k=top_k,
    )

    return {
        "tags": tags,
        "results_count": len(results),
        "results": results,
    }


@router.get("/health")
async def rag_health(_: CurrentUser) -> dict:
    """
    Check RAG service health.

    Verifies that embeddings and Ollama are working.
    """
    embedding_service = EmbeddingService()
    ollama_healthy = embedding_service.get_health()

    return {
        "status": "healthy" if ollama_healthy else "degraded",
        "ollama_available": ollama_healthy,
        "embedding_model": embedding_service.model,
        "message": (
            "RAG system operational"
            if ollama_healthy
            else "Ollama service not available. Ensure Ollama is running."
        ),
    }


@router.post("/regenerate-embeddings")
async def regenerate_embeddings(
    _: CurrentUser,
    limit: int = Query(100, ge=1, le=1000, description="Max memories to regenerate"),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Regenerate embeddings for memories.

    Useful after updating embedding model or fixing corrupted embeddings.

    **Warning:** This is computationally expensive for large numbers of memories.
    """
    from sqlmodel import select
    from app.models.memory_entry import MemoryEntry
    from datetime import datetime, timezone

    RAGRetriever(session)
    embedding_service = EmbeddingService()

    # Get memories without embeddings
    statement = (
        select(MemoryEntry)
        .where(
            col(MemoryEntry.embedding).is_(None) & col(MemoryEntry.body).is_not(None)
        )
        .limit(limit)
    )

    memories = (await session.exec(statement)).all()

    regenerated = 0
    failed = 0

    for memory in memories:
        if not memory.body:
            continue

        # Generate embedding
        embedding = await embedding_service.generate_embedding(memory.body)

        if embedding:
            memory.embedding = embedding
            memory.embedding_generated_at = datetime.now(timezone.utc)
            regenerated += 1
        else:
            failed += 1

        session.add(memory)

    await session.commit()

    return {
        "total_memories_processed": len(memories),
        "embeddings_regenerated": regenerated,
        "failures": failed,
        "message": f"Regenerated {regenerated} embeddings (failed: {failed})",
    }
