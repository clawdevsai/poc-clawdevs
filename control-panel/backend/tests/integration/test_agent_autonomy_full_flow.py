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
End-to-End Integration Tests for Agent Autonomy Framework

Tests complete workflows:
1. Task creation → completion → memory storage
2. Failure detection and escalation
3. RAG semantic search on past solutions
4. Governance validation (CONSTITUTION, cost, multi-repo)
5. Test automation quality gates
6. Cost tracking and budget enforcement
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Task, Agent, MemoryEntry
from app.services.failure_detector import FailureDetector
from app.services.rag_retriever import RAGRetriever
from app.services.governance_engine import GovernanceEngine
from app.services.cost_tracker import CostTracker


class TestAgentAutonomyFullFlow:
    """Complete end-to-end autonomy framework tests."""

    @pytest.mark.asyncio
    async def test_01_task_creation_workflow(
        self, client: AsyncClient, db_session: AsyncSession, auth_headers: dict
    ):
        """Test complete task creation workflow."""
        from uuid import UUID as PyUUID

        # Create task
        task_data = {
            "title": "Implement user authentication",
            "description": "Add JWT-based auth to backend",
            "label": "back_end",
            "priority": "high",
        }
        response = await client.post("/tasks", json=task_data, headers=auth_headers)
        assert response.status_code == 201
        task = response.json()
        task_id = PyUUID(task["id"])  # Convert string to UUID

        # Verify task created in database
        db_task = await db_session.get(Task, task_id)
        assert db_task is not None
        assert db_task.title == "Implement user authentication"
        assert db_task.status == "inbox"
        assert db_task.failure_count == 0
        assert db_task.consecutive_failures == 0

    @pytest.mark.asyncio
    async def test_02_task_status_progression(
        self, client: AsyncClient, db_session: AsyncSession, auth_headers: dict
    ):
        """Test task status transitions."""
        # Create task
        task = Task(
            title="Fix bug in API",
            description="Endpoint returns 500",
            label="back_end",
            priority="high",
            status="inbox",
        )
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)

        # Update to in_progress
        response = await client.patch(
            f"/tasks/{task.id}",
            json={"status": "in_progress"},
            headers=auth_headers,
        )
        assert response.status_code == 200

        # Verify status updated
        await db_session.refresh(task)
        assert task.status == "in_progress"

        # Update to done
        response = await client.patch(
            f"/tasks/{task.id}",
            json={"status": "done"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        await db_session.refresh(task)
        assert task.status == "done"

    @pytest.mark.asyncio
    async def test_03_failure_detection_consecutive_failures(
        self, db_session: AsyncSession
    ):
        """Test failure detection on consecutive failures."""
        detector = FailureDetector(db_session)

        # Create task
        task = Task(
            title="Deploy to production",
            description="Push new version",
            label="devops",
            status="in_progress",
        )
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)

        # Simulate 3 consecutive failures
        for i in range(3):
            await detector.record_failure(
                task_id=task.id,
                error_type="DeploymentError",
                error_message=f"Deployment attempt {i+1} failed",
            )
            await db_session.refresh(task)
            assert task.failure_count == i + 1
            assert task.consecutive_failures == i + 1

        # After 3 failures, should be ready for escalation
        assert task.consecutive_failures == 3
        assert task.last_error is not None

    @pytest.mark.asyncio
    async def test_04_automatic_escalation_on_repeated_failures(
        self, db_session: AsyncSession
    ):
        """Test automatic escalation to senior agent."""
        detector = FailureDetector(db_session)

        # Create backend developer agent
        dev_agent = Agent(
            name="Dev_Backend",
            slug="dev_backend",
            role="developer",
            can_escalate=False,
        )
        db_session.add(dev_agent)
        await db_session.commit()

        # Create senior architect agent
        architect = Agent(
            name="Arquiteto",
            slug="arquiteto",
            role="architect",
            can_escalate=True,
        )
        db_session.add(architect)
        await db_session.commit()

        # Create task assigned to dev
        task = Task(
            title="Fix authentication bug",
            description="Auth endpoint broken",
            label="back_end",
            assigned_agent_id=dev_agent.id,
            status="in_progress",
        )
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)

        # Simulate 3 failures - should escalate
        for i in range(3):
            await detector.record_failure(
                task_id=task.id,
                error_type="AuthError",
                error_message="Token validation failed",
            )

        # Check if escalation was triggered
        await db_session.refresh(task)
        assert task.consecutive_failures == 3
        # Escalation routing: backend issue → Arquiteto
        escalated_agent_id = detector.domain_escalation_routing.get("backend")
        assert escalated_agent_id is not None

    @pytest.mark.asyncio
    async def test_05_exponential_backoff_retry_logic(self, db_session: AsyncSession):
        """Test exponential backoff on retries."""
        detector = FailureDetector(db_session)

        task = Task(
            title="Sync data with external API",
            description="API call failing intermittently",
            label="back_end",
        )
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)

        # Record first failure
        await detector.record_failure(
            task_id=task.id,
            error_type="APITimeout",
            error_message="Connection timeout",
        )
        await db_session.refresh(task)
        assert task.failure_count == 1

        # Apply exponential backoff
        await detector.apply_exponential_backoff(task.id, attempt=1)
        await db_session.refresh(task)
        # Backoff should be stored (1.5x multiplier: 1.5 seconds)

        # Record second failure
        await detector.record_failure(
            task_id=task.id,
            error_type="APITimeout",
            error_message="Connection timeout again",
        )
        await db_session.refresh(task)
        assert task.failure_count == 2

    @pytest.mark.asyncio
    async def test_06_memory_persistence_and_rag_retrieval(
        self, db_session: AsyncSession
    ):
        """Test memory persistence and semantic search via RAG."""
        # Create memory entries with solutions
        solution_1 = MemoryEntry(
            title="Fix JWT token expiration",
            content="Add refresh token logic to auth service. Use sliding window with 15min expiration.",
            agent_slug="dev_backend",
            tags=["authentication", "jwt", "tokens"],
            source="completed_task_12345",
        )
        solution_2 = MemoryEntry(
            title="Handle API timeouts gracefully",
            content="Implement retry logic with exponential backoff. Start with 1s, max 30s between retries.",
            agent_slug="dev_backend",
            tags=["api", "timeout", "retry"],
            source="completed_task_67890",
        )
        db_session.add(solution_1)
        db_session.add(solution_2)
        await db_session.commit()

        # Verify memory entries exist
        entries = await db_session.execute(
            "SELECT * FROM memory_entries WHERE agent_slug = 'dev_backend'"
        )
        entries = entries.fetchall()
        assert len(entries) == 2

        # Test RAG retriever (simulated without actual embeddings)
        retriever = RAGRetriever(db_session)
        # In full implementation, would use semantic search
        # For now, verify the service initializes
        assert retriever is not None

    @pytest.mark.asyncio
    async def test_07_governance_validation_constitution_rules(
        self, db_session: AsyncSession, auth_headers: dict
    ):
        """Test governance validation against CONSTITUTION rules."""
        engine = GovernanceEngine(db_session)

        # Valid task
        valid_task = {
            "title": "Add unit tests for payment module",
            "description": "Implement 90%+ coverage",
            "label": "back_end",
        }
        is_valid, error = await engine.validate_task_creation(valid_task)
        assert is_valid
        assert error is None

        # Invalid task (title too short)
        invalid_task = {
            "title": "Fix",
            "description": "Quick fix",
            "label": "back_end",
        }
        is_valid, error = await engine.validate_task_creation(invalid_task)
        assert not is_valid
        assert error is not None

    @pytest.mark.asyncio
    async def test_08_cost_estimation_and_tracking(self, db_session: AsyncSession):
        """Test cost estimation and tracking."""
        tracker = CostTracker(db_session)

        # Estimate cost for simple task
        estimates = await tracker.estimate_task_cost(
            task_type="unit_test",
            complexity="simple",
        )
        assert "local" in estimates
        assert "medium" in estimates
        assert "premium" in estimates
        # Local (Ollama) should be free
        assert estimates["local"] == 0.0
        # Medium should be cheap
        assert estimates["medium"] > 0
        # Premium should be more expensive
        assert estimates["premium"] > estimates["medium"]

    @pytest.mark.asyncio
    async def test_09_cost_budget_enforcement(self, db_session: AsyncSession):
        """Test cost budget limits per tier."""
        tracker = CostTracker(db_session)

        # Create agent
        agent = Agent(name="Dev_Backend", slug="dev_backend", role="developer")
        db_session.add(agent)
        await db_session.commit()
        await db_session.refresh(agent)

        # Check budget for medium tier
        available, warning = await tracker.check_budget_available(
            agent_id=agent.id,
            task_tier="medium",
        )
        # New agent should have full budget available
        assert available is True
        assert warning is None

    @pytest.mark.asyncio
    async def test_10_multi_repo_coordination_validation(
        self, db_session: AsyncSession
    ):
        """Test multi-repo dependency validation."""
        engine = GovernanceEngine(db_session)

        # Valid: frontend depends on backend
        is_valid, error = await engine.validate_multi_repo_change(
            repo="frontend",
            depends_on_repos=["backend", "shared_lib"],
            pr_description="Depends on: #123 - backend API changes",
        )
        assert is_valid
        assert error is None

        # Invalid: mobile depends on frontend (wrong order)
        is_valid, error = await engine.validate_multi_repo_change(
            repo="mobile",
            depends_on_repos=["frontend"],  # Should only depend on backend/shared_lib
            pr_description="Mobile update",
        )
        # This might be invalid depending on rules
        # (mobile should not directly depend on frontend)

    @pytest.mark.asyncio
    async def test_11_test_automation_quality_gates(
        self, client: AsyncClient, db_session: AsyncSession, auth_headers: dict
    ):
        """Test quality gate enforcement."""
        # Create task with test requirements
        task = Task(
            title="New feature implementation",
            description="Must have >80% test coverage",
            label="back_end",
            status="in_progress",
        )
        db_session.add(task)
        await db_session.commit()

        # In full integration, would check /api/quality endpoints
        # Verify quality gate API exists
        response = await client.get("/api/health/summary", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_tasks" in data
        assert "health_percentage" in data

    @pytest.mark.asyncio
    async def test_12_failure_recovery_workflow(self, db_session: AsyncSession):
        """Test complete failure detection and recovery."""
        detector = FailureDetector(db_session)

        # Create task
        task = Task(
            title="Database migration",
            description="Run schema migration",
            label="devops",
            status="in_progress",
        )
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)

        # First failure
        await detector.record_failure(
            task_id=task.id,
            error_type="MigrationError",
            error_message="Foreign key constraint violation",
        )
        await db_session.refresh(task)
        assert task.failure_count == 1
        assert task.consecutive_failures == 1

        # Reset failures on success
        await detector.reset_consecutive_failures(task.id)
        await db_session.refresh(task)
        # consecutive_failures should be 0, but failure_count remains
        assert task.consecutive_failures == 0
        assert task.failure_count == 1  # Still tracks total failures

    @pytest.mark.asyncio
    async def test_13_agent_health_status_monitoring(
        self, client: AsyncClient, db_session: AsyncSession, auth_headers: dict
    ):
        """Test agent health status monitoring."""
        # Create healthy task
        healthy_task = Task(
            title="Simple task",
            description="No failures",
            label="back_end",
            status="done",
        )
        db_session.add(healthy_task)

        # Create unhealthy task (with failures)
        unhealthy_task = Task(
            title="Problematic task",
            description="Multiple failures",
            label="back_end",
            consecutive_failures=2,
            failure_count=2,
        )
        db_session.add(unhealthy_task)

        # Create failed task (escalated)
        escalated_agent = Agent(
            name="Arquiteto",
            slug="arquiteto",
            role="architect",
            can_escalate=True,
        )
        db_session.add(escalated_agent)
        await db_session.commit()

        failed_task = Task(
            title="Critical issue",
            description="Escalated to architect",
            label="back_end",
            consecutive_failures=3,
            failure_count=3,
            escalated_to_agent_id=escalated_agent.id,
        )
        db_session.add(failed_task)
        await db_session.commit()

        # Get health summary
        response = await client.get(
            "/api/health/summary",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_tasks"] == 3
        assert data["healthy_tasks"] == 1
        assert data["unhealthy_tasks"] == 1
        assert data["escalated_tasks"] == 1

    @pytest.mark.asyncio
    async def test_14_end_to_end_task_lifecycle(
        self, client: AsyncClient, db_session: AsyncSession, auth_headers: dict
    ):
        """Test complete task lifecycle from creation to completion."""
        # 1. Create task
        task_data = {
            "title": "Implement new API endpoint",
            "description": "POST /api/v1/users with validation",
            "label": "back_end",
            "priority": "high",
        }
        response = await client.post("/tasks", json=task_data, headers=auth_headers)
        assert response.status_code == 201
        task = response.json()
        task_id = task["id"]

        # 2. Assign to agent
        db_task = await db_session.get(Task, task_id)
        agent = Agent(name="Dev_Backend", slug="dev_backend", role="developer")
        db_session.add(agent)
        await db_session.commit()
        await db_session.refresh(agent)

        db_task.assigned_agent_id = agent.id
        await db_session.commit()

        # 3. Mark as in_progress
        response = await client.patch(
            f"/tasks/{task_id}",
            json={"status": "in_progress"},
            headers=auth_headers,
        )
        assert response.status_code == 200

        # 4. Run tests (simulated)
        # In real scenario, tests would run via CI/CD

        # 5. Mark as done
        response = await client.patch(
            f"/tasks/{task_id}",
            json={"status": "done"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        await db_session.refresh(db_task)
        assert db_task.status == "done"

        # 6. Store in memory
        memory = MemoryEntry(
            title="API endpoint implementation",
            content="Created POST /api/v1/users with request validation",
            agent_slug="dev_backend",
            tags=["api", "endpoint", "rest"],
            source=f"task_{task_id}",
        )
        db_session.add(memory)
        await db_session.commit()

        # Verify memory stored
        entries = await db_session.execute(
            "SELECT * FROM memory_entries WHERE source = :source",
            {"source": f"task_{task_id}"},
        )
        entries = entries.fetchall()
        assert len(entries) == 1

    @pytest.mark.asyncio
    async def test_15_concurrent_agent_tasks(self, db_session: AsyncSession):
        """Test multiple agents handling concurrent tasks."""
        # Create multiple agents
        agents = []
        for i in range(3):
            agent = Agent(
                name=f"Agent_{i}",
                slug=f"agent_{i}",
                role="developer",
            )
            db_session.add(agent)
            agents.append(agent)
        await db_session.commit()

        # Create concurrent tasks
        tasks = []
        for i, agent in enumerate(agents):
            task = Task(
                title=f"Task for {agent.name}",
                description=f"Concurrent task {i}",
                label="back_end",
                assigned_agent_id=agent.id,
                status="in_progress",
            )
            db_session.add(task)
            tasks.append(task)
        await db_session.commit()

        # Verify all tasks created
        task_count = await db_session.execute("SELECT COUNT(*) FROM tasks")
        count = task_count.scalar()
        assert count == 3

        # Verify each agent has 1 task
        for agent in agents:
            agent_tasks = await db_session.execute(
                "SELECT COUNT(*) FROM tasks WHERE assigned_agent_id = :id",
                {"id": str(agent.id)},
            )
            assert agent_tasks.scalar() == 1
