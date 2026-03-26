import pytest
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, create_engine, Session
from app.models.activity_event import ActivityEvent


@pytest.fixture(scope="function")
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


class TestActivityEventModel:
    """Test ActivityEvent model creation and validation."""

    def test_activity_event_creation(self, db_session):
        """Test basic activity event creation."""
        event = ActivityEvent(
            event_type="user_login",
        )
        db_session.add(event)
        db_session.commit()

        assert event.id is not None
        assert isinstance(event.id, UUID)
        assert event.event_type == "user_login"
        assert event.created_at is not None

    def test_activity_event_with_agent(self, db_session):
        """Test activity event linked to agent."""
        agent_id = uuid4()
        event = ActivityEvent(
            event_type="agent_start",
            agent_id=agent_id,
        )
        db_session.add(event)
        db_session.commit()

        assert event.agent_id == agent_id

    def test_activity_event_with_user(self, db_session):
        """Test activity event linked to user."""
        user_id = uuid4()
        event = ActivityEvent(
            event_type="user_created",
            user_id=user_id,
        )
        db_session.add(event)
        db_session.commit()

        assert event.user_id == user_id

    def test_activity_event_with_payload(self, db_session):
        """Test activity event with JSON payload."""
        payload = {
            "ip_address": "192.168.1.1",
            "user_agent": "Mozilla/5.0",
            "location": "New York",
        }
        event = ActivityEvent(
            event_type="api_call",
            payload=payload,
        )
        db_session.add(event)
        db_session.commit()

        assert event.payload == payload

    def test_activity_event_with_entity(self, db_session):
        """Test activity event with entity reference."""
        event = ActivityEvent(
            event_type="entity_updated",
            entity_type="task",
            entity_id="task-123",
        )
        db_session.add(event)
        db_session.commit()

        assert event.entity_type == "task"
        assert event.entity_id == "task-123"

    def test_activity_event_timestamp(self, db_session):
        """Test automatic timestamp creation."""
        event = ActivityEvent(
            event_type="test_event",
        )
        db_session.add(event)
        db_session.commit()

        assert event.created_at is not None
        assert isinstance(event.created_at, datetime)
