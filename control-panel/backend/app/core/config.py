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

from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = (
        "postgresql+asyncpg://panel:password@clawdevs-panel-db:5432/clawdevs_panel"
    )

    # Redis
    redis_url: str = "redis://:password@clawdevs-panel-redis:6379/0"

    # Auth
    secret_key: str = "change-me-32-chars-minimum-secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # Admin bootstrap
    admin_username: str = "admin"
    admin_password: str = "change-me"

    # OpenClaw gateway
    openclaw_gateway_url: str = "http://clawdevs-ai:18789"
    openclaw_gateway_token: str = ""

    # Ollama (panel semantic optimization + health checks)
    # In Docker the service hostname is usually `ollama`. For local `uvicorn` on the host, set
    # PANEL_OLLAMA_BASE_URL=http://localhost:11434
    ollama_base_url: str = Field(default="http://ollama:11434")
    ollama_model: str = Field(default="phi4-mini-reasoning:latest")

    # GitHub
    github_token: str = ""
    github_org: str = ""
    github_default_repository: str = ""

    # OpenClaw data path (PVC mounted read-only)
    openclaw_data_path: str = "/data/openclaw"

    # Panel chat: max total words stored per (agent, session_key) transcript (approximate count)
    chat_transcript_max_words: int = Field(default=200_000, ge=1_000, le=2_000_000)

    # Container orchestration
    container_namespace: str = "default"

    # Cost tracking - Token costs per 1M tokens for each model
    token_costs_per_model: dict[str, float] = {
        "ollama": 0.0,  # Free
        "mistral": 0.0,  # Free (ollama)
        "claude-3-haiku": 0.00025,
        "claude-3-sonnet": 0.003,
        "claude-3-opus": 0.015,
        "gpt-4-mini": 0.00015,
        "gpt-4": 0.03,
    }

    # Cost tier budgets (max monthly and per-task)
    cost_tier_budgets: dict[str, dict[str, float]] = {
        "local": {"max_monthly": 10.0, "max_per_task": 5.0},
        "medium": {"max_monthly": 100.0, "max_per_task": 50.0},
        "premium": {"max_monthly": 500.0, "max_per_task": 200.0},
    }

    # Security
    debug: bool = False
    run_db_migrations_on_startup: bool = True
    allow_schema_create_all_fallback: bool = False
    allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://clawdevs-panel-frontend:3000",
    ]

    # Health Monitor Configuration
    HEALTH_MONITOR_ENABLED: bool = Field(
        default=True,
        description="Enable health monitoring loop"
    )
    HEALTH_MONITOR_INTERVAL_SECONDS: int = Field(
        default=300,
        description="Health monitor check interval (seconds)"
    )
    HEALTH_MONITOR_STARTUP_DELAY_SECONDS: int = Field(
        default=30,
        description="Delay before first health monitor run (seconds)"
    )

    # Repair Agent Toggles
    DATABASE_HEALER_ENABLED: bool = Field(default=True)
    AGENT_REVIVER_ENABLED: bool = Field(default=True)
    QUEUE_MECHANIC_ENABLED: bool = Field(default=True)

    # Health Thresholds
    DB_CONNECTION_POOL_WARNING_PCT: int = Field(default=80)
    DB_CONNECTION_POOL_CRITICAL_PCT: int = Field(default=95)
    AGENT_HEARTBEAT_TIMEOUT_MINUTES: int = Field(default=30)
    QUEUE_CRITICAL_DEPTH: int = Field(default=100)
    QUEUE_CRITICAL_PROCESSING_RATE_MIN: int = Field(default=5)

    # Semantic Optimization Feature Flags (Week 4 - Rollout Strategy)
    SEMANTIC_OPT_QUERY_ENHANCEMENT: bool = Field(default=False)
    SEMANTIC_OPT_SEMANTIC_RERANKING: bool = Field(default=False)
    SEMANTIC_OPT_ADAPTIVE_COMPRESSION: bool = Field(default=False)
    SEMANTIC_OPT_SUMMARIZATION: bool = Field(default=False)
    SEMANTIC_OPT_CATEGORIZATION: bool = Field(default=False)
    SEMANTIC_OPT_ANOMALY_DETECTION: bool = Field(default=False)
    SEMANTIC_OPT_CONTEXT_SUGGESTION: bool = Field(default=False)

    # Canary deployment agents (comma-separated)
    SEMANTIC_OPT_CANARY_AGENTS: str = Field(default="")

    # Orchestration parallelism gate
    ORCH_PARALLELISM_ENABLED: bool = Field(default=False)
    ORCH_PARALLELISM_FORCE: bool = Field(default=False)
    ORCH_PARALLELISM_COST_THRESHOLD: float = Field(default=2.0)
    ORCH_PARALLELISM_LATENCY_THRESHOLD_SECONDS: int = Field(default=600)
    ORCH_PARALLELISM_LOOKBACK_TASKS: int = Field(default=25)
    ORCH_PARALLELISM_ADAPTIVE_ENABLED: bool = Field(default=True)
    ORCH_PARALLELISM_ADAPTIVE_MIN_SAMPLES: int = Field(default=10)
    ORCH_PARALLELISM_COST_MULTIPLIER: float = Field(default=1.2)
    ORCH_PARALLELISM_LATENCY_MULTIPLIER: float = Field(default=1.2)

    # Memory compaction thresholds
    MEMORY_COMPACTION_SIZE_THRESHOLD: int = Field(default=200_000)
    MEMORY_COMPACTION_MAX_AGE_SECONDS: int = Field(default=86_400)

    model_config = {"env_prefix": "PANEL_", "env_file": ".env", "extra": "allow"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
