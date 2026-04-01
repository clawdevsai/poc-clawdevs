"""Test embedding search with Ollama."""

import pytest
from unittest.mock import AsyncMock, patch

from app.services.embedding_search import EmbeddingSearch


@pytest.mark.asyncio
class TestEmbeddingSearch:
    """Test semantic search using Ollama embeddings."""

    async def test_cosine_similarity(self):
        """Test cosine similarity calculation."""
        search = EmbeddingSearch()

        # Perfect similarity
        assert search.cosine_similarity([1, 0, 0], [1, 0, 0]) == pytest.approx(1.0)

        # Orthogonal
        assert search.cosine_similarity([1, 0, 0], [0, 1, 0]) == pytest.approx(0.0)

        # Opposite
        assert search.cosine_similarity([1, 0, 0], [-1, 0, 0]) == pytest.approx(-1.0)

    async def test_cosine_similarity_empty(self):
        """Test with empty embeddings."""
        search = EmbeddingSearch()
        assert search.cosine_similarity([], [1, 2, 3]) == 0.0
        assert search.cosine_similarity([1, 2, 3], []) == 0.0

    @pytest.mark.asyncio
    async def test_embed_success(self):
        """Test successful embedding."""
        search = EmbeddingSearch()

        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(
                return_value={"embeddings": [[0.1, 0.2, 0.3]]}
            )
            mock_post.return_value.__aenter__.return_value = mock_response

            result = await search.embed("test query")
            assert result == [0.1, 0.2, 0.3]

    @pytest.mark.asyncio
    async def test_embed_failure(self):
        """Test embedding failure falls back to empty."""
        search = EmbeddingSearch()

        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 500
            mock_post.return_value.__aenter__.return_value = mock_response

            result = await search.embed("test query")
            assert result == []

    @pytest.mark.asyncio
    async def test_rank_by_semantic_similarity(self):
        """Test ranking chunks by semantic similarity."""
        search = EmbeddingSearch()

        with patch.object(search, "embed") as mock_embed:
            with patch.object(search, "embed_batch") as mock_batch:
                # Query embedding
                mock_embed.return_value = [1.0, 0.0, 0.0]

                # Chunk embeddings (first chunk most similar)
                mock_batch.return_value = [
                    [0.9, 0.1, 0.0],  # High similarity
                    [0.1, 0.9, 0.0],  # Low similarity
                    [0.0, 0.0, 1.0],  # No similarity
                ]

                chunks = ["relevant", "less relevant", "irrelevant"]
                ranked = await search.rank_by_semantic_similarity("query", chunks, top_k=2)

                assert len(ranked) == 2
                assert ranked[0][0] == "relevant"
                assert ranked[1][0] == "less relevant"
