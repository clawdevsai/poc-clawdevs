import pytest
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from sqlmodel import SQLModel, create_engine, Session
from app.models.metric import Metric


@pytest.fixture(scope="function")
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


class TestMetricModel:
    """Test Metric model creation and validation."""

    def test_metric_creation(self, db_session):
        """Test basic metric creation."""
        now = datetime.utcnow()
        period_end = now + timedelta(hours=1)
        
        metric = Metric(
            metric_type="tokens_used",
            value=1000.0,
            period_start=now,
            period_end=period_end,
        )
        db_session.add(metric)
        db_session.commit()

        assert metric.id is not None
        assert isinstance(metric.id, UUID)
        assert metric.metric_type == "tokens_used"
        assert metric.value == 1000.0
        assert metric.created_at is not None

    def test_metric_with_agent(self, db_session):
        """Test metric linked to agent."""
        agent_id = uuid4()
        now = datetime.utcnow()
        period_end = now + timedelta(hours=1)
        
        metric = Metric(
            agent_id=agent_id,
            metric_type="tasks_completed",
            value=5.0,
            period_start=now,
            period_end=period_end,
        )
        db_session.add(metric)
        db_session.commit()

        assert metric.agent_id == agent_id

    def test_metric_type_values(self, db_session):
        """Test valid metric_type values."""
        valid_types = ["tokens_used", "tasks_completed", "approvals_issued", "errors"]

        for metric_type in valid_types:
            now = datetime.utcnow()
            period_end = now + timedelta(hours=1)
            
            metric = Metric(
                metric_type=metric_type,
                value=1.0,
                period_start=now,
                period_end=period_end,
            )
            db_session.add(metric)
            db_session.commit()

            assert metric.metric_type == metric_type

    def test_metric_value_variations(self, db_session):
        """Test metric value variations (integers and decimals)."""
        now = datetime.utcnow()
        period_end = now + timedelta(hours=1)

        # Integer value
        metric1 = Metric(
            metric_type="tasks_completed",
            value=10.0,
            period_start=now,
            period_end=period_end,
        )
        db_session.add(metric1)
        db_session.commit()

        # Decimal value
        metric2 = Metric(
            metric_type="tokens_used",
            value=1234.56,
            period_start=now,
            period_end=period_end,
        )
        db_session.add(metric2)
        db_session.commit()

        assert metric1.value == 10.0
        assert metric2.value == 1234.56

    def test_metric_period_tracking(self, db_session):
        """Test metric period tracking."""
        now = datetime.utcnow()
        period_end = now + timedelta(hours=1)
        
        metric = Metric(
            metric_type="tokens_used",
            value=100.0,
            period_start=now,
            period_end=period_end,
        )
        db_session.add(metric)
        db_session.commit()

        assert metric.period_start == now
        assert metric.period_end == period_end

    def test_metric_timestamp(self, db_session):
        """Test automatic timestamp creation."""
        now = datetime.utcnow()
        period_end = now + timedelta(hours=1)
        
        metric = Metric(
            metric_type="errors",
            value=0.0,
            period_start=now,
            period_end=period_end,
        )
        db_session.add(metric)
        db_session.commit()

        assert metric.created_at is not None
        assert isinstance(metric.created_at, datetime)


class TestMetricScenarios:
    """Test common metric scenarios."""

    def test_tokens_used_metric(self, db_session):
        """Test tokens used tracking."""
        now = datetime.utcnow()
        period_end = now + timedelta(hours=1)
        
        metric = Metric(
            metric_type="tokens_used",
            value=2500.0,
            period_start=now,
            period_end=period_end,
        )
        db_session.add(metric)
        db_session.commit()

        assert metric.metric_type == "tokens_used"
        assert metric.value == 2500.0

    def test_tasks_completed_metric(self, db_session):
        """Test tasks completed tracking."""
        now = datetime.utcnow()
        period_end = now + timedelta(hours=1)
        
        metric = Metric(
            metric_type="tasks_completed",
            value=15.0,
            period_start=now,
            period_end=period_end,
        )
        db_session.add(metric)
        db_session.commit()

        assert metric.metric_type == "tasks_completed"
        assert metric.value == 15.0

    def test_approvals_issued_metric(self, db_session):
        """Test approvals issued tracking."""
        now = datetime.utcnow()
        period_end = now + timedelta(hours=1)
        
        metric = Metric(
            metric_type="approvals_issued",
            value=8.0,
            period_start=now,
            period_end=period_end,
        )
        db_session.add(metric)
        db_session.commit()

        assert metric.metric_type == "approvals_issued"
        assert metric.value == 8.0

    def test_errors_metric(self, db_session):
        """Test errors tracking."""
        now = datetime.utcnow()
        period_end = now + timedelta(hours=1)
        
        metric = Metric(
            metric_type="errors",
            value=2.0,
            period_start=now,
            period_end=period_end,
        )
        db_session.add(metric)
        db_session.commit()

        assert metric.metric_type == "errors"
        assert metric.value == 2.0
