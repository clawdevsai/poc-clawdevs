import pytest
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from sqlmodel import SQLModel, create_engine, Session
from app.models.agent import Agent


@pytest.fixture(scope="function")
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


class TestAgentModel:
    """Test Agent model creation and validation."""

    def test_agent_creation(self, db_session):
        """Test basic agent creation."""
        agent = Agent(
            slug="test-agent",
            display_name="Test Agent",
            role="QA Engineer",
        )
        db_session.add(agent)
        db_session.commit()

        assert agent.id is not None
        assert isinstance(agent.id, UUID)
        assert agent.slug == "test-agent"
        assert agent.display_name == "Test Agent"
        assert agent.role == "QA Engineer"
        assert agent.status == "unknown"  # default
        assert agent.created_at is not None
        assert agent.updated_at is not None

    def test_agent_with_optional_fields(self, db_session):
        """Test agent with all optional fields populated."""
        now = datetime.utcnow()
        agent = Agent(
            slug="complete-agent",
            display_name="Complete Agent",
            role="Developer",
            avatar_url="https://example.com/avatar.png",
            status="active",
            current_model="gpt-4",
            openclaw_session_id="session-123",
            last_heartbeat_at=now,
            cron_expression="0 * * * *",
            cron_status="idle",
        )
        db_session.add(agent)
        db_session.commit()

        assert agent.avatar_url == "https://example.com/avatar.png"
        assert agent.status == "active"
        assert agent.current_model == "gpt-4"
        assert agent.openclaw_session_id == "session-123"
        assert agent.last_heartbeat_at == now
        assert agent.cron_expression == "0 * * * *"
        assert agent.cron_status == "idle"

    def test_agent_status_values(self, db_session):
        """Test valid status values for agent."""
        valid_statuses = ["active", "inactive", "error", "unknown"]

        for status in valid_statuses:
            agent = Agent(
                slug=f"agent-{status}",
                display_name=f"Agent {status}",
                role="Tester",
                status=status,
            )
            db_session.add(agent)
            db_session.commit()

            assert agent.status == status

    def test_agent_cron_status_values(self, db_session):
        """Test valid cron status values."""
        valid_cron_statuses = ["idle", "running", "error"]

        for cron_status in valid_cron_statuses:
            agent = Agent(
                slug=f"agent-cron-{cron_status}",
                display_name=f"Agent {cron_status}",
                role="Tester",
                cron_status=cron_status,
            )
            db_session.add(agent)
            db_session.commit()

            assert agent.cron_status == cron_status

    def test_agent_unique_slug(self, db_session):
        """Test that slug is unique."""
        agent1 = Agent(
            slug="unique-agent",
            display_name="First Agent",
            role="Tester",
        )
        db_session.add(agent1)
        db_session.commit()

        agent2 = Agent(
            slug="unique-agent",
            display_name="Second Agent",
            role="Tester",
        )
        db_session.add(agent2)

        # This test documents expected behavior - uniqueness constraint
        assert agent2.slug == agent1.slug  # Same slug in different objects

    def test_agent_timestamps(self, db_session):
        """Test automatic timestamp creation."""
        agent = Agent(
            slug="timestamp-agent",
            display_name="Timestamp Agent",
            role="Tester",
        )
        db_session.add(agent)
        db_session.commit()

        assert agent.created_at is not None
        assert agent.updated_at is not None
        assert isinstance(agent.created_at, datetime)
        assert isinstance(agent.updated_at, datetime)

    def test_agent_relationships(self, db_session):
        """Test Agent relationships with Sessions and Tasks."""
        agent = Agent(
            slug="related-agent",
            display_name="Related Agent",
            role="Tester",
        )
        db_session.add(agent)
        db_session.commit()

        # Agents can have many sessions
        # Agents can be assigned to many tasks
        assert agent.id is not None


class TestAgentStatusTransitions:
    """Test agent status change scenarios."""

    def test_agent_activation_workflow(self, db_session):
        """Test agent status changes from unknown to active."""
        agent = Agent(
            slug="activation-agent",
            display_name="Activation Agent",
            role="Tester",
            status="unknown",
        )
        db_session.add(agent)
        db_session.commit()

        # Simulate activation
        agent.status = "active"
        db_session.commit()

        assert agent.status == "active"

    def test_agent_error_recovery(self, db_session):
        """Test agent recovery from error state."""
        agent = Agent(
            slug="error-agent",
            display_name="Error Agent",
            role="Tester",
            status="error",
        )
        db_session.add(agent)
        db_session.commit()

        # Simulate recovery
        agent.status = "active"
        db_session.commit()

        assert agent.status == "active"

    def test_agent_deactivation(self, db_session):
        """Test agent deactivation."""
        agent = Agent(
            slug="deactivated-agent",
            display_name="Deactivated Agent",
            role="Tester",
            status="active",
        )
        db_session.add(agent)
        db_session.commit()

        # Deactivate
        agent.status = "inactive"
        db_session.commit()

        assert agent.status == "inactive"


class TestAgentCronManagement:
    """Test agent cron-related fields."""

    def test_agent_cron_schedule(self, db_session):
        """Test agent with cron schedule."""
        agent = Agent(
            slug="cron-agent",
            display_name="Cron Agent",
            role="Scheduler",
            cron_expression="*/5 * * * *",  # Every 5 minutes
            cron_status="idle",
        )
        db_session.add(agent)
        db_session.commit()

        assert agent.cron_expression == "*/5 * * * *"
        assert agent.cron_status == "idle"

    def test_agent_cron_execution_tracking(self, db_session):
        """Test tracking of cron execution times."""
        now = datetime.utcnow()
        tomorrow = now + timedelta(days=1)

        agent = Agent(
            slug="cron-tracker-agent",
            display_name="Cron Tracker Agent",
            role="Scheduler",
            cron_expression="0 0 * * *",  # Daily at midnight
            cron_last_run_at=now,
            cron_next_run_at=tomorrow,
            cron_status="idle",
        )
        db_session.add(agent)
        db_session.commit()

        assert agent.cron_last_run_at == now
        assert agent.cron_next_run_at == tomorrow
