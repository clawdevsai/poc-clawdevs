#!/usr/bin/env python3
"""Resolucao explicita de sessao OpenClaw para a stack Ollama."""
from __future__ import annotations

from dataclasses import dataclass

from .model_provider import RuntimeStackConfig, resolve_role_fallback_model, resolve_role_primary_model


@dataclass(frozen=True, slots=True)
class OpenClawSessionConfig:
    session_key: str
    provider: str
    mode: str
    model: str
    base_url: str
    fallback_model: str = ""

    def to_payload(self) -> dict[str, str]:
        return {
            "provider": self.provider,
            "mode": self.mode,
            "model": self.model,
            "baseUrl": self.base_url,
        }


def resolve_openclaw_session_config(session_key: str, stack: RuntimeStackConfig) -> OpenClawSessionConfig:
    return resolve_openclaw_session_config_for_role(session_key=session_key, stack=stack, role_name="")


def resolve_openclaw_session_config_for_role(
    session_key: str,
    stack: RuntimeStackConfig,
    role_name: str,
) -> OpenClawSessionConfig:
    model = resolve_role_primary_model(role_name, stack) if role_name else stack.ollama_model
    fallback_model = resolve_role_fallback_model(role_name) if role_name else ""
    return OpenClawSessionConfig(
        session_key=session_key,
        provider=stack.model_provider,
        mode=stack.model_mode,
        model=model,
        base_url=stack.ollama_base_url,
        fallback_model=fallback_model,
    )
