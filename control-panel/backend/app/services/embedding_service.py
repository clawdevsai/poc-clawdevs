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
Embedding Service - Generates vector embeddings using Ollama

Provides local, free embeddings using Ollama models (Mistral, etc.)
No API keys or external dependencies required.
"""

import logging
import httpx
from typing import List, Optional

logger = logging.getLogger(__name__)

# Ollama configuration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_EMBEDDING_MODEL = "mistral"  # Free model for embeddings
OLLAMA_TIMEOUT = 60.0  # seconds


class EmbeddingService:
    """Generate and manage vector embeddings using Ollama."""

    def __init__(
        self,
        base_url: str = OLLAMA_BASE_URL,
        model: str = OLLAMA_EMBEDDING_MODEL,
        timeout: float = OLLAMA_TIMEOUT,
    ):
        self.base_url = base_url
        self.model = model
        self.timeout = timeout

    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text using Ollama.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector, or None on error
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return None

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/embeddings",
                    json={
                        "model": self.model,
                        "prompt": text,
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    embedding = data.get("embedding")

                    if embedding:
                        logger.debug(
                            f"Generated embedding ({len(embedding)} dims) "
                            f"for text ({len(text)} chars)"
                        )
                        return embedding
                    else:
                        logger.warning("No embedding in response")
                        return None
                else:
                    logger.error(
                        f"Ollama API error: {response.status_code} - {response.text}"
                    )
                    return None

        except httpx.ConnectError:
            logger.error(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Ensure Ollama is running: ollama serve"
            )
            return None
        except httpx.TimeoutException:
            logger.error(f"Ollama request timed out after {self.timeout}s")
            return None
        except Exception as e:
            logger.error(f"Error generating embedding: {e}", exc_info=True)
            return None

    async def batch_embed_chunks(
        self, chunks: List[str]
    ) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple text chunks.

        Args:
            chunks: List of text chunks to embed

        Returns:
            List of embeddings (may contain None for failed chunks)
        """
        embeddings = []

        for chunk in chunks:
            embedding = await self.generate_embedding(chunk)
            embeddings.append(embedding)

        successful = sum(1 for e in embeddings if e is not None)
        logger.info(f"Generated {successful}/{len(chunks)} embeddings successfully")

        return embeddings

    def chunk_text(
        self,
        text: str,
        chunk_size: int = 512,
        overlap: int = 64,
    ) -> List[str]:
        """
        Split text into overlapping chunks for embedding.

        Args:
            text: Text to chunk
            chunk_size: Size of each chunk (in characters)
            overlap: Overlap between chunks

        Returns:
            List of text chunks
        """
        if not text:
            return []

        chunks = []
        start = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk = text[start:end]

            if chunk.strip():  # Only add non-empty chunks
                chunks.append(chunk)

            start = end - overlap if end < len(text) else end

        logger.debug(f"Chunked text ({len(text)} chars) into {len(chunks)} chunks")
        return chunks

    def cosine_similarity(
        self, embedding1: List[float], embedding2: List[float]
    ) -> float:
        """
        Calculate cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity score (0-1, where 1 = identical)
        """
        import math

        if not embedding1 or not embedding2:
            return 0.0

        if len(embedding1) != len(embedding2):
            logger.warning(
                f"Embedding dimension mismatch: {len(embedding1)} vs {len(embedding2)}"
            )
            return 0.0

        # Calculate dot product
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))

        # Calculate magnitudes
        magnitude1 = math.sqrt(sum(a * a for a in embedding1))
        magnitude2 = math.sqrt(sum(b * b for b in embedding2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        # Calculate cosine similarity
        similarity = dot_product / (magnitude1 * magnitude2)
        return max(0.0, min(1.0, similarity))  # Clamp to [0, 1]

    def get_health(self) -> bool:
        """
        Check if Ollama service is healthy and model is available.

        Returns:
            True if service is healthy, False otherwise
        """
        try:
            import requests

            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5.0,
            )

            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                model_names = [m.get("name", "") for m in models]

                if self.model in model_names:
                    logger.info(f"Ollama healthy - {self.model} available")
                    return True
                else:
                    logger.warning(
                        f"Ollama healthy but {self.model} not available. "
                        f"Available: {model_names}"
                    )
                    return False
            else:
                logger.warning(f"Ollama health check failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Cannot reach Ollama service: {e}")
            return False
