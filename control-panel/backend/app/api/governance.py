# Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Governance API Endpoints

Policy validation, cost tracking, and compliance checking.
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import BaseModel

from app.api.deps import AdminUser
from app.core.database import get_session
from app.api.deps import CurrentUser
from app.services.governance_engine import GovernanceEngine
from app.services.cost_tracker import CostTracker

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/governance",
    tags=["governance"],
    dependencies=[Depends(require_admin)],
)


class TaskValidationRequest(BaseModel):
    title: str
    description: Optional[str] = None
    label: Optional[str] = None
    assigned_agent_id: Optional[UUID] = None


class CodeChangeRequest(BaseModel):
    agent_slug: str
    change_type: str  # auth, database, api, etc.
    affected_areas: List[str]


class MultiRepoChangeRequest(BaseModel):
    repo: str
    depends_on_repos: List[str] = []
    pr_description: str


@router.post("/validate/task-creation")
async def validate_task_creation(
    request: TaskValidationRequest,
    _: CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Validate task creation against CONSTITUTION rules.

    Returns 422 if validation fails, 200 with details if passes.

    **Example:**
    ```json
    POST /api/governance/validate/task-creation
    {
      "title": "Implement user authentication",
      "description": "Add JWT-based authentication...",
      "label": "back_end",
      "assigned_agent_id": "..."
    }
    ```
    """
    engine = GovernanceEngine(session)

    is_valid, error = await engine.validate_task_creation(request.dict())

    if not is_valid:
        raise HTTPException(status_code=422, detail=error)

    return {
        "valid": True,
        "message": "Task creation validated successfully",
        "task_data": request.dict(),
    }


@router.post("/validate/code-change")
async def validate_code_change(
    request: CodeChangeRequest,
    _: CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Validate code change against CONSTITUTION rules.

    Returns violations if any are found.

    **Example:**
    ```json
    POST /api/governance/validate/code-change
    {
      "agent_slug": "dev_backend",
      "change_type": "auth",
      "affected_areas": ["app/auth/", "app/models/user.py"]
    }
    ```
    """
    engine = GovernanceEngine(session)

    is_valid, violations = await engine.validate_code_change(
        agent_slug=request.agent_slug,
        change_type=request.change_type,
        affected_areas=request.affected_areas,
    )

    return {
        "valid": is_valid,
        "violations": violations,
        "message": (
            "Code change approved"
            if is_valid
            else f"Found {len(violations)} violation(s)"
        ),
    }


@router.post("/validate/multi-repo")
async def validate_multi_repo_change(
    request: MultiRepoChangeRequest,
    _: CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Validate multi-repo coordination.

    Ensures proper dependency ordering (shared_lib → backend → frontend → mobile).

    **Example:**
    ```json
    POST /api/governance/validate/multi-repo
    {
      "repo": "frontend",
      "depends_on_repos": ["shared_lib", "backend"],
      "pr_description": "Depends on: #123 - backend API changes"
    }
    ```
    """
    engine = GovernanceEngine(session)

    is_valid, error = await engine.validate_multi_repo_change(
        repo=request.repo,
        depends_on_repos=request.depends_on_repos,
        pr_description=request.pr_description,
    )

    if not is_valid:
        raise HTTPException(status_code=422, detail=error)

    return {
        "valid": True,
        "message": "Multi-repo change validated",
        "repo": request.repo,
        "dependencies": request.depends_on_repos,
    }


@router.post("/cost/estimate")
async def estimate_cost(
    _: CurrentUser,
    task_type: str = Query(...),
    complexity: str = Query(..., pattern="^(simple|medium|complex)$"),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Estimate cost for task before execution.

    Returns cost estimates for each tier.

    **Example:**
    ```
    POST /api/governance/cost/estimate?task_type=api_endpoint&complexity=medium
    ```
    """
    tracker = CostTracker(session)

    estimates = await tracker.estimate_task_cost(task_type, complexity)
    recommendation = await tracker.get_cost_recommendation(task_type, complexity)

    return {
        "task_type": task_type,
        "complexity": complexity,
        "cost_estimates": estimates,
        "recommendation": recommendation,
    }


@router.post("/cost/track")
async def track_cost(
    task_id: UUID,
    _: CurrentUser,
    tokens_used: int = Body(..., ge=1),
    model: str = Body(...),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Track actual cost for completed task.

    **Example:**
    ```json
    POST /api/governance/cost/track
    {
      "task_id": "...",
      "tokens_used": 5000,
      "model": "claude-3-haiku"
    }
    ```
    """
    tracker = CostTracker(session)

    await tracker.track_actual_cost(task_id, tokens_used, model)

    return {
        "task_id": str(task_id),
        "tokens": tokens_used,
        "model": model,
        "tracked": True,
    }


@router.get("/cost/budget/{agent_id}")
async def check_budget(
    agent_id: UUID,
    _: CurrentUser,
    tier: str = Query("medium", pattern="^(local|medium|premium)$"),
    session: AsyncSession = Depends(get_session),
    tier: str = Query("medium", pattern="^(local|medium|premium)$"),
) -> dict:
    """
    Check if agent has budget available for task tier.

    Returns warning if nearing budget limit.

    **Example:**
    ```
    GET /api/governance/cost/budget/{agent_id}?tier=premium
    ```
    """
    tracker = CostTracker(session)

    available, warning = await tracker.check_budget_available(agent_id, tier)

    return {
        "agent_id": str(agent_id),
        "tier": tier,
        "budget_available": available,
        "warning": warning,
    }


@router.get("/cost/spending/{agent_id}")
async def get_agent_spending(
    agent_id: UUID,
    _: CurrentUser,
    days: int = Query(30, ge=1, le=365),
    session: AsyncSession = Depends(get_session),
    days: int = Query(30, ge=1, le=365),
) -> dict:
    """
    Get agent's spending summary.

    **Example:**
    ```
    GET /api/governance/cost/spending/{agent_id}?days=30
    ```
    """
    tracker = CostTracker(session)

    spending = await tracker.get_agent_spending(agent_id, days)

    return {
        "agent_id": str(agent_id),
        "period_days": days,
        "spending": spending,
    }


@router.get("/cost/team-spending")
async def get_team_spending(
    _: CurrentUser,
    days: int = Query(30, ge=1, le=365),
    session: AsyncSession = Depends(get_session),
    days: int = Query(30, ge=1, le=365),
) -> dict:
    """
    Get team-wide spending summary.

    **Example:**
    ```
    GET /api/governance/cost/team-spending?days=30
    ```
    """
    tracker = CostTracker(session)

    spending = await tracker.get_team_spending(days)

    return {
        "period_days": days,
        "spending": spending,
    }


@router.get("/constitution/rules")
async def get_constitution_rules(_: CurrentUser) -> dict:
    """
    Get CONSTITUTION.md rules summary.

    Returns overview of governance rules.
    """
    return {
        "rules": [
            "No direct production database modification",
            "Require QA approval for backend changes",
            "Security review required for auth/crypto/secrets",
            "Exponential backoff on task failures",
            "Max 3 consecutive failures before escalation",
            "Production deployments require devops_sre or CEO",
            "Multi-repo changes must follow dependency order",
            "Cost tier must match task complexity",
        ],
        "document": "docker/base/openclaw-config/shared/CONSTITUTION.md",
    }


@router.get("/multi-repo/rules")
async def get_multi_repo_rules(_: CurrentUser) -> dict:
    """
    Get MULTI_REPO_COORDINATION.md rules.

    Returns dependency ordering and coordination rules.
    """
    return {
        "dependency_order": {
            "shared_lib": {"can_depend_on": []},
            "backend": {"can_depend_on": ["shared_lib"]},
            "frontend": {"can_depend_on": ["shared_lib", "backend"]},
            "mobile": {"can_depend_on": ["shared_lib", "backend"]},
        },
        "required_keywords": ["Depends on:", "Related to:", "Requires"],
        "document": "docker/base/openclaw-config/shared/MULTI_REPO_COORDINATION.md",
    }


@router.get("/cost-orchestration/rules")
async def get_cost_orchestration_rules(_: CurrentUser) -> dict:
    """
    Get DYNAMIC_COST_ORCHESTRATION.md rules.

    Returns cost tier recommendations by task type.
    """
    return {
        "tiers": {
            "local": {
                "models": ["ollama", "mistral"],
                "task_types": ["unit_test", "linting", "simple_task"],
                "cost": "free",
            },
            "medium": {
                "models": ["claude-3-haiku", "gpt-4-mini"],
                "task_types": ["api_endpoint", "feature", "debugging"],
                "cost": "~$0.01-0.10 per task",
            },
            "premium": {
                "models": ["claude-3-opus", "gpt-4"],
                "task_types": ["architecture", "security_audit", "complex_design"],
                "cost": "~$0.50-2.00 per task",
            },
        },
        "document": "docker/base/openclaw-config/shared/DYNAMIC_COST_ORCHESTRATION.md",
    }
