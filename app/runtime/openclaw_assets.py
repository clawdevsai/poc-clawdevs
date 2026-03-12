#!/usr/bin/env python3
"""Assets de profiles, rules e skills usados no contexto do OpenClaw."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ASSETS_ROOT = Path(__file__).resolve().parents[1] / "openclaw"


@dataclass(frozen=True, slots=True)
class OpenClawRoleConfig:
    profile: str
    rules: tuple[str, ...]
    skills: tuple[str, ...]
    output_schema: str


ROLE_CONFIGS: dict[str, OpenClawRoleConfig] = {
    "PO": OpenClawRoleConfig(
        profile="po",
        rules=("core", "product_scope"),
        skills=("po_handoff", "backlog_decomposition", "acceptance_criteria", "github_issue_flow", "github_cli", "redis_streams"),
        output_schema="po",
    ),
    "Architect-draft": OpenClawRoleConfig(
        profile="architect",
        rules=("core", "solution_simplicity"),
        skills=("architect_triage", "solution_design", "architecture_review", "implementation_planning", "github_cli", "redis_streams"),
        output_schema="architect",
    ),
    "Developer": OpenClawRoleConfig(
        profile="developer",
        rules=("core", "engineering", "change_safety"),
        skills=("developer_execution", "code_delivery", "implementation_planning", "test_execution", "github_cli", "redis_streams"),
        output_schema="developer",
    ),
    "QA": OpenClawRoleConfig(
        profile="qa",
        rules=("core", "engineering", "release_integrity"),
        skills=("qa_decision", "test_execution", "architecture_review", "deploy_validation", "github_cli", "redis_streams"),
        output_schema="qa",
    ),
    "DevOps": OpenClawRoleConfig(
        profile="devops",
        rules=("core", "release_integrity"),
        skills=("devops_release_gate", "release_ops", "deploy_validation", "github_cli", "redis_streams"),
        output_schema="devops",
    ),
    "DBA": OpenClawRoleConfig(
        profile="dba",
        rules=("core", "engineering", "release_integrity"),
        skills=("dba_guard", "architecture_review", "deploy_validation", "github_cli", "redis_streams"),
        output_schema="dba",
    ),
    "CyberSec": OpenClawRoleConfig(
        profile="cybersec",
        rules=("core", "engineering", "change_safety"),
        skills=("cybersec_guard", "architecture_review", "deploy_validation", "github_cli", "redis_streams"),
        output_schema="cybersec",
    ),
    "Architect-review": OpenClawRoleConfig(
        profile="architect_review",
        rules=("core", "release_integrity", "solution_simplicity"),
        skills=("architect_final_decision", "architecture_review", "release_ops", "github_cli", "redis_streams"),
        output_schema="architect_review",
    ),
}

COMMON_TEMPLATE_ORDER: tuple[str, ...] = (
    "AGENTS.default",
    "AGENTS",
    "BOOT",
    "BOOTSTRAP",
    "HEARTBEAT",
    "IDENTITY",
    "SOUL",
    "TOOLS",
    "USER",
)


def _read_asset(kind: str, name: str) -> str:
    path = ASSETS_ROOT / kind / f"{name}.md"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


def _read_soul(profile: str) -> str:
    path = ASSETS_ROOT / "souls" / profile / "SOUL.md"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


def _read_identity(profile: str) -> str:
    return _read_asset("identities", profile)


def _read_tools_contract(profile: str) -> str:
    return _read_asset("tools", profile)


def _read_template(name: str) -> str:
    path = ASSETS_ROOT / "templates" / f"{name}.md"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


def get_role_openclaw_config(role_name: str) -> OpenClawRoleConfig | None:
    return ROLE_CONFIGS.get(role_name)


def render_openclaw_context(role_name: str, allowed_tools: tuple[str, ...] = ()) -> str:
    config = get_role_openclaw_config(role_name)
    if config is None:
        return ""

    parts = [f"OpenClaw role profile: {config.profile}"]

    template_blocks = []
    for template_name in COMMON_TEMPLATE_ORDER:
        template_text = _read_template(template_name)
        if template_text:
            template_blocks.append(f"[template:{template_name.lower()}]\n{template_text}")
    if template_blocks:
        parts.append("\n".join(template_blocks))

    profile_text = _read_asset("profiles", config.profile)
    if profile_text:
        parts.append(profile_text)

    identity_text = _read_identity(config.profile)
    if identity_text:
        parts.append(f"[identity:{config.profile}]\n{identity_text}")

    soul_text = _read_soul(config.profile)
    if soul_text:
        parts.append(f"[soul:{config.profile}]\n{soul_text}")

    rule_blocks = []
    for rule_name in config.rules:
        rule_text = _read_asset("rules", rule_name)
        if rule_text:
            rule_blocks.append(f"[rule:{rule_name}]\n{rule_text}")
    if rule_blocks:
        parts.append("\n".join(rule_blocks))

    skill_blocks = []
    for skill_name in config.skills:
        skill_text = _read_asset("skills", skill_name)
        if skill_text:
            skill_blocks.append(f"[skill:{skill_name}]\n{skill_text}")
    if skill_blocks:
        parts.append("\n".join(skill_blocks))

    if allowed_tools:
        tool_lines = ["Allowed runtime tools:"]
        tool_lines.extend(f"- {tool_name}" for tool_name in allowed_tools)
        parts.append("\n".join(tool_lines))

    tools_contract = _read_tools_contract(config.profile)
    if tools_contract:
        parts.append(f"[tools:{config.profile}]\n{tools_contract}")

    output_schema_text = _read_asset("output_schemas", config.output_schema)
    if output_schema_text:
        parts.append(f"[output_schema:{config.output_schema}]\n{output_schema_text}")

    return "\n\n".join(parts).strip()


def render_openclaw_message(role_name: str, instruction: str, allowed_tools: tuple[str, ...] = ()) -> str:
    context = render_openclaw_context(role_name, allowed_tools=allowed_tools)
    if not context:
        return instruction
    return f"{context}\n\n---\n\nTask instruction:\n\n{instruction}"
