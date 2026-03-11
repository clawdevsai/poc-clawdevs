#!/usr/bin/env python3
"""Configuracao explicita da stack de inferencia do runtime."""
from __future__ import annotations

from dataclasses import dataclass
import os


DEFAULT_OLLAMA_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL_PROVIDER = "ollama"
DEFAULT_MODEL_MODE = "cloud"


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
        ollama_model=(os.getenv("OLLAMA_MODEL") or "").strip(),
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
