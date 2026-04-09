"""Task handoff contracts and validation helpers."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ValidationError


class PlanContract(BaseModel):
    task_id: str
    task_title: str
    task_description: str | None = None
    plan_steps: list[str]
    risk_notes: list[str]


class ExecuteContract(BaseModel):
    task_id: str
    plan_steps: list[str]
    actions: list[str]
    artifacts: list[str]
    evidence: list[str]
    errors: list[str]


class SelfReviewContract(BaseModel):
    task_id: str
    checks: list[str]
    issues: list[str]
    decision: Literal["pass", "rework"]


class PeerReviewContract(BaseModel):
    task_id: str
    reviewer: str
    issues: list[str]
    decision: Literal["pass", "rework"]


class ConsolidateContract(BaseModel):
    task_id: str
    summary: str
    artifacts: list[str]
    evidence: list[str]
    next_steps: list[str]


CONTRACT_MODELS: dict[str, type[BaseModel]] = {
    "plan": PlanContract,
    "execute": ExecuteContract,
    "self_review": SelfReviewContract,
    "peer_review": PeerReviewContract,
    "consolidate": ConsolidateContract,
}

CONTRACT_SCHEMAS = {
    name: model.model_json_schema() for name, model in CONTRACT_MODELS.items()
}


def _format_errors(exc: ValidationError) -> list[str]:
    try:
        return [err.get("msg", "validation_error") for err in exc.errors()]
    except Exception:
        return [str(exc)]


def validate_contract(
    contract_name: str, payload: dict
) -> tuple[bool, dict | None, list[str]]:
    model = CONTRACT_MODELS.get(contract_name)
    if model is None:
        return False, None, ["unknown_contract"]

    try:
        validated = model.model_validate(payload)
        return True, validated.model_dump(), []
    except ValidationError as exc:
        return False, None, _format_errors(exc)
