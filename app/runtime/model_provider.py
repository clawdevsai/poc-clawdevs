#!/usr/bin/env python3
"""Configuracao explicita da stack de inferencia do runtime."""
from __future__ import annotations

from dataclasses import dataclass
import os
import re


DEFAULT_OLLAMA_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL_PROVIDER = "ollama"
DEFAULT_MODEL_MODE = "cloud"
DEFAULT_OLLAMA_MODEL = "qwen3-next:80b-cloud"

DEFAULT_ROLE_MODELS_PRIMARY: dict[str, str] = {
    "CEO": "qwen3.5:397b-cloud",
    "PO": "qwen3-next:80b-cloud",
    "ARCHITECT_DRAFT": "devstral-2:123b-cloud",
    "DEVELOPER": "qwen3-coder:480b-cloud",
    "QA": "gpt-oss:120b-cloud",
    "DEVOPS": "devstral-small-2:24b-cloud",
    "CRITIC": "deepseek-v3.1:671b-cloud",
    "VISUAL": "qwen3-vl:235b-instruct-cloud",
}

DEFAULT_ROLE_MODELS_FALLBACK: dict[str, str] = {
    "CEO": "qwen3-next:80b-cloud",
    "PO": "ministral-3:14b-cloud",
    "ARCHITECT_DRAFT": "qwen3.5:397b-cloud",
    "DEVELOPER": "qwen3-coder-next:cloud",
    "QA": "nemotron-3-nano:30b-cloud",
    "DEVOPS": "rnj-1:8b-cloud",
    "CRITIC": "qwen3.5:397b-cloud",
    "VISUAL": "qwen3-next:80b-cloud",
}


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True, slots=True)
class RuntimeStackConfig:
    openclaw_required: bool
    model_provider: str
    model_mode: str
    ollama_base_url: str
    ollama_model: str

    @property
    def stack_label(self) -> str:
        return f"openclaw+{self.model_provider}"


def load_runtime_stack_config() -> RuntimeStackConfig:
    return RuntimeStackConfig(
        openclaw_required=_as_bool(os.getenv("OPENCLAW_REQUIRED"), default=True),
        model_provider=(os.getenv("MODEL_PROVIDER") or DEFAULT_MODEL_PROVIDER).strip().lower(),
        model_mode=(os.getenv("MODEL_MODE") or DEFAULT_MODEL_MODE).strip().lower(),
        ollama_base_url=(os.getenv("OLLAMA_BASE_URL") or os.getenv("OLLAMA_HOST") or DEFAULT_OLLAMA_BASE_URL).strip(),
        ollama_model=(os.getenv("OLLAMA_MODEL") or DEFAULT_OLLAMA_MODEL).strip(),
    )


def validate_runtime_stack(config: RuntimeStackConfig | None = None) -> list[str]:
    cfg = config or load_runtime_stack_config()
    errors: list[str] = []

    if cfg.openclaw_required and not (os.getenv("OPENCLAW_GATEWAY_WS") or "").strip():
        errors.append("OPENCLAW_GATEWAY_WS nao definido para stack obrigatoria com OpenClaw")

    if cfg.model_provider != "ollama":
        errors.append(f"MODEL_PROVIDER invalido: {cfg.model_provider}. Esperado: ollama")

    if cfg.model_mode not in {"cloud", "local"}:
        errors.append(f"MODEL_MODE invalido: {cfg.model_mode}. Esperado: cloud ou local")

    if not cfg.ollama_base_url:
        errors.append("OLLAMA_BASE_URL/OLLAMA_HOST nao definido")

    if not cfg.ollama_model:
        errors.append("OLLAMA_MODEL nao definido")

    return errors


def normalize_role_env_key(role_name: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", role_name).strip("_").upper()
    return normalized or "GENERIC"


def resolve_role_primary_model(role_name: str, stack: RuntimeStackConfig) -> str:
    role_key = normalize_role_env_key(role_name)
    return (
        (os.getenv(f"OPENCLAW_MODEL_{role_key}_PRIMARY") or "").strip()
        or (os.getenv(f"OPENCLAW_MODEL_{role_key}") or "").strip()
        or DEFAULT_ROLE_MODELS_PRIMARY.get(role_key, "")
        or stack.ollama_model
    )


def resolve_role_fallback_model(role_name: str) -> str:
    role_key = normalize_role_env_key(role_name)
    return (
        (os.getenv(f"OPENCLAW_MODEL_{role_key}_FALLBACK") or "").strip()
        or DEFAULT_ROLE_MODELS_FALLBACK.get(role_key, "")
    )
