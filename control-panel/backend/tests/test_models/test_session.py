import pytest
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from sqlmodel import SQLModel, create_engine, Session
from app.models.session import Session


@pytest.fixture(scope="function")
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


class TestSessionModel:
    """Test Session model creation and validation."""

    def test_session_creation(self, db_session):
        """Test basic session creation."""
        session = Session(
            openclaw_session_id="sess-12345",
            channel_type="telegram",
        )
        db_session.add(session)
        db_session.commit()

        assert session.id is not None
        assert isinstance(session.id, UUID)
        assert session.openclaw_session_id == "sess-12345"
        assert session.channel_type == "telegram"
        assert session.status == "active"  # default
        assert session.message_count == 0  # default
        assert session.token_count == 0  # default
        assert session.created_at is not None

    def test_session_with_all_fields(self, db_session):
        """Test session with all fields populated."""
        now = datetime.utcnow()
        agent_slug = "test-agent"
        channel_peer = "123456789"

        session = Session(
            openclaw_session_id="complete-sess",
            agent_slug=agent_slug,
            channel_type="cli",
            channel_peer=channel_peer,
            status="active",
            message_count=150,
            token_count=2500,
            started_at=now,
            last_active_at=now,
        )
        db_session.add(session)
        db_session.commit()

        assert session.agent_slug == agent_slug
        assert session.channel_peer == channel_peer
        assert session.status == "active"
        assert session.message_count == 150
        assert session.token_count == 2500
        assert session.started_at == now
        assert session.last_active_at == now

    def test_session_status_values(self, db_session):
        """Test valid status values for session."""
        valid_statuses = ["active", "ended", "error"]

        for status in valid_statuses:
            session = Session(
                openclaw_session_id=f"sess-{status}",
                channel_type="cli",
                status=status,
            )
            db_session.add(session)
            db_session.commit()

            assert session.status == status

    def test_session_without_agent(self, db_session):
        """Test session without agent_slug (agent-to-agent)."""
        session = Session(
            openclaw_session_id="agent-to-agent-sess",
            channel_type="agent-to-agent",
        )
        db_session.add(session)
        db_session.commit()

        assert session.agent_slug is None

    def test_session_with_ended_status(self, db_session):
        """Test session with ended status and timestamps."""
        now = datetime.utcnow()
        ended_at = now - timedelta(hours=1)

        session = Session(
            openclaw_session_id="ended-sess",
            channel_type="cli",
            status="ended",
            started_at=now - timedelta(hours=2),
            ended_at=ended_at,
            message_count=100,
            token_count=1500,
        )
        db_session.add(session)
        db_session.commit()

        assert session.status == "ended"
        assert session.ended_at == ended_at

    def test_session_timestamps(self, db_session):
        """Test automatic timestamp creation."""
        session = Session(
            openclaw_session_id="timestamp-sess",
            channel_type="telegram",
        )
        db_session.add(session)
        db_session.commit()

        assert session.created_at is not None
        assert isinstance(session.created_at, datetime)


class TestSessionStatistics:
    """Test session statistics tracking."""

    def test_session_message_count(self, db_session):
        """Test message count increment."""
        session = Session(
            openclaw_session_id="count-sess",
            channel_type="cli",
            message_count=10,
        )
        db_session.add(session)
        db_session.commit()

        # Update count
        session.message_count += 5
        db_session.commit()

        assert session.message_count == 15

    def test_session_token_count(self, db_session):
        """Test token count tracking."""
        session = Session(
            openclaw_session_id="token-sess",
            channel_type="telegram",
            token_count=1000,
        )
        db_session.add(session)
        db_session.commit()

        # Add more tokens
        session.token_count += 500
        db_session.commit()

        assert session.token_count == 1500


class TestSessionQueries:
    """Test common session queries."""

    def test_find_by_openclaw_session_id(self, db_session):
        """Test finding session by ID."""
        session = Session(
            openclaw_session_id="findable-sess",
            channel_type="cli",
        )
        db_session.add(session)
        db_session.commit()

        # Query by ID
        found = db_session.query(Session).filter(
            Session.openclaw_session_id == "findable-sess"
        ).first()

        assert found is not None
        assert found.openclaw_session_id == "findable-sess"

    def test_find_by_agent_slug(self, db_session):
        """Test finding sessions by agent."""
        agent_slug = "test-agent"
        session = Session(
            openclaw_session_id="agent-sess",
            agent_slug=agent_slug,
            channel_type="telegram",
        )
        db_session.add(session)
        db_session.commit()

        # Query by agent
        found = db_session.query(Session).filter(
            Session.agent_slug == agent_slug
        ).first()

        assert found is not None
        assert found.agent_slug == agent_slug

    def test_find_by_status(self, db_session):
        """Test finding sessions by status."""
        session = Session(
            openclaw_session_id="status-sess",
            channel_type="cli",
            status="active",
        )
        db_session.add(session)
        db_session.commit()

        # Query by status
        found = db_session.query(Session).filter(
            Session.status == "active"
        ).first()

        assert found is not None
