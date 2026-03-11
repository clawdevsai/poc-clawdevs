#!/usr/bin/env python3
"""Politicas de execucao compartilhadas pelos workers."""
from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True, slots=True)
class ExecutionPolicy:
    block_ms: int = 5000
    timeout_sec: int = 0
    max_attempts: int = 1
    max_runtime_sec: int | None = None
    max_cost: float | None = None

    @classmethod
    def from_env(
        cls,
        prefix: str,
        *,
        default_block_ms: int = 5000,
        default_timeout_sec: int = 0,
        default_max_attempts: int = 1,
        default_max_runtime_sec: int | None = None,
        default_max_cost: float | None = None,
    ) -> "ExecutionPolicy":
        max_cost_raw = os.getenv(f"{prefix}_MAX_COST")
        max_runtime_raw = os.getenv(f"{prefix}_MAX_RUNTIME_SEC")
        max_cost = default_max_cost if max_cost_raw is None else float(max_cost_raw)
        max_runtime_sec = default_max_runtime_sec if max_runtime_raw is None else int(max_runtime_raw)
        return cls(
            block_ms=int(os.getenv(f"{prefix}_BLOCK_MS", str(default_block_ms))),
            timeout_sec=int(os.getenv(f"{prefix}_TIMEOUT_SEC", str(default_timeout_sec))),
            max_attempts=int(os.getenv(f"{prefix}_MAX_ATTEMPTS", str(default_max_attempts))),
            max_runtime_sec=max_runtime_sec,
            max_cost=max_cost,
        )
