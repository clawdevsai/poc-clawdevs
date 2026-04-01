"""Embedding-based semantic search using Ollama local embeddings."""

import aiohttp
from app.services.ollama_client import OllamaClient


class EmbeddingSearch:
    """Semantic search using nomic-embed-text embeddings."""

    def __init__(self):
        self.ollama = OllamaClient()
        self.model = "nomic-embed-text"

    async def embed(self, text: str) -> list[float]:
        """Generate embedding for text using Ollama."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.ollama.base_url}/api/embed",
                    json={"model": self.model, "input": text},
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("embeddings", [[]])[0]
                    return []
        except Exception:
            return []

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts in batch."""
        embeddings = []
        for text in texts:
            emb = await self.embed(text)
            embeddings.append(emb)
        return embeddings

    @staticmethod
    def cosine_similarity(a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between two embeddings."""
        if not a or not b:
            return 0.0

        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x ** 2 for x in a) ** 0.5
        norm_b = sum(x ** 2 for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    async def rank_by_semantic_similarity(
        self, query: str, chunks: list[str], top_k: int = 5
    ) -> list[tuple[str, float]]:
        """Rank chunks by semantic similarity to query."""
        query_emb = await self.embed(query)
        if not query_emb:
            return [(c, 0.0) for c in chunks[:top_k]]

        chunk_embs = await self.embed_batch(chunks)

        scores = [
            (chunk, self.cosine_similarity(query_emb, emb))
            for chunk, emb in zip(chunks, chunk_embs)
        ]

        # Sort by score descending and return top_k
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]
