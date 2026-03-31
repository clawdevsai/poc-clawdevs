from app.services.openclaw_client import (  # legacy module kept for compatibility
    NemoClawClient as LlmRuntimeClient,
    nemoclaw_client as llm_runtime_client,
)

openclaw_client = llm_runtime_client

__all__ = ["LlmRuntimeClient", "llm_runtime_client", "openclaw_client"]
