"""Semantic reranking of search results using Ollama embeddings."""
import logging
from typing import Optional
from app.services.embedding_search import EmbeddingSearch

logger = logging.getLogger(__name__)


class SemanticRanker:
    """Rerank search results by semantic relevance using embeddings."""

    def __init__(self, embedding_search: Optional[EmbeddingSearch] = None):
        self.embedding_search = embedding_search or EmbeddingSearch()

    async def rerank(
        self,
        query: str,
        chunks: list[str],
        bm25_scores: list[float],
        top_k: int = 5,
    ) -> list[tuple[str, float]]:
        """Rerank chunks using semantic similarity (embeddings) + BM25.

        Args:
            query: Search query
            chunks: Content chunks to rank
            bm25_scores: Original BM25 scores (0-100)
            top_k: Return top K results

        Returns:
            List of (chunk, combined_score) tuples sorted by score descending
        """
        if not chunks or not query:
            return []

        # Get query embedding
        query_emb = await self.embedding_search.embed(query)
        if not query_emb:
            # Fallback to BM25 if embedding fails
            return self._rank_by_bm25(chunks, bm25_scores, top_k)

        # Get chunk embeddings
        chunk_embs = await self.embedding_search.embed_batch(chunks)

        # Calculate semantic similarity scores (0-1)
        semantic_scores = [
            self.embedding_search.cosine_similarity(query_emb, emb)
            for emb in chunk_embs
        ]

        # Normalize BM25 scores to 0-1 range
        bm25_normalized = [min(s / 100.0, 1.0) for s in bm25_scores]

        # Combine: semantic 70%, BM25 30%
        combined = []
        for chunk, semantic, bm25 in zip(chunks, semantic_scores, bm25_normalized):
            score = semantic * 0.7 + bm25 * 0.3
            combined.append((chunk, score))

        return sorted(combined, key=lambda x: x[1], reverse=True)[:top_k]

    def _rank_by_bm25(
        self, chunks: list[str], bm25_scores: list[float], top_k: int
    ) -> list[tuple[str, float]]:
        """Fallback to BM25-only ranking."""
        combined = [
            (chunk, min(score / 100.0, 1.0)) for chunk, score in zip(chunks, bm25_scores)
        ]
        return sorted(combined, key=lambda x: x[1], reverse=True)[:top_k]
