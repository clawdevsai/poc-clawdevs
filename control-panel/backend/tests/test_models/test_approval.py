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
Unit tests for Approval model - 100% mocked, no external access.
"""

from datetime import datetime, UTC
from uuid import UUID, uuid4


class TestApprovalModel:
    """Test Approval model creation and validation - UNIT TESTS ONLY."""

    def test_approval_creation(self):
        """Test basic approval creation."""
        from app.models.approval import Approval

        approval = Approval(
            action_type="deploy",
        )

        assert approval.action_type == "deploy"
        assert approval.status == "pending"
        assert approval.id is not None
        assert isinstance(approval.id, UUID)

    def test_approval_with_agent(self):
        """Test approval linked to agent."""
        from app.models.approval import Approval

        agent_id = uuid4()

        approval = Approval(
            action_type="agent_start",
            agent_id=agent_id,
        )

        assert approval.agent_id == agent_id

    def test_approval_with_payload(self):
        """Test approval with JSON payload."""
        from app.models.approval import Approval

        payload = {
            "target_environment": "production",
            "services": ["api", "worker"],
        }

        approval = Approval(
            action_type="deploy",
            payload=payload,
        )

        assert approval.payload == payload

    def test_approval_with_confidence(self):
        """Test approval with confidence score."""
        from app.models.approval import Approval

        approval = Approval(
            action_type="task_complete",
            confidence=0.95,
        )

        assert approval.confidence == 0.95

    def test_approval_with_rubric_scores(self):
        """Test approval with rubric scores."""
        from app.models.approval import Approval

        rubric_scores = {
            "quality": 9,
            "completeness": 8,
            "efficiency": 7,
        }

        approval = Approval(
            action_type="code_review",
            rubric_scores=rubric_scores,
        )

        assert approval.rubric_scores == rubric_scores

    def test_approval_status_values(self):
        """Test valid status values for approval."""
        from app.models.approval import Approval

        valid_statuses = ["pending", "approved", "rejected"]

        for status in valid_statuses:
            approval = Approval(
                action_type=f"approval-{status}",
                status=status,
            )
            assert approval.status == status

    def test_approval_with_justification(self):
        """Test approval with justification."""
        from app.models.approval import Approval

        approval = Approval(
            action_type="deploy",
            status="approved",
            justification="All tests passed and metrics look good",
        )

        assert approval.justification == "All tests passed and metrics look good"

    def test_approval_timestamp(self):
        """Test automatic timestamp creation."""
        from app.models.approval import Approval

        approval = Approval(
            action_type="test_approval",
        )

        assert approval.created_at is not None
        assert isinstance(approval.created_at, datetime)


class TestApprovalWorkflow:
    """Test approval workflow transitions - UNIT TESTS ONLY."""

    def test_pending_to_approved(self):
        """Test approval transition from pending to approved."""
        from app.models.approval import Approval

        approval = Approval(
            action_type="task_start",
            status="pending",
        )

        approval.status = "approved"

        assert approval.status == "approved"

    def test_pending_to_rejected(self):
        """Test approval transition from pending to rejected."""
        from app.models.approval import Approval

        approval = Approval(
            action_type="task_start",
            status="pending",
        )

        approval.status = "rejected"

        assert approval.status == "rejected"

    def test_approval_with_decider(self):
        """Test approval with decision maker."""
        from app.models.approval import Approval
        from datetime import datetime

        user_id = uuid4()

        approval = Approval(
            action_type="deploy",
            status="approved",
            decided_by_id=user_id,
            decided_at=datetime.now(UTC),
        )

        assert approval.decided_by_id == user_id


class TestApprovalTypes:
    """Test different approval types - UNIT TESTS ONLY."""

    def test_deploy_approval(self):
        """Test deployment approval."""
        from app.models.approval import Approval

        approval = Approval(
            action_type="deploy",
            payload={"environment": "staging"},
            status="approved",
        )

        assert approval.action_type == "deploy"

    def test_agent_approval(self):
        """Test agent-related approval."""
        from app.models.approval import Approval

        approval = Approval(
            action_type="agent_start",
            payload={"agent_slug": "test-agent"},
        )

        assert approval.action_type == "agent_start"

    def test_task_approval(self):
        """Test task-related approval."""
        from app.models.approval import Approval

        approval = Approval(
            action_type="task_complete",
            payload={"task_id": "task-123"},
            status="approved",
        )

        assert approval.action_type == "task_complete"


class TestApprovalEdgeCases:
    """Test edge cases for Approval model."""

    def test_approval_id_is_uuid(self):
        """Test that approval ID is UUID."""
        from app.models.approval import Approval

        approval = Approval(
            action_type="uuid-approval",
        )

        assert isinstance(approval.id, UUID)
        assert len(str(approval.id)) == 36

    def test_approval_empty_payload(self):
        """Test approval with empty payload."""
        from app.models.approval import Approval

        approval = Approval(
            action_type="empty-payload-approval",
            payload={},
        )

        assert approval.payload == {}

    def test_approval_none_values(self):
        """Test approval with None values."""
        from app.models.approval import Approval

        approval = Approval(
            action_type="none-values-approval",
            agent_id=None,
            payload=None,
        )

        assert approval.agent_id is None
        assert approval.payload is None

    def test_approval_large_payload(self):
        """Test approval with large payload."""
        from app.models.approval import Approval

        payload = {"key": "x" * 10000 for _ in range(100)}

        approval = Approval(
            action_type="large-payload-approval",
            payload=payload,
        )

        assert len(approval.payload) > 0
