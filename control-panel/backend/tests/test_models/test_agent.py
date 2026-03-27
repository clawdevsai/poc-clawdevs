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
Unit tests for Agent model - 100% mocked, no external access.
"""

from datetime import datetime
from uuid import UUID


class TestAgentModel:
    """Test Agent model creation and validation - UNIT TESTS ONLY."""

    def test_agent_creation(self):
        """Test basic agent creation."""
        from app.models.agent import Agent

        agent = Agent(
            slug="test-agent",
            display_name="Test Agent",
            role="QA Engineer",
        )

        assert agent.slug == "test-agent"
        assert agent.display_name == "Test Agent"
        assert agent.role == "QA Engineer"
        assert agent.status == "unknown"
        assert agent.id is not None
        assert isinstance(agent.id, UUID)

    def test_agent_with_optional_fields(self):
        """Test agent with all optional fields populated."""
        from app.models.agent import Agent
        from datetime import datetime

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

        assert agent.avatar_url == "https://example.com/avatar.png"
        assert agent.status == "active"
        assert agent.current_model == "gpt-4"
        assert agent.openclaw_session_id == "session-123"
        assert agent.cron_expression == "0 * * * *"
        assert agent.cron_status == "idle"

    def test_agent_status_values(self):
        """Test valid status values for agent."""
        from app.models.agent import Agent

        valid_statuses = ["active", "inactive", "error", "unknown"]

        for status in valid_statuses:
            agent = Agent(
                slug=f"agent-{status}",
                display_name=f"Agent {status}",
                role="Tester",
                status=status,
            )
            assert agent.status == status

    def test_agent_cron_status_values(self):
        """Test valid cron status values."""
        from app.models.agent import Agent

        valid_cron_statuses = ["idle", "running", "error"]

        for cron_status in valid_cron_statuses:
            agent = Agent(
                slug=f"agent-cron-{cron_status}",
                display_name=f"Agent {cron_status}",
                role="Tester",
                cron_status=cron_status,
            )
            assert agent.cron_status == cron_status

    def test_agent_timestamps(self):
        """Test automatic timestamp creation."""
        from app.models.agent import Agent

        agent = Agent(
            slug="timestamp-agent",
            display_name="Timestamp Agent",
            role="Tester",
        )

        assert agent.created_at is not None
        assert agent.updated_at is not None
        assert isinstance(agent.created_at, datetime)

    def test_agent_update(self):
        """Test updating agent attributes."""
        from app.models.agent import Agent

        agent = Agent(
            slug="update-agent",
            display_name="Update Agent",
            role="Tester",
            status="unknown",
        )

        agent.status = "active"
        agent.current_model = "gpt-4"

        assert agent.status == "active"
        assert agent.current_model == "gpt-4"


class TestAgentStatusTransitions:
    """Test agent status change scenarios - UNIT TESTS ONLY."""

    def test_agent_activation_workflow(self):
        """Test agent status changes from unknown to active."""
        from app.models.agent import Agent

        agent = Agent(
            slug="activation-agent",
            display_name="Activation Agent",
            role="Tester",
            status="unknown",
        )

        agent.status = "active"

        assert agent.status == "active"

    def test_agent_error_recovery(self):
        """Test agent recovery from error state."""
        from app.models.agent import Agent

        agent = Agent(
            slug="error-agent",
            display_name="Error Agent",
            role="Tester",
            status="error",
        )

        agent.status = "active"

        assert agent.status == "active"

    def test_agent_deactivation(self):
        """Test agent deactivation."""
        from app.models.agent import Agent

        agent = Agent(
            slug="deactivated-agent",
            display_name="Deactivated Agent",
            role="Tester",
            status="active",
        )

        agent.status = "inactive"

        assert agent.status == "inactive"


class TestAgentCronManagement:
    """Test agent cron-related fields - UNIT TESTS ONLY."""

    def test_agent_cron_schedule(self):
        """Test agent with cron schedule."""
        from app.models.agent import Agent

        agent = Agent(
            slug="cron-agent",
            display_name="Cron Agent",
            role="Scheduler",
            cron_expression="*/5 * * * *",
            cron_status="idle",
        )

        assert agent.cron_expression == "*/5 * * * *"
        assert agent.cron_status == "idle"

    def test_agent_cron_execution_tracking(self):
        """Test tracking of cron execution times."""
        from app.models.agent import Agent
        from datetime import datetime, timedelta

        now = datetime.utcnow()
        tomorrow = now + timedelta(days=1)

        agent = Agent(
            slug="cron-tracker-agent",
            display_name="Cron Tracker Agent",
            role="Scheduler",
            cron_expression="0 0 * * *",
            cron_last_run_at=now,
            cron_next_run_at=tomorrow,
            cron_status="idle",
        )

        assert agent.cron_last_run_at == now
        assert agent.cron_next_run_at == tomorrow


class TestAgentEdgeCases:
    """Test edge cases for Agent model."""

    def test_agent_id_is_uuid(self):
        """Test that agent ID is UUID."""
        from app.models.agent import Agent

        agent = Agent(
            slug="uuid-agent",
            display_name="UUID Agent",
            role="Tester",
        )

        assert isinstance(agent.id, UUID)
        assert len(str(agent.id)) == 36

    def test_agent_can_be_serialized(self):
        """Test that agent can be serialized to dict."""
        from app.models.agent import Agent

        agent = Agent(
            slug="serialize-agent",
            display_name="Serialize Agent",
            role="Tester",
        )

        assert hasattr(agent, "slug")
        assert hasattr(agent, "display_name")
        assert hasattr(agent, "role")
        assert hasattr(agent, "status")

    def test_agent_empty_fields(self):
        """Test agent with empty optional fields."""
        from app.models.agent import Agent

        agent = Agent(
            slug="empty-agent",
            display_name="Empty Agent",
            role="Tester",
            avatar_url="",
            current_model=None,
        )

        assert agent.avatar_url == ""
        assert agent.current_model is None
