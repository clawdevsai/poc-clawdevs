"""Semantic Optimization API endpoints for Ollama-enhanced optimization."""
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.database import get_session
from app.services.query_enhancer import QueryEnhancer
from app.services.semantic_ranker import SemanticRanker
from app.services.adaptive_compressor import AdaptiveCompressor
from app.services.summarizer import IntelligentSummarizer
from app.services.categorizer import MemoryCategorizer
from app.services.anomaly_detector import AnomalyDetector
from app.services.context_suggester import ContextSuggester
from app.services.ollama_client import OllamaClient
from app.services.semantic_optimization_flags import flags
from app.services.context_metrics import context_tracker

router = APIRouter(prefix="/api/context-mode/semantic-optimization", tags=["semantic-optimization"])

# Service instances (singleton-like)
query_enhancer = QueryEnhancer()
semantic_ranker = SemanticRanker()
adaptive_compressor = AdaptiveCompressor()
summarizer = IntelligentSummarizer()
categorizer = MemoryCategorizer()
anomaly_detector = AnomalyDetector()
context_suggester = ContextSuggester()
ollama_client = OllamaClient()


@router.post("/enhance-query")
async def enhance_query(query: str, agent_id: str):
    """Expand query with semantic variations."""
    if not query or len(query) < 2:
        raise HTTPException(status_code=400, detail="Query too short")

    if not flags.is_enabled("query_enhancement", agent_id):
        raise HTTPException(
            status_code=503,
            detail="Query enhancement feature is not enabled",
        )

    agent_context = agent_id  # Could fetch from DB
    result = await query_enhancer.enhance_query(query, agent_context)
    return result


@router.post("/rerank-results")
async def rerank_results(query: str, chunks: list[str], bm25_scores: list[float] = None):
    """Rerank chunks by semantic relevance."""
    if not chunks or not query:
        raise HTTPException(status_code=400, detail="Missing query or chunks")

    if not bm25_scores:
        bm25_scores = [0.5] * len(chunks)

    result = await semantic_ranker.rerank(query, chunks, bm25_scores, top_k=5)
    return {"reranked": [{"chunk": c[:200], "score": s} for c, s in result]}


@router.post("/classify-output")
async def classify_output(output: str, tool_name: str = ""):
    """Classify output type and select compression strategy."""
    if not output:
        raise HTTPException(status_code=400, detail="Output required")

    result = await adaptive_compressor.compress_adaptive(output, tool_name)
    return result


@router.post("/summarize")
async def summarize(content: str, intent: str = None, max_words: int = 100):
    """Summarize content intelligently."""
    if not content:
        raise HTTPException(status_code=400, detail="Content required")

    result = await summarizer.summarize(content, intent, max_words)
    return result


@router.post("/categorize")
async def categorize(content: str):
    """Auto-categorize memory chunk."""
    if not content:
        raise HTTPException(status_code=400, detail="Content required")

    result = await categorizer.categorize(content)
    return result


@router.post("/detect-anomaly")
async def detect_anomaly(output: str, tool_name: str = ""):
    """Detect anomalies in tool output."""
    if not output:
        raise HTTPException(status_code=400, detail="Output required")

    result = await anomaly_detector.detect(output, tool_name)
    return result


@router.post("/suggest-context")
async def suggest_context(tool_name: str, args: str, candidate_memories: list[dict] = None):
    """Suggest relevant memories for agent action."""
    if not tool_name:
        raise HTTPException(status_code=400, detail="Tool name required")

    if not candidate_memories:
        candidate_memories = []

    result = await context_suggester.suggest_context(tool_name, args, candidate_memories)
    return result


@router.get("/ollama-health")
async def ollama_health():
    """Check Ollama server health."""
    online = await ollama_client.health_check()
    return {
        "status": "active" if online else "unavailable",
        "model": "phi4-mini-reasoning:latest",
        "online": online,
    }


@router.get("/metrics")
async def semantic_optimization_metrics(session: AsyncSession = Depends(get_session)):
    """Get semantic optimization context metrics (compression tracking)."""
    summary = context_tracker.get_summary()
    ollama_health = await ollama_client.health_check()

    return {
        "context_compression": summary,
        "ollama_status": "active" if ollama_health else "unavailable",
        "model": "phi4-mini-reasoning:latest",
    }


@router.get("/feature-flags")
async def get_feature_flags():
    """Get all semantic optimization feature flags status."""
    return {
        "flags": flags.get_all_status(),
        "canary_agents": flags.get_canary_agents(),
    }


@router.get("/feature-flags/{task_name}")
async def check_task_enabled(task_name: str, agent_id: str = None):
    """Check if a specific task is enabled for an agent."""
    is_enabled = flags.is_enabled(task_name, agent_id)
    return {
        "task": task_name,
        "agent_id": agent_id,
        "enabled": is_enabled,
        "canary": agent_id in flags.canary_agents if agent_id else False,
    }
