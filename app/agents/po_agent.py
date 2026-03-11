#!/usr/bin/env python3
"""Implementacao do papel PO sobre o runtime compartilhado."""
from __future__ import annotations

import os

from app.agents.base import AgentSettings, BaseRoleAgent
from app.runtime import AgentResult, ExecutionPolicy, PreparedRun, RunContext
from app.shared.issue_state import KEY_PREFIX


class POAgent(BaseRoleAgent):
    def __init__(self) -> None:
        self.settings = AgentSettings(
            role_name="PO",
            stream_name=os.getenv("STREAM_CMD_STRATEGY", "cmd:strategy"),
            consumer_group=os.getenv("PO_GROUP", "clawdevs"),
            consumer_name=os.getenv("POD_NAME", os.getenv("HOSTNAME", "po-1")),
            session_key=os.getenv("OPENCLAW_PO_SESSION_KEY", "agent:po:main"),
            policy=ExecutionPolicy.from_env("PO", default_block_ms=5000, default_timeout_sec=0),
        )
        self.strategy_doc_key = os.getenv("STRATEGY_DOC_KEY", f"{KEY_PREFIX}:strategy_doc")
        self.github_repo = os.getenv("GITHUB_REPO", os.getenv("GH_REPO", ""))

    def prepare(self, redis_client, ctx: RunContext) -> PreparedRun:
        return PreparedRun()

    def read_strategy(self, redis_client, key: str | None = None) -> str:
        raw = redis_client.get(key or self.strategy_doc_key)
        if raw is None:
            return ""
        if isinstance(raw, bytes):
            return raw.decode("utf-8", errors="replace")
        return str(raw)

    def build_instruction(self, redis_client, ctx: RunContext) -> str:
        payload = ctx.event
        directive = (payload.get("directive") or "").strip()
        strategy_key = (payload.get("strategy_doc_key") or "").strip() or self.strategy_doc_key
        repo = (payload.get("repo") or self.github_repo or "").strip()
        if not directive:
            directive = self.read_strategy(redis_client, strategy_key or None) or (
                "Implementar conforme documento estrategico na Memoria."
            )
        return f"""Nova diretriz estrategica (cmd:strategy). Acao: leia o documento em Memoria se necessario, quebre em Epico/Features/Stories, crie as issues no GitHub, grave em project:v1:issue:{{id}} e publique em draft.2.issue para o Arquiteto.

Diretriz: {directive[:8000]}
Repo: {repo or '(nao informado)'}
Chave estrategica no Redis: {strategy_key or self.strategy_doc_key}
"""

    def on_success(self, redis_client, ctx: RunContext, send_output: dict | str) -> AgentResult:
        return AgentResult(
            status="forwarded",
            status_code="forwarded",
            event_name="po.forwarded",
            summary=(
                f"[{self.role_name}] XACK {self.stream_name} {self.consumer_group} "
                f"{ctx.message_id} (mensagem enviada ao agente PO)"
            ),
            metadata={"run_id": ctx.run_id},
        )
