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
Unit tests for Task model - 100% mocked, no external access.
"""

from datetime import datetime, timedelta, UTC
from uuid import UUID, uuid4


class TestTaskModel:
    """Test Task model creation and validation - UNIT TESTS ONLY."""

    def test_task_creation(self):
        """Test basic task creation."""
        from app.models.task import Task

        task = Task(
            title="Test Task",
            description="A test task description",
        )

        assert task.title == "Test Task"
        assert task.description == "A test task description"
        assert task.status == "inbox"
        assert task.priority == "medium"
        assert task.id is not None
        assert isinstance(task.id, UUID)

    def test_task_with_all_fields(self):
        """Test task with all fields populated."""
        from app.models.task import Task

        now = datetime.now(UTC)

        task = Task(
            title="Complete Task",
            description="Complete task with all fields",
            status="in_progress",
            priority="high",
            assigned_agent_id=uuid4(),
            github_issue_number=123,
            github_issue_url="https://github.com/org/repo/issues/123",
            github_repo="org/repo",
            label="back_end",
            due_at=now + timedelta(days=7),
        )

        assert task.status == "in_progress"
        assert task.priority == "high"
        assert task.github_issue_number == 123
        assert task.github_issue_url == "https://github.com/org/repo/issues/123"
        assert task.github_repo == "org/repo"
        assert task.label == "back_end"
        assert task.due_at == now + timedelta(days=7)

    def test_task_status_values(self):
        """Test valid status values for task."""
        from app.models.task import Task

        valid_statuses = ["inbox", "in_progress", "review", "done"]

        for status in valid_statuses:
            task = Task(
                title=f"Task-{status}",
                description=f"Task in {status}",
                status=status,
            )
            assert task.status == status

    def test_task_priority_values(self):
        """Test valid priority values for task."""
        from app.models.task import Task

        valid_priorities = ["low", "medium", "high"]

        for priority in valid_priorities:
            task = Task(
                title=f"Task-{priority}",
                description=f"Task with {priority} priority",
                priority=priority,
            )
            assert task.priority == priority

    def test_task_label_values(self):
        """Test valid label values for task."""
        from app.models.task import Task

        valid_labels = [
            "back_end",
            "front_end",
            "mobile",
            "tests",
            "devops",
            "dba",
            "security",
            "ux",
        ]

        for label in valid_labels:
            task = Task(
                title=f"Task-{label}",
                description=f"Task with {label} label",
                label=label,
            )
            assert task.label == label

    def test_task_without_description(self):
        """Test task without description (optional field)."""
        from app.models.task import Task

        task = Task(
            title="No Description Task",
        )

        assert task.description is None

    def test_task_without_due_date(self):
        """Test task without due date (optional field)."""
        from app.models.task import Task

        task = Task(
            title="No Due Date Task",
            description="Task without due date",
        )

        assert task.due_at is None

    def test_task_without_github_integration(self):
        """Test task without GitHub integration."""
        from app.models.task import Task

        task = Task(
            title="Local Task",
            description="Task not linked to GitHub",
        )

        assert task.github_issue_number is None
        assert task.github_issue_url is None
        assert task.github_repo is None

    def test_task_timestamps(self):
        """Test automatic timestamp creation."""
        from app.models.task import Task

        task = Task(
            title="Timestamp Task",
            description="Task for timestamp testing",
        )

        assert task.created_at is not None
        assert task.updated_at is not None
        assert isinstance(task.created_at, datetime)

    def test_task_update(self):
        """Test updating task attributes."""
        from app.models.task import Task

        task = Task(
            title="Update Task",
            description="Task to update",
            status="inbox",
            priority="medium",
        )

        task.status = "in_progress"
        task.priority = "high"

        assert task.status == "in_progress"
        assert task.priority == "high"


class TestTaskStatusTransitions:
    """Test task status workflow - UNIT TESTS ONLY."""

    def test_inbox_to_in_progress(self):
        """Test task move from inbox to in_progress."""
        from app.models.task import Task

        task = Task(
            title="Workflow Task",
            description="Testing status workflow",
            status="inbox",
        )

        task.status = "in_progress"

        assert task.status == "in_progress"

    def test_in_progress_to_review(self):
        """Test task move from in_progress to review."""
        from app.models.task import Task

        task = Task(
            title="Review Task",
            description="Needs review",
            status="in_progress",
        )

        task.status = "review"

        assert task.status == "review"

    def test_review_to_done(self):
        """Test task move from review to done."""
        from app.models.task import Task

        task = Task(
            title="Complete Task",
            description="Done and dusted",
            status="review",
        )

        task.status = "done"

        assert task.status == "done"

    def test_complete_workflow(self):
        """Test complete task workflow."""
        from app.models.task import Task

        task = Task(
            title="Full Workflow Task",
            description="Testing complete workflow",
            status="inbox",
        )

        task.status = "in_progress"
        assert task.status == "in_progress"

        task.status = "review"
        assert task.status == "review"

        task.status = "done"
        assert task.status == "done"


class TestTaskAssignments:
    """Test task assignment scenarios - UNIT TESTS ONLY."""

    def test_task_assignment(self):
        """Test assigning task to agent."""
        from app.models.task import Task

        agent_id = uuid4()

        task = Task(
            title="Assigned Task",
            description="Task for specific agent",
            assigned_agent_id=agent_id,
        )

        assert task.assigned_agent_id == agent_id

    def test_task_unassignment(self):
        """Test unassigning task from agent."""
        from app.models.task import Task

        agent_id = uuid4()

        task = Task(
            title="Unassigned Task",
            description="Task to be unassigned",
            assigned_agent_id=agent_id,
        )

        task.assigned_agent_id = None

        assert task.assigned_agent_id is None


class TestTaskGitHubIntegration:
    """Test GitHub-related task functionality - UNIT TESTS ONLY."""

    def test_task_with_github_issue(self):
        """Test task linked to GitHub issue."""
        from app.models.task import Task

        task = Task(
            title="GitHub Task",
            description="Task from GitHub issue",
            github_issue_number=456,
            github_issue_url="https://github.com/org/repo/issues/456",
            github_repo="org/repo",
        )

        assert task.github_issue_number == 456
        assert "456" in task.github_issue_url

    def test_task_github_repo_tracking(self):
        """Test tracking GitHub repository."""
        from app.models.task import Task

        task = Task(
            title="Repo Task",
            github_repo="myorg/myrepo",
            label="back_end",
        )

        assert task.github_repo == "myorg/myrepo"


class TestTaskEdgeCases:
    """Test edge cases for Task model."""

    def test_task_id_is_uuid(self):
        """Test that task ID is UUID."""
        from app.models.task import Task

        task = Task(
            title="UUID Task",
            description="Task with UUID",
        )

        assert isinstance(task.id, UUID)
        assert len(str(task.id)) == 36

    def test_task_empty_fields(self):
        """Test task with empty optional fields."""
        from app.models.task import Task

        task = Task(
            title="Empty Task",
            description="",
            github_issue_url="",
            github_repo="",
        )

        assert task.description == ""
        assert task.github_issue_url == ""
        assert task.github_repo == ""

    def test_task_long_values(self):
        """Test task with long field values."""
        from app.models.task import Task

        long_text = "x" * 10000

        task = Task(
            title="Long Task",
            description=long_text,
        )

        assert len(task.description) == 10000
