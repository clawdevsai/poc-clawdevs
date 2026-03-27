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
Unit tests for CronExecution model - 100% mocked, no external access.
"""

from datetime import datetime
from uuid import UUID, uuid4


class TestCronExecutionModel:
    """Test CronExecution model creation and validation - UNIT TESTS ONLY."""

    def test_cron_execution_creation(self):
        """Test basic cron execution creation."""
        from app.models.cron_execution import CronExecution
        
        now = datetime.utcnow()
        agent_id = uuid4()
        
        execution = CronExecution(
            agent_id=agent_id,
            started_at=now,
        )
        
        assert execution.agent_id == agent_id
        assert execution.started_at == now
        assert execution.trigger_type == "scheduled"
        assert execution.id is not None
        assert isinstance(execution.id, UUID)

    def test_cron_execution_with_trigger_type(self):
        """Test cron execution with manual trigger."""
        from app.models.cron_execution import CronExecution
        
        now = datetime.utcnow()
        agent_id = uuid4()
        
        execution = CronExecution(
            agent_id=agent_id,
            started_at=now,
            trigger_type="manual",
        )
        
        assert execution.trigger_type == "manual"

    def test_cron_execution_with_exit_code(self):
        """Test cron execution with exit code."""
        from app.models.cron_execution import CronExecution
        
        now = datetime.utcnow()
        agent_id = uuid4()
        
        execution = CronExecution(
            agent_id=agent_id,
            started_at=now,
            exit_code=0,
        )
        
        assert execution.exit_code == 0

    def test_cron_execution_with_log(self):
        """Test cron execution with log tail."""
        from app.models.cron_execution import CronExecution
        
        now = datetime.utcnow()
        agent_id = uuid4()
        log_content = "Starting execution...\nRunning task...\nDone."
        
        execution = CronExecution(
            agent_id=agent_id,
            started_at=now,
            log_tail=log_content,
        )
        
        assert execution.log_tail == log_content

    def test_cron_execution_with_finish_time(self):
        """Test cron execution with finish time."""
        from app.models.cron_execution import CronExecution
        
        now = datetime.utcnow()
        agent_id = uuid4()
        
        execution = CronExecution(
            agent_id=agent_id,
            started_at=now,
            finished_at=now,
            exit_code=0,
        )
        
        assert execution.finished_at == now
        assert execution.exit_code == 0

    def test_cron_execution_timestamp(self):
        """Test automatic timestamp creation."""
        from app.models.cron_execution import CronExecution
        
        now = datetime.utcnow()
        agent_id = uuid4()
        
        execution = CronExecution(
            agent_id=agent_id,
            started_at=now,
        )
        
        assert execution.created_at is not None
        assert isinstance(execution.created_at, datetime)


class TestCronExecutionScenarios:
    """Test common cron execution scenarios - UNIT TESTS ONLY."""

    def test_successful_execution(self):
        """Test successful cron execution."""
        from app.models.cron_execution import CronExecution
        
        now = datetime.utcnow()
        agent_id = uuid4()
        
        execution = CronExecution(
            agent_id=agent_id,
            started_at=now,
            finished_at=now,
            exit_code=0,
            trigger_type="scheduled",
        )
        
        assert execution.exit_code == 0
        assert execution.trigger_type == "scheduled"

    def test_failed_execution(self):
        """Test failed cron execution."""
        from app.models.cron_execution import CronExecution
        
        now = datetime.utcnow()
        agent_id = uuid4()
        
        execution = CronExecution(
            agent_id=agent_id,
            started_at=now,
            finished_at=now,
            exit_code=1,
        )
        
        assert execution.exit_code == 1

    def test_manual_trigger(self):
        """Test manually triggered execution."""
        from app.models.cron_execution import CronExecution
        
        now = datetime.utcnow()
        agent_id = uuid4()
        
        execution = CronExecution(
            agent_id=agent_id,
            started_at=now,
            trigger_type="manual",
        )
        
        assert execution.trigger_type == "manual"

    def test_running_execution(self):
        """Test running (incomplete) cron execution."""
        from app.models.cron_execution import CronExecution
        
        now = datetime.utcnow()
        agent_id = uuid4()
        
        execution = CronExecution(
            agent_id=agent_id,
            started_at=now,
        )
        
        assert execution.finished_at is None
        assert execution.exit_code is None

    def test_execution_with_log(self):
        """Test execution with log output."""
        from app.models.cron_execution import CronExecution
        
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
        
        assert "Starting task" in execution.log_tail
        assert "Task completed successfully" in execution.log_tail


class TestCronExecutionEdgeCases:
    """Test edge cases for CronExecution model."""

    def test_execution_id_is_uuid(self):
        """Test that execution ID is UUID."""
        from app.models.cron_execution import CronExecution
        
        now = datetime.utcnow()
        agent_id = uuid4()
        
        execution = CronExecution(
            agent_id=agent_id,
            started_at=now,
        )
        
        assert isinstance(execution.id, UUID)
        assert len(str(execution.id)) == 36

    def test_execution_zero_values(self):
        """Test cron execution with zero values."""
        from app.models.cron_execution import CronExecution
        
        now = datetime.utcnow()
        agent_id = uuid4()
        
        execution = CronExecution(
            agent_id=agent_id,
            started_at=now,
            exit_code=0,
        )
        
        assert execution.exit_code == 0

    def test_execution_none_values(self):
        """Test cron execution with None values."""
        from app.models.cron_execution import CronExecution
        
        now = datetime.utcnow()
        agent_id = uuid4()
        
        execution = CronExecution(
            agent_id=agent_id,
            started_at=now,
            finished_at=None,
            exit_code=None,
            log_tail=None,
        )
        
        assert execution.finished_at is None
        assert execution.exit_code is None
        assert execution.log_tail is None

    def test_execution_large_log(self):
        """Test execution with large log output."""
        from app.models.cron_execution import CronExecution
        
        now = datetime.utcnow()
        agent_id = uuid4()
        log_output = "x" * 100000
        
        execution = CronExecution(
            agent_id=agent_id,
            started_at=now,
            log_tail=log_output,
        )
        
        assert len(execution.log_tail) == 100000
