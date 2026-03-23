from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://panel:password@clawdevs-panel-db:5432/clawdevs_panel"

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

    # GitHub
    github_token: str = ""
    github_org: str = ""
    github_default_repository: str = ""

    # OpenClaw data path (PVC mounted read-only)
    openclaw_data_path: str = "/data/openclaw"

    # Kubernetes
    k8s_namespace: str = "default"

    model_config = {"env_prefix": "PANEL_", "env_file": ".env", "extra": "allow"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
