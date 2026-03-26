import pytest
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, create_engine, Session
from app.models.sdd_artifact import SddArtifact


@pytest.fixture(scope="function")
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


class TestSddArtifactModel:
    """Test SddArtifact model creation and validation."""

    def test_artifact_creation(self, db_session):
        """Test basic artifact creation."""
        artifact = SddArtifact(
            artifact_type="BRIEF",
            title="Test Brief",
            content="Test content",
        )
        db_session.add(artifact)
        db_session.commit()

        assert artifact.id is not None
        assert isinstance(artifact.id, UUID)
        assert artifact.artifact_type == "BRIEF"
        assert artifact.title == "Test Brief"
        assert artifact.content == "Test content"
        assert artifact.status == "draft"  # default
        assert artifact.created_at is not None

    def test_artifact_with_agent(self, db_session):
        """Test artifact linked to agent."""
        agent_id = uuid4()
        artifact = SddArtifact(
            agent_id=agent_id,
            artifact_type="SPEC",
            title="Agent Spec",
            content="Agent specification content",
        )
        db_session.add(artifact)
        db_session.commit()

        assert artifact.agent_id == agent_id

    def test_artifact_type_values(self, db_session):
        """Test valid artifact_type values."""
        valid_types = ["BRIEF", "SPEC", "CLARIFY", "PLAN", "TASK", "VALIDATE"]

        for artifact_type in valid_types:
            artifact = SddArtifact(
                artifact_type=artifact_type,
                title=f"Artifact {artifact_type}",
                content=f"Content for {artifact_type}",
            )
            db_session.add(artifact)
            db_session.commit()

            assert artifact.artifact_type == artifact_type

    def test_artifact_status_values(self, db_session):
        """Test valid status values."""
        valid_statuses = ["draft", "active", "done"]

        for status in valid_statuses:
            artifact = SddArtifact(
                artifact_type="BRIEF",
                title=f"Status Test {status}",
                status=status,
            )
            db_session.add(artifact)
            db_session.commit()

            assert artifact.status == status

    def test_artifact_with_github_issue(self, db_session):
        """Test artifact linked to GitHub issue."""
        artifact = SddArtifact(
            artifact_type="TASK",
            title="GitHub Task",
            github_issue_number=123,
            github_issue_url="https://github.com/org/repo/issues/123",
        )
        db_session.add(artifact)
        db_session.commit()

        assert artifact.github_issue_number == 123
        assert "123" in artifact.github_issue_url

    def test_artifact_with_file_path(self, db_session):
        """Test artifact with file path reference."""
        artifact = SddArtifact(
            artifact_type="SPEC",
            title="File Spec",
            file_path="/pvc/specs/agent_spec.md",
        )
        db_session.add(artifact)
        db_session.commit()

        assert artifact.file_path == "/pvc/specs/agent_spec.md"

    def test_artifact_without_content(self, db_session):
        """Test artifact without content (defaults to empty string)."""
        artifact = SddArtifact(
            artifact_type="BRIEF",
            title="Empty Content Test",
        )
        db_session.add(artifact)
        db_session.commit()

        assert artifact.content == ""

    def test_artifact_timestamps(self, db_session):
        """Test automatic timestamp creation."""
        artifact = SddArtifact(
            artifact_type="BRIEF",
            title="Timestamp Test",
            content="Testing timestamps",
        )
        db_session.add(artifact)
        db_session.commit()

        assert artifact.created_at is not None
        assert artifact.updated_at is not None
        assert isinstance(artifact.created_at, datetime)
        assert isinstance(artifact.updated_at, datetime)


class TestSddArtifactWorkflow:
    """Test artifact status workflow."""

    def test_draft_to_active(self, db_session):
        """Test artifact transition from draft to active."""
        artifact = SddArtifact(
            artifact_type="BRIEF",
            title="Workflow Test",
            status="draft",
        )
        db_session.add(artifact)
        db_session.commit()

        artifact.status = "active"
        db_session.commit()

        assert artifact.status == "active"

    def test_active_to_done(self, db_session):
        """Test artifact transition from active to done."""
        artifact = SddArtifact(
            artifact_type="SPEC",
            title="Done Workflow",
            status="active",
        )
        db_session.add(artifact)
        db_session.commit()

        artifact.status = "done"
        db_session.commit()

        assert artifact.status == "done"

    def test_complete_workflow(self, db_session):
        """Test complete artifact workflow."""
        artifact = SddArtifact(
            artifact_type="CLARIFY",
            title="Complete Workflow",
            status="draft",
        )
        db_session.add(artifact)
        db_session.commit()

        artifact.status = "active"
        db_session.commit()
        assert artifact.status == "active"

        artifact.status = "done"
        db_session.commit()
        assert artifact.status == "done"


class TestSddArtifactTypes:
    """Test different SDD artifact types."""

    def test_brief_artifact(self, db_session):
        """Test BRIEF artifact type."""
        artifact = SddArtifact(
            artifact_type="BRIEF",
            title="System Brief",
            content="High-level system overview",
        )
        db_session.add(artifact)
        db_session.commit()

        assert artifact.artifact_type == "BRIEF"

    def test_spec_artifact(self, db_session):
        """Test SPEC artifact type."""
        artifact = SddArtifact(
            artifact_type="SPEC",
            title="Technical Specification",
            content="Detailed technical specs",
        )
        db_session.add(artifact)
        db_session.commit()

        assert artifact.artifact_type == "SPEC"

    def test_plan_artifact(self, db_session):
        """Test PLAN artifact type."""
        artifact = SddArtifact(
            artifact_type="PLAN",
            title="Implementation Plan",
            content="Steps for implementation",
        )
        db_session.add(artifact)
        db_session.commit()

        assert artifact.artifact_type == "PLAN"

    def test_task_artifact(self, db_session):
        """Test TASK artifact type."""
        artifact = SddArtifact(
            artifact_type="TASK",
            title="Development Task",
            github_issue_number=456,
        )
        db_session.add(artifact)
        db_session.commit()

        assert artifact.artifact_type == "TASK"

    def test_validate_artifact(self, db_session):
        """Test VALIDATE artifact type."""
        artifact = SddArtifact(
            artifact_type="VALIDATE",
            title="Validation Check",
            content="Validation criteria",
        )
        db_session.add(artifact)
        db_session.commit()

        assert artifact.artifact_type == "VALIDATE"


class TestSddArtifactQueries:
    """Test common SDD artifact queries."""

    def test_find_by_type(self, db_session):
        """Test finding artifacts by type."""
        artifact = SddArtifact(
            artifact_type="BRIEF",
            title="Findable Brief",
            content="Content",
        )
        db_session.add(artifact)
        db_session.commit()

        found = db_session.query(SddArtifact).filter(
            SddArtifact.artifact_type == "BRIEF"
        ).first()

        assert found is not None
        assert found.artifact_type == "BRIEF"

    def test_find_by_status(self, db_session):
        """Test finding artifacts by status."""
        artifact = SddArtifact(
            artifact_type="SPEC",
            title="Active Spec",
            status="active",
        )
        db_session.add(artifact)
        db_session.commit()

        found = db_session.query(SddArtifact).filter(
            SddArtifact.status == "active"
        ).first()

        assert found is not None
        assert found.status == "active"
