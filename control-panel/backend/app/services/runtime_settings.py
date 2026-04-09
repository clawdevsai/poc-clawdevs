"""Runtime settings read/write service with audit tracking."""

from __future__ import annotations

from datetime import datetime, UTC
from typing import Any

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import Settings
from app.models import RuntimeSetting, RuntimeSettingAudit, User


class RuntimeSettingsService:
    """Manage persisted runtime settings with confirmation rules."""

    def __init__(self, session: AsyncSession, settings: Settings):
        self.session = session
        self.settings = settings

    async def get_settings(self) -> dict:
        defaults = self._default_settings()
        overrides = await self._load_overrides()
        merged = {**defaults, **overrides}
        return merged

    async def update_settings(self, payload: dict, actor: User) -> dict:
        confirm_text = payload.get("confirm_text")

        if payload.get("model_provider") is not None or payload.get("model_name") is not None:
            if confirm_text != "CONFIRM":
                raise ValueError("model changes require confirm_text=CONFIRM")

        if payload.get("thresholds") is not None:
            if confirm_text != "CONFIRM":
                raise ValueError("threshold changes require confirm_text=CONFIRM")

        agent_updates = payload.get("agent_updates")
        if self._has_disabled_agents(agent_updates):
            if confirm_text != "DISABLE":
                raise ValueError("agent disable requires confirm_text=DISABLE")

        updates = {
            "limits": payload.get("limits"),
            "flags": payload.get("flags"),
            "model_provider": payload.get("model_provider"),
            "model_name": payload.get("model_name"),
            "agent_updates": agent_updates,
            "thresholds": payload.get("thresholds"),
        }

        for key, value in updates.items():
            if value is None:
                continue
            await self._upsert_setting(key, value, actor, confirm_text)

        await self.session.commit()
        return await self.get_settings()

    async def _load_overrides(self) -> dict:
        result = await self.session.exec(select(RuntimeSetting))
        overrides = {}
        for row in result.all():
            overrides[row.key] = row.value_json
        return overrides

    def _default_settings(self) -> dict:
        return {
            "limits": {
                "chat_transcript_max_words": self.settings.chat_transcript_max_words,
                "cost_tier_budgets": self.settings.cost_tier_budgets,
            },
            "flags": {
                "semantic_optimization": {
                    "query_enhancement": self.settings.SEMANTIC_OPT_QUERY_ENHANCEMENT,
                    "semantic_reranking": self.settings.SEMANTIC_OPT_SEMANTIC_RERANKING,
                    "adaptive_compression": self.settings.SEMANTIC_OPT_ADAPTIVE_COMPRESSION,
                    "summarization": self.settings.SEMANTIC_OPT_SUMMARIZATION,
                    "categorization": self.settings.SEMANTIC_OPT_CATEGORIZATION,
                    "anomaly_detection": self.settings.SEMANTIC_OPT_ANOMALY_DETECTION,
                    "context_suggestion": self.settings.SEMANTIC_OPT_CONTEXT_SUGGESTION,
                },
                "orchestration": {
                    "parallelism_enabled": self.settings.ORCH_PARALLELISM_ENABLED,
                    "parallelism_force": self.settings.ORCH_PARALLELISM_FORCE,
                    "adaptive_enabled": self.settings.ORCH_PARALLELISM_ADAPTIVE_ENABLED,
                },
                "repairs": {
                    "database_healer": self.settings.DATABASE_HEALER_ENABLED,
                    "agent_reviver": self.settings.AGENT_REVIVER_ENABLED,
                    "queue_mechanic": self.settings.QUEUE_MECHANIC_ENABLED,
                },
            },
            "model_provider": "ollama",
            "model_name": self.settings.ollama_model,
            "agent_updates": [],
            "thresholds": {
                "db_pool_warning_pct": self.settings.DB_CONNECTION_POOL_WARNING_PCT,
                "db_pool_critical_pct": self.settings.DB_CONNECTION_POOL_CRITICAL_PCT,
                "agent_heartbeat_timeout_minutes": self.settings.AGENT_HEARTBEAT_TIMEOUT_MINUTES,
                "queue_critical_depth": self.settings.QUEUE_CRITICAL_DEPTH,
                "queue_critical_processing_rate_min": self.settings.QUEUE_CRITICAL_PROCESSING_RATE_MIN,
                "orch_parallelism_cost_threshold": self.settings.ORCH_PARALLELISM_COST_THRESHOLD,
                "orch_parallelism_latency_threshold_seconds": self.settings.ORCH_PARALLELISM_LATENCY_THRESHOLD_SECONDS,
                "orch_parallelism_lookback_tasks": self.settings.ORCH_PARALLELISM_LOOKBACK_TASKS,
                "orch_parallelism_adaptive_min_samples": self.settings.ORCH_PARALLELISM_ADAPTIVE_MIN_SAMPLES,
                "orch_parallelism_cost_multiplier": self.settings.ORCH_PARALLELISM_COST_MULTIPLIER,
                "orch_parallelism_latency_multiplier": self.settings.ORCH_PARALLELISM_LATENCY_MULTIPLIER,
                "memory_compaction_size_threshold": self.settings.MEMORY_COMPACTION_SIZE_THRESHOLD,
                "memory_compaction_max_age_seconds": self.settings.MEMORY_COMPACTION_MAX_AGE_SECONDS,
            },
        }

    async def _upsert_setting(
        self,
        key: str,
        value: Any,
        actor: User,
        confirm_text: str | None,
    ) -> None:
        result = await self.session.exec(
            select(RuntimeSetting).where(RuntimeSetting.key == key)
        )
        existing = result.first()
        now = datetime.now(UTC).replace(tzinfo=None)
        previous_value = existing.value_json if existing else None

        if existing is None:
            existing = RuntimeSetting(
                key=key,
                value_json=value,
                updated_at=now,
                updated_by_user_id=actor.id,
            )
            self.session.add(existing)
        else:
            existing.value_json = value
            existing.updated_at = now
            existing.updated_by_user_id = actor.id
            self.session.add(existing)

        audit = RuntimeSettingAudit(
            setting_key=key,
            previous_value_json=previous_value,
            new_value_json=value,
            action="update",
            confirm_text=confirm_text,
            created_at=now,
            created_by_user_id=actor.id,
        )
        self.session.add(audit)

    def _has_disabled_agents(self, agent_updates: Any) -> bool:
        if not isinstance(agent_updates, list):
            return False
        for update in agent_updates:
            if isinstance(update, dict) and update.get("enabled") is False:
                return True
        return False
