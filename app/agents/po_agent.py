#!/usr/bin/env python3
"""Implementacao do papel PO sobre o runtime compartilhado."""
from __future__ import annotations

import json
import os

from app.agents.base import AgentSettings, BaseRoleAgent
from app.runtime import AgentResult, ExecutionPolicy, PreparedRun, RunContext
from app.runtime.openclaw_output import normalize_openclaw_output
from app.shared.issue_state import KEY_PREFIX, STATE_REFINAMENTO, set_issue_state


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
        self.github_repo = os.getenv("GITHUB_REPO", "")
        self.stream_draft_issue = os.getenv("STREAM_DRAFT_ISSUE", "draft.2.issue")

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
        normalized = normalize_openclaw_output(send_output)
        issues = normalized.get("issues") if isinstance(normalized, dict) else None
        published = 0
        if isinstance(issues, list):
            for index, issue in enumerate(issues, start=1):
                if not isinstance(issue, dict):
                    continue
                child_issue_id = str(issue.get("issue_id") or f"{ctx.issue_id}-{index}")
                title = str(issue.get("title") or f"{ctx.issue_id} item {index}")
                summary = str(issue.get("acceptance") or issue.get("summary") or normalized.get("summary") or "")
                priority = str(issue.get("priority") or "1")
                redis_client.set(
                    f"{KEY_PREFIX}:issue:{child_issue_id}",
                    json.dumps(
                        {
                            "parent_issue_id": ctx.issue_id,
                            "title": title,
                            "summary": summary,
                            "priority": priority,
                        },
                        ensure_ascii=False,
                    ),
                )
                set_issue_state(redis_client, child_issue_id, STATE_REFINAMENTO)
                redis_client.xadd(
                    self.stream_draft_issue,
                    {
                        "issue_id": child_issue_id,
                        "parent_issue_id": ctx.issue_id or "",
                        "title": title,
                        "summary": summary,
                        "priority": priority,
                        "run_id": ctx.run_id,
                        "trace_id": ctx.trace_id,
                        "source": "po-output",
                    },
                )
                published += 1
            if ctx.issue_id:
                set_issue_state(redis_client, ctx.issue_id, STATE_REFINAMENTO)
        status_code = "forwarded"
        event_name = "po.forwarded"
        summary_suffix = "mensagem enviada ao agente PO"
        if published > 0:
            status_code = "po_published_draft_issue"
            event_name = "po.published_draft_issue"
            summary_suffix = f"{published} issue(s) publicada(s) em {self.stream_draft_issue}"
        return AgentResult(
            status="forwarded",
            status_code=status_code,
            event_name=event_name,
            summary=(
                f"[{self.role_name}] XACK {self.stream_name} {self.consumer_group} "
                f"{ctx.message_id} ({summary_suffix})"
            ),
            metadata={"run_id": ctx.run_id, "published_count": published},
        )
