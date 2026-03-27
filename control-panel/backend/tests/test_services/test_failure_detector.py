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
Unit tests for Failure Detection Service
"""

import pytest
from datetime import timedelta
from uuid import uuid4

from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from app.models.task import Task
from app.models.agent import Agent
from app.services.failure_detector import FailureDetector


@pytest.fixture
def session():
    """Create in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def sample_agents(session: Session) -> dict:
    """Create sample agents for testing."""
    arquiteto = Agent(
        slug="arquiteto",
        display_name="Arquiteto",
        role="Senior Architect",
        can_escalate=True,
        max_escalations=10,
    )
    dev_backend = Agent(
        slug="dev_backend",
        display_name="Dev Backend",
        role="Backend Developer",
        can_escalate=False,
    )
    dev_frontend = Agent(
        slug="dev_frontend",
        display_name="Dev Frontend",
        role="Frontend Developer",
        can_escalate=False,
    )
    qa_engineer = Agent(
        slug="qa_engineer",
        display_name="QA Engineer",
        role="QA Engineer",
        can_escalate=False,
    )

    session.add(arquiteto)
    session.add(dev_backend)
    session.add(dev_frontend)
    session.add(qa_engineer)
    session.commit()

    return {
        "arquiteto": arquiteto,
        "dev_backend": dev_backend,
        "dev_frontend": dev_frontend,
        "qa_engineer": qa_engineer,
    }


@pytest.fixture
def sample_task(session: Session) -> Task:
    """Create a sample task for testing."""
    task = Task(
        title="Test Task",
        description="A task for testing",
        status="in_progress",
        label="back_end",
    )
    session.add(task)
    session.commit()
    return task


class TestFailureDetector:
    """Test cases for FailureDetector service."""

    def test_record_single_failure(self, session: Session, sample_task: Task):
        """Test recording a single failure."""
        detector = FailureDetector(session)

        detector.record_failure(
            sample_task.id,
            "Connection timeout",
            "network_error",
        )

        # Refresh task from session
        session.refresh(sample_task)

        assert sample_task.failure_count == 1
        assert sample_task.consecutive_failures == 1
        assert sample_task.last_error == "Connection timeout"
        assert sample_task.error_reason == "network_error"

    def test_record_multiple_failures(self, session: Session, sample_task: Task):
        """Test recording multiple failures."""
        detector = FailureDetector(session)

        for i in range(3):
            detector.record_failure(
                sample_task.id,
                f"Error {i+1}",
                "execution_error",
            )

        session.refresh(sample_task)

        assert sample_task.failure_count == 3
        assert sample_task.consecutive_failures == 3

    def test_escalation_on_threshold(
        self,
        session: Session,
        sample_task: Task,
        sample_agents: dict,
    ):
        """Test escalation triggers on reaching threshold."""
        detector = FailureDetector(session)

        # Record 3 failures (threshold)
        for i in range(3):
            detector.record_failure(
                sample_task.id,
                f"Error {i+1}",
                "execution_error",
            )

        session.refresh(sample_task)

        # Check escalation
        assert sample_task.escalated_to_agent_id is not None
        assert sample_task.escalation_reason is not None

    def test_domain_specific_escalation(
        self,
        session: Session,
        sample_agents: dict,
    ):
        """Test domain-specific escalation routing."""
        detector = FailureDetector(session)

        # Create backend task
        backend_task = Task(
            title="Backend Task",
            label="back_end",
            status="in_progress",
        )
        session.add(backend_task)
        session.commit()

        # Record failures
        for i in range(3):
            detector.record_failure(backend_task.id, f"Error {i+1}", "execution_error")

        session.refresh(backend_task)
        session.refresh(sample_agents["dev_backend"])

        # Backend task should not escalate to dev_backend directly
        # but should escalate to arquiteto
        assert backend_task.escalated_to_agent_id == sample_agents["arquiteto"].id

    def test_reset_consecutive_failures(
        self,
        session: Session,
        sample_task: Task,
    ):
        """Test resetting consecutive failures on success."""
        detector = FailureDetector(session)

        # Record failures
        for i in range(2):
            detector.record_failure(sample_task.id, "Error", "execution_error")

        session.refresh(sample_task)
        assert sample_task.consecutive_failures == 2

        # Reset on success
        detector.reset_consecutive_failures(sample_task.id)

        session.refresh(sample_task)
        assert sample_task.consecutive_failures == 0

    def test_exponential_backoff(self, session: Session):
        """Test exponential backoff calculation."""
        detector = FailureDetector(session)

        # Test backoff delays
        delay1 = detector.apply_exponential_backoff(uuid4(), 1)
        delay2 = detector.apply_exponential_backoff(uuid4(), 2)
        delay3 = detector.apply_exponential_backoff(uuid4(), 3)

        assert delay1 == timedelta(seconds=1)
        assert delay2 == timedelta(seconds=1)  # 1.5^1 = 1.5 → int = 1
        assert delay3.total_seconds() > delay2.total_seconds()

    def test_get_task_health_healthy(
        self,
        session: Session,
        sample_task: Task,
    ):
        """Test health status for healthy task."""
        detector = FailureDetector(session)
        health = detector.get_task_health(sample_task.id)

        assert health["status"] == "healthy"
        assert health["failure_count"] == 0
        assert health["consecutive_failures"] == 0

    def test_get_task_health_unhealthy(
        self,
        session: Session,
        sample_task: Task,
    ):
        """Test health status for unhealthy task."""
        detector = FailureDetector(session)

        # Record one failure
        detector.record_failure(sample_task.id, "Error", "execution_error")

        health = detector.get_task_health(sample_task.id)

        assert health["status"] == "unhealthy"
        assert health["failure_count"] == 1

    def test_get_task_health_failed(
        self,
        session: Session,
        sample_task: Task,
        sample_agents: dict,
    ):
        """Test health status for failed task."""
        detector = FailureDetector(session)

        # Record 3 failures
        for i in range(3):
            detector.record_failure(sample_task.id, "Error", "execution_error")

        health = detector.get_task_health(sample_task.id)

        assert health["status"] == "failed"
        assert health["escalated_to_agent_id"] is not None

    def test_duplicate_escalation_prevention(
        self,
        session: Session,
        sample_task: Task,
        sample_agents: dict,
    ):
        """Test that tasks are not escalated twice."""
        detector = FailureDetector(session)

        # Record first 3 failures (triggers escalation)
        for i in range(3):
            detector.record_failure(sample_task.id, "Error", "execution_error")

        session.refresh(sample_task)
        first_escalation = sample_task.escalated_to_agent_id

        # Try to record more failures
        detector.record_failure(sample_task.id, "Another error", "execution_error")

        session.refresh(sample_task)
        second_escalation = sample_task.escalated_to_agent_id

        # Escalation should not change
        assert first_escalation == second_escalation

    def test_non_existent_task(self, session: Session):
        """Test handling of non-existent task."""
        detector = FailureDetector(session)
        non_existent_id = uuid4()

        # Should not raise exception
        detector.record_failure(non_existent_id, "Error", "execution_error")

        health = detector.get_task_health(non_existent_id)
        assert health["status"] == "unknown"
