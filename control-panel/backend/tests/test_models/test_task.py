import pytest
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from sqlmodel import SQLModel, create_engine, Session
from app.models.task import Task


@pytest.fixture(scope="function")
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


class TestTaskModel:
    """Test Task model creation and validation."""

    def test_task_creation(self, db_session):
        """Test basic task creation."""
        task = Task(
            title="Test Task",
            description="A test task description",
        )
        db_session.add(task)
        db_session.commit()

        assert task.id is not None
        assert isinstance(task.id, UUID)
        assert task.title == "Test Task"
        assert task.description == "A test task description"
        assert task.status == "inbox"  # default
        assert task.priority == "medium"  # default
        assert task.created_at is not None
        assert task.updated_at is not None

    def test_task_with_all_fields(self, db_session):
        """Test task with all fields populated."""
        now = datetime.utcnow()
        agent_id = uuid4()

        task = Task(
            title="Complete Task",
            description="Complete task with all fields",
            status="in_progress",
            priority="high",
            assigned_agent_id=agent_id,
            github_issue_number=123,
            github_issue_url="https://github.com/org/repo/issues/123",
            github_repo="org/repo",
            label="back_end",
            due_at=now + timedelta(days=7),
        )
        db_session.add(task)
        db_session.commit()

        assert task.status == "in_progress"
        assert task.priority == "high"
        assert task.assigned_agent_id == agent_id
        assert task.github_issue_number == 123
        assert task.github_issue_url == "https://github.com/org/repo/issues/123"
        assert task.github_repo == "org/repo"
        assert task.label == "back_end"
        assert task.due_at == now + timedelta(days=7)

    def test_task_status_values(self, db_session):
        """Test valid status values for task."""
        valid_statuses = ["inbox", "in_progress", "review", "done"]

        for status in valid_statuses:
            task = Task(
                title=f"Task-{status}",
                description=f"Task in {status}",
                status=status,
            )
            db_session.add(task)
            db_session.commit()

            assert task.status == status

    def test_task_priority_values(self, db_session):
        """Test valid priority values for task."""
        valid_priorities = ["low", "medium", "high"]

        for priority in valid_priorities:
            task = Task(
                title=f"Task-{priority}",
                description=f"Task with {priority} priority",
                priority=priority,
            )
            db_session.add(task)
            db_session.commit()

            assert task.priority == priority

    def test_task_label_values(self, db_session):
        """Test valid label values for task."""
        valid_labels = [
            "back_end", "front_end", "mobile", "tests",
            "devops", "dba", "security", "ux"
        ]

        for label in valid_labels:
            task = Task(
                title=f"Task-{label}",
                description=f"Task with {label} label",
                label=label,
            )
            db_session.add(task)
            db_session.commit()

            assert task.label == label

    def test_task_without_description(self, db_session):
        """Test task without description (optional field)."""
        task = Task(
            title="No Description Task",
        )
        db_session.add(task)
        db_session.commit()

        assert task.description is None

    def test_task_without_due_date(self, db_session):
        """Test task without due date (optional field)."""
        task = Task(
            title="No Due Date Task",
            description="Task without due date",
        )
        db_session.add(task)
        db_session.commit()

        assert task.due_at is None

    def test_task_without_github_integration(self, db_session):
        """Test task without GitHub integration."""
        task = Task(
            title="Local Task",
            description="Task not linked to GitHub",
        )
        db_session.add(task)
        db_session.commit()

        assert task.github_issue_number is None
        assert task.github_issue_url is None
        assert task.github_repo is None

    def test_task_timestamps(self, db_session):
        """Test automatic timestamp creation."""
        task = Task(
            title="Timestamp Task",
            description="Task for timestamp testing",
        )
        db_session.add(task)
        db_session.commit()

        assert task.created_at is not None
        assert task.updated_at is not None
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)


class TestTaskStatusTransitions:
    """Test task status workflow."""

    def test_inbox_to_in_progress(self, db_session):
        """Test task move from inbox to in_progress."""
        task = Task(
            title="Workflow Task",
            description="Testing status workflow",
            status="inbox",
        )
        db_session.add(task)
        db_session.commit()

        task.status = "in_progress"
        db_session.commit()

        assert task.status == "in_progress"

    def test_in_progress_to_review(self, db_session):
        """Test task move from in_progress to review."""
        task = Task(
            title="Review Task",
            description="Needs review",
            status="in_progress",
        )
        db_session.add(task)
        db_session.commit()

        task.status = "review"
        db_session.commit()

        assert task.status == "review"

    def test_review_to_done(self, db_session):
        """Test task move from review to done."""
        task = Task(
            title="Complete Task",
            description="Done and dusted",
            status="review",
        )
        db_session.add(task)
        db_session.commit()

        task.status = "done"
        db_session.commit()

        assert task.status == "done"

    def test_done_workflow(self, db_session):
        """Test complete task workflow."""
        task = Task(
            title="Full Workflow Task",
            description="Testing complete workflow",
            status="inbox",
        )
        db_session.add(task)
        db_session.commit()

        # Follow complete workflow
        task.status = "in_progress"
        db_session.commit()
        assert task.status == "in_progress"

        task.status = "review"
        db_session.commit()
        assert task.status == "review"

        task.status = "done"
        db_session.commit()
        assert task.status == "done"


class TestTaskAssignments:
    """Test task assignment scenarios."""

    def test_task_assignment(self, db_session):
        """Test assigning task to agent."""
        agent_id = uuid4()
        task = Task(
            title="Assigned Task",
            description="Task for specific agent",
            assigned_agent_id=agent_id,
        )
        db_session.add(task)
        db_session.commit()

        assert task.assigned_agent_id == agent_id

    def test_task_unassignment(self, db_session):
        """Test unassigning task from agent."""
        agent_id = uuid4()
        task = Task(
            title="Unassigned Task",
            description="Task to be unassigned",
            assigned_agent_id=agent_id,
        )
        db_session.add(task)
        db_session.commit()

        # Unassign
        task.assigned_agent_id = None
        db_session.commit()

        assert task.assigned_agent_id is None


class TestTaskGitHubIntegration:
    """Test GitHub-related task functionality."""

    def test_task_with_github_issue(self, db_session):
        """Test task linked to GitHub issue."""
        task = Task(
            title="GitHub Task",
            description="Task from GitHub issue",
            github_issue_number=456,
            github_issue_url="https://github.com/org/repo/issues/456",
            github_repo="org/repo",
        )
        db_session.add(task)
        db_session.commit()

        assert task.github_issue_number == 456
        assert "456" in task.github_issue_url

    def test_task_github_repo_tracking(self, db_session):
        """Test tracking GitHub repository."""
        task = Task(
            title="Repo Task",
            github_repo="myorg/myrepo",
            label="back_end",
        )
        db_session.add(task)
        db_session.commit()

        assert task.github_repo == "myorg/myrepo"
