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
Governance Engine - Validates agent actions against policies

Enforces:
- CONSTITUTION.md rules (security, design patterns)
- DYNAMIC_COST_ORCHESTRATION.md (cost tiers)
- MULTI_REPO_COORDINATION.md (PR dependencies)
"""

import logging
import re
from typing import Optional, List, Tuple
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.task import Task
from app.models.agent import Agent
from app.models.constants import VALID_TASK_LABELS, normalize_label, is_valid_label

logger = logging.getLogger(__name__)


class GovernanceEngine:
    """Validates agent actions against CONSTITUTION and policies."""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.constitution_rules = self._load_constitution_rules()
        self.cost_tiers = self._load_cost_tiers()
        self.multi_repo_rules = self._load_multi_repo_rules()

    async def validate_task_creation(
        self, task_data: dict
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate task creation against CONSTITUTION rules.

        Args:
            task_data: Dictionary with title, description, label, assigned_agent_id

        Returns:
            (is_valid, error_message)
        """
        # Validate title
        if not task_data.get("title") or len(task_data["title"]) < 5:
            return False, "Task title too short (min 5 chars)"

        if len(task_data.get("title", "")) > 200:
            return False, "Task title too long (max 200 chars)"

        # Validate description
        description = task_data.get("description", "")
        if description and len(description) > 5000:
            return False, "Task description too long (max 5000 chars)"

        # Validate label (matches agent domain)
        label = task_data.get("label")
        if label and not self._is_valid_label(label):
            return False, f"Invalid label: {label}"

        # Check security constraints
        security_issues = self._check_security_constraints(task_data)
        if security_issues:
            return False, f"Security constraint violated: {security_issues[0]}"

        # Check design pattern compliance
        design_issues = self._check_design_patterns(task_data)
        if design_issues:
            return False, f"Design pattern violation: {design_issues[0]}"

        return True, None

    async def validate_code_change(
        self,
        agent_slug: str,
        change_type: str,
        affected_areas: List[str],
    ) -> Tuple[bool, List[str]]:
        """
        Validate code changes against CONSTITUTION rules.

        Args:
            agent_slug: Which agent is making the change
            change_type: Type of change (auth, database, api, etc.)
            affected_areas: Which parts of codebase are affected

        Returns:
            (is_valid, list_of_violations)
        """
        violations = []

        # Check role-based restrictions
        if change_type == "auth" and agent_slug not in [
            "security_engineer",
            "dev_backend",
        ]:
            violations.append(
                f"Only security_engineer or dev_backend can modify authentication (not {agent_slug})"
            )

        if change_type == "database" and agent_slug not in [
            "dba_data_engineer",
            "dev_backend",
        ]:
            violations.append(
                f"Only dba_data_engineer or dev_backend can modify database (not {agent_slug})"
            )

        if change_type == "security" and agent_slug != "security_engineer":
            violations.append(
                f"Security changes require security_engineer approval (not {agent_slug})"
            )

        # Check affected areas for production protection
        if any("production" in area.lower() for area in affected_areas):
            if agent_slug != "devops_sre" and agent_slug != "ceo":
                violations.append(
                    "Production changes require devops_sre or CEO approval"
                )

        # Check for direct DB modification (forbidden)
        if any(
            "raw sql" in area.lower() or "direct query" in area.lower()
            for area in affected_areas
        ):
            violations.append("Direct SQL queries forbidden. Use ORM or migrations.")

        return len(violations) == 0, violations

    async def validate_multi_repo_change(
        self,
        repo: str,
        depends_on_repos: List[str],
        pr_description: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate multi-repo coordination.

        Args:
            repo: Repository being modified (shared_lib, backend, frontend, mobile)
            depends_on_repos: Repos this depends on
            pr_description: PR description text

        Returns:
            (is_valid, error_message)
        """
        # Check dependency order
        valid_order = {
            "shared_lib": [],
            "back_end": ["shared_lib"],
            "front_end": ["shared_lib", "back_end"],
            "mobile": ["shared_lib", "back_end"],
        }

        if repo in valid_order:
            allowed_deps = valid_order[repo]
            invalid_deps = [d for d in depends_on_repos if d not in allowed_deps]
            if invalid_deps:
                return (
                    False,
                    f"Invalid dependencies for {repo}: {invalid_deps}. "
                    f"Allowed: {allowed_deps}",
                )

        # Check PR description has dependency keywords
        if depends_on_repos and not any(
            keyword in pr_description.lower()
            for keyword in ["depends on", "related to", "requires"]
        ):
            return (
                False,
                "PR description must mention dependencies using 'Depends on:', 'Related to:', etc.",
            )

        return True, None

    async def enforce_constitution_rules(
        self,
        agent_slug: str,
        action: str,
        context: dict,
    ) -> Tuple[bool, Optional[str]]:
        """
        Enforce CONSTITUTION.md rules.

        Args:
            agent_slug: Agent performing action
            action: Action being taken (create_task, modify_code, deploy, etc.)
            context: Context about the action

        Returns:
            (is_allowed, reason_if_blocked)
        """
        # Self-healing rules
        if action == "escalate_task":
            agent_result = await self.db_session.exec(
                select(Agent).where(Agent.slug == agent_slug)
            )
            agent = agent_result.first()
            if agent and not agent.can_escalate:
                return False, f"Agent {agent_slug} cannot escalate tasks"

        # Exponential backoff enforcement
        if action == "retry_task":
            task_id = context.get("task_id")
            if task_id:
                task_result = await self.db_session.exec(
                    select(Task).where(Task.id == task_id)
                )
                task = task_result.first()
                if task and task.consecutive_failures >= 3:
                    return (
                        False,
                        "Task must be escalated after 3 failures. Cannot retry directly.",
                    )

        # Approval requirements
        if action == "deploy_to_production":
            required_approvers = ["devops_sre", "ceo"]
            if agent_slug not in required_approvers:
                return False, f"Production deployment requires {required_approvers}"

        return True, None

    def _load_constitution_rules(self) -> dict:
        """Load CONSTITUTION.md rules."""
        return {
            "no_production_direct_modification": True,
            "require_qa_approval": True,
            "security_review_required": ["auth", "crypto", "secrets"],
            "exponential_backoff_on_failures": True,
            "max_consecutive_failures": 3,
            "escalate_on_threshold": True,
        }

    def _load_cost_tiers(self) -> dict:
        """Load DYNAMIC_COST_ORCHESTRATION tiers."""
        return {
            "local": {
                "models": ["ollama", "mistral"],
                "task_types": ["unit_test", "linting", "simple_task"],
                "max_tokens": 4000,
            },
            "medium": {
                "models": ["claude-3-haiku", "gpt-4-mini"],
                "task_types": ["api_endpoint", "feature", "debugging"],
                "max_tokens": 100000,
            },
            "premium": {
                "models": ["claude-3-opus", "gpt-4"],
                "task_types": ["architecture", "security_audit", "complex_design"],
                "max_tokens": 200000,
            },
        }

    def _load_multi_repo_rules(self) -> dict:
        """Load MULTI_REPO_COORDINATION rules."""
        return {
            "shared_lib": {"can_depend_on": []},
            "back_end": {"can_depend_on": ["shared_lib"]},
            "front_end": {"can_depend_on": ["shared_lib", "back_end"]},
            "mobile": {"can_depend_on": ["shared_lib", "back_end"]},
        }

    def _is_valid_label(self, label: str) -> bool:
        """Check if task label is valid."""
        return is_valid_label(label)

    def _check_security_constraints(self, task_data: dict) -> List[str]:
        """Check for security constraint violations."""
        issues = []
        description = (task_data.get("description") or "").lower()

        # Forbidden patterns
        forbidden_patterns = [
            (r"password.*hardcoded", "Hardcoded passwords not allowed"),
            (r"sql.*injection", "SQL injection vulnerability cannot be task"),
            (r"xss.*attack", "XSS vulnerability cannot be task"),
        ]

        for pattern, issue in forbidden_patterns:
            if re.search(pattern, description):
                issues.append(issue)

        return issues

    def _check_design_patterns(self, task_data: dict) -> List[str]:
        """Check for design pattern compliance."""
        issues = []
        description = (task_data.get("description") or "").lower()

        # Check for anti-patterns mentioned in task
        anti_patterns = [
            (r"god object", "God objects violate SOLID"),
            (r"circular import", "Circular imports create tight coupling"),
            (r"monolithic", "Monolithic design should be refactored"),
        ]

        for pattern, issue in anti_patterns:
            if re.search(pattern, description):
                issues.append(issue)

        return issues

    def suggest_cost_tier(self, task_type: str, complexity: str) -> str:
        """
        Suggest appropriate cost tier for a task.

        Args:
            task_type: Type of task (unit_test, api_endpoint, etc.)
            complexity: Estimated complexity (simple, medium, complex)

        Returns:
            Suggested tier (local, medium, premium)
        """
        # Simple heuristic mapping
        if task_type in ["unit_test", "linting", "simple_task"]:
            return "local"
        elif task_type in ["api_endpoint", "feature", "debugging"]:
            if complexity == "simple":
                return "local"
            return "medium"
        else:  # architecture, security_audit, complex_design
            return "premium"

    async def audit_action(
        self,
        agent_id: UUID,
        action: str,
        resource: str,
        allowed: bool,
        reason: Optional[str] = None,
    ) -> None:
        """
        Log action audit trail.

        Args:
            agent_id: Agent performing action
            action: Action taken
            resource: Resource affected
            allowed: Whether action was allowed
            reason: Reason for decision
        """
        from datetime import datetime, timezone

        audit_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent_id": str(agent_id),
            "action": action,
            "resource": resource,
            "allowed": allowed,
            "reason": reason,
        }

        logger.info(f"Audit: {audit_entry}")
        # TODO: Store in database audit_logs table
