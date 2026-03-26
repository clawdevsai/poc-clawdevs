import pytest
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, create_engine, Session
from app.models.approval import Approval


@pytest.fixture(scope="function")
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


class TestApprovalModel:
    """Test Approval model creation and validation."""

    def test_approval_creation(self, db_session):
        """Test basic approval creation."""
        approval = Approval(
            action_type="deploy",
        )
        db_session.add(approval)
        db_session.commit()

        assert approval.id is not None
        assert isinstance(approval.id, UUID)
        assert approval.action_type == "deploy"
        assert approval.status == "pending"  # default
        assert approval.created_at is not None

    def test_approval_with_agent(self, db_session):
        """Test approval linked to agent."""
        agent_id = uuid4()
        approval = Approval(
            action_type="agent_start",
            agent_id=agent_id,
        )
        db_session.add(approval)
        db_session.commit()

        assert approval.agent_id == agent_id

    def test_approval_with_payload(self, db_session):
        """Test approval with JSON payload."""
        payload = {
            "target_environment": "production",
            "services": ["api", "worker"],
        }
        approval = Approval(
            action_type="deploy",
            payload=payload,
        )
        db_session.add(approval)
        db_session.commit()

        assert approval.payload == payload

    def test_approval_with_confidence(self, db_session):
        """Test approval with confidence score."""
        approval = Approval(
            action_type="task_complete",
            confidence=0.95,
        )
        db_session.add(approval)
        db_session.commit()

        assert approval.confidence == 0.95

    def test_approval_with_rubric_scores(self, db_session):
        """Test approval with rubric scores."""
        rubric_scores = {
            "quality": 9,
            "completeness": 8,
            "efficiency": 7,
        }
        approval = Approval(
            action_type="code_review",
            rubric_scores=rubric_scores,
        )
        db_session.add(approval)
        db_session.commit()

        assert approval.rubric_scores == rubric_scores

    def test_approval_status_values(self, db_session):
        """Test valid status values for approval."""
        valid_statuses = ["pending", "approved", "rejected"]

        for status in valid_statuses:
            approval = Approval(
                action_type=f"approval-{status}",
                status=status,
            )
            db_session.add(approval)
            db_session.commit()

            assert approval.status == status

    def test_approval_with_justification(self, db_session):
        """Test approval with justification."""
        approval = Approval(
            action_type="deploy",
            status="approved",
            justification="All tests passed and metrics look good",
        )
        db_session.add(approval)
        db_session.commit()

        assert approval.justification == "All tests passed and metrics look good"

    def test_approval_timestamp(self, db_session):
        """Test automatic timestamp creation."""
        approval = Approval(
            action_type="test_approval",
        )
        db_session.add(approval)
        db_session.commit()

        assert approval.created_at is not None
        assert isinstance(approval.created_at, datetime)


class TestApprovalWorkflow:
    """Test approval workflow transitions."""

    def test_pending_to_approved(self, db_session):
        """Test approval transition from pending to approved."""
        approval = Approval(
            action_type="task_start",
            status="pending",
        )
        db_session.add(approval)
        db_session.commit()

        approval.status = "approved"
        db_session.commit()

        assert approval.status == "approved"

    def test_pending_to_rejected(self, db_session):
        """Test approval transition from pending to rejected."""
        approval = Approval(
            action_type="task_start",
            status="pending",
        )
        db_session.add(approval)
        db_session.commit()

        approval.status = "rejected"
        db_session.commit()

        assert approval.status == "rejected"

    def test_approval_with_decider(self, db_session):
        """Test approval with decision maker."""
        user_id = uuid4()
        now = datetime.utcnow()
        
        approval = Approval(
            action_type="deploy",
            status="approved",
            decided_by_id=user_id,
            decided_at=now,
        )
        db_session.add(approval)
        db_session.commit()

        assert approval.decided_by_id == user_id
        assert approval.decided_at == now


class TestApprovalTypes:
    """Test different approval types."""

    def test_deploy_approval(self, db_session):
        """Test deployment approval."""
        approval = Approval(
            action_type="deploy",
            payload={"environment": "staging"},
            status="approved",
        )
        db_session.add(approval)
        db_session.commit()

        assert approval.action_type == "deploy"

    def test_agent_approval(self, db_session):
        """Test agent-related approval."""
        approval = Approval(
            action_type="agent_start",
            payload={"agent_slug": "test-agent"},
        )
        db_session.add(approval)
        db_session.commit()

        assert approval.action_type == "agent_start"

    def test_task_approval(self, db_session):
        """Test task-related approval."""
        approval = Approval(
            action_type="task_complete",
            payload={"task_id": "task-123"},
            status="approved",
        )
        db_session.add(approval)
        db_session.commit()

        assert approval.action_type == "task_complete"
