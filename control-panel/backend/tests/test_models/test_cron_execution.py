import pytest
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, create_engine, Session
from app.models.cron_execution import CronExecution


@pytest.fixture(scope="function")
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


class TestCronExecutionModel:
    """Test CronExecution model creation and validation."""

    def test_cron_execution_creation(self, db_session):
        """Test basic cron execution creation."""
        now = datetime.utcnow()
        agent_id = uuid4()
        
        execution = CronExecution(
            agent_id=agent_id,
            started_at=now,
        )
        db_session.add(execution)
        db_session.commit()

        assert execution.id is not None
        assert isinstance(execution.id, UUID)
        assert execution.agent_id == agent_id
        assert execution.started_at == now
        assert execution.trigger_type == "scheduled"  # default
        assert execution.created_at is not None

    def test_cron_execution_with_trigger_type(self, db_session):
        """Test cron execution with manual trigger."""
        now = datetime.utcnow()
        agent_id = uuid4()
        
        execution = CronExecution(
            agent_id=agent_id,
            started_at=now,
            trigger_type="manual",
        )
        db_session.add(execution)
        db_session.commit()

        assert execution.trigger_type == "manual"

    def test_cron_execution_with_exit_code(self, db_session):
        """Test cron execution with exit code."""
        now = datetime.utcnow()
        agent_id = uuid4()
        
        execution = CronExecution(
            agent_id=agent_id,
            started_at=now,
            exit_code=0,
        )
        db_session.add(execution)
        db_session.commit()

        assert execution.exit_code == 0

    def test_cron_execution_with_log(self, db_session):
        """Test cron execution with log tail."""
        now = datetime.utcnow()
        agent_id = uuid4()
        log_content = "Starting execution...\nRunning task...\nDone."
        
        execution = CronExecution(
            agent_id=agent_id,
            started_at=now,
            log_tail=log_content,
        )
        db_session.add(execution)
        db_session.commit()

        assert execution.log_tail == log_content

    def test_cron_execution_with_finish_time(self, db_session):
        """Test cron execution with finish time."""
        now = datetime.utcnow()
        agent_id = uuid4()
        
        execution = CronExecution(
            agent_id=agent_id,
            started_at=now,
            finished_at=now,
            exit_code=0,
        )
        db_session.add(execution)
        db_session.commit()

        assert execution.finished_at == now
        assert execution.exit_code == 0

    def test_cron_execution_timestamp(self, db_session):
        """Test automatic timestamp creation."""
        now = datetime.utcnow()
        agent_id = uuid4()
        
        execution = CronExecution(
            agent_id=agent_id,
            started_at=now,
        )
        db_session.add(execution)
        db_session.commit()

        assert execution.created_at is not None
        assert isinstance(execution.created_at, datetime)


class TestCronExecutionScenarios:
    """Test common cron execution scenarios."""

    def test_successful_execution(self, db_session):
        """Test successful cron execution."""
        now = datetime.utcnow()
        agent_id = uuid4()
        
        execution = CronExecution(
            agent_id=agent_id,
            started_at=now,
            finished_at=now,
            exit_code=0,
            trigger_type="scheduled",
        )
        db_session.add(execution)
        db_session.commit()

        assert execution.exit_code == 0
        assert execution.trigger_type == "scheduled"

    def test_failed_execution(self, db_session):
        """Test failed cron execution."""
        now = datetime.utcnow()
        agent_id = uuid4()
        
        execution = CronExecution(
            agent_id=agent_id,
            started_at=now,
            finished_at=now,
            exit_code=1,
        )
        db_session.add(execution)
        db_session.commit()

        assert execution.exit_code == 1

    def test_manual_trigger(self, db_session):
        """Test manually triggered execution."""
        now = datetime.utcnow()
        agent_id = uuid4()
        
        execution = CronExecution(
            agent_id=agent_id,
            started_at=now,
            trigger_type="manual",
        )
        db_session.add(execution)
        db_session.commit()

        assert execution.trigger_type == "manual"

    def test_running_execution(self, db_session):
        """Test running (incomplete) cron execution."""
        now = datetime.utcnow()
        agent_id = uuid4()
        
        execution = CronExecution(
            agent_id=agent_id,
            started_at=now,
        )
        db_session.add(execution)
        db_session.commit()

        assert execution.finished_at is None
        assert execution.exit_code is None

    def test_execution_with_log(self, db_session):
        """Test execution with log output."""
        now = datetime.utcnow()
        agent_id = uuid4()
        log_output = """INFO: Starting task
INFO: Processing data
INFO: Task completed successfully"""
        
        execution = CronExecution(
            agent_id=agent_id,
            started_at=now,
            log_tail=log_output,
        )
        db_session.add(execution)
        db_session.commit()

        assert "Starting task" in execution.log_tail
        assert "Task completed successfully" in execution.log_tail


class TestCronExecutionQueries:
    """Test common cron execution queries."""

    def test_find_by_agent(self, db_session):
        """Test finding executions by agent."""
        agent_id = uuid4()
        now = datetime.utcnow()
        
        execution = CronExecution(
            agent_id=agent_id,
            started_at=now,
        )
        db_session.add(execution)
        db_session.commit()

        found = db_session.query(CronExecution).filter(
            CronExecution.agent_id == agent_id
        ).first()

        assert found is not None
        assert found.agent_id == agent_id

    def test_find_recent_executions(self, db_session):
        """Test finding recent cron executions."""
        now = datetime.utcnow()
        agent_id = uuid4()
        
        execution = CronExecution(
            agent_id=agent_id,
            started_at=now,
        )
        db_session.add(execution)
        db_session.commit()

        # Query recent executions (within last hour)
        from datetime import timedelta
        recent_cutoff = now - timedelta(hours=1)
        
        recent = db_session.query(CronExecution).filter(
            CronExecution.started_at >= recent_cutoff
        ).all()

        assert len(recent) >= 1
