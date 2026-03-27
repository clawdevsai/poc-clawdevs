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
Unit tests for SddArtifact model - 100% mocked, no external access.
"""

from datetime import datetime
from uuid import UUID, uuid4


class TestSddArtifactModel:
    """Test SddArtifact model creation and validation - UNIT TESTS ONLY."""

    def test_artifact_creation(self):
        """Test basic artifact creation."""
        from app.models.sdd_artifact import SddArtifact
        
        artifact = SddArtifact(
            artifact_type="BRIEF",
            title="Test Brief",
            content="Test content",
        )
        
        assert artifact.artifact_type == "BRIEF"
        assert artifact.title == "Test Brief"
        assert artifact.content == "Test content"
        assert artifact.status == "draft"
        assert artifact.id is not None
        assert isinstance(artifact.id, UUID)

    def test_artifact_with_agent(self):
        """Test artifact linked to agent."""
        from app.models.sdd_artifact import SddArtifact
        
        agent_id = uuid4()
        
        artifact = SddArtifact(
            agent_id=agent_id,
            artifact_type="SPEC",
            title="Agent Spec",
            content="Agent specification content",
        )
        
        assert artifact.agent_id == agent_id

    def test_artifact_type_values(self):
        """Test valid artifact_type values."""
        from app.models.sdd_artifact import SddArtifact
        
        valid_types = ["BRIEF", "SPEC", "CLARIFY", "PLAN", "TASK", "VALIDATE"]
        
        for artifact_type in valid_types:
            artifact = SddArtifact(
                artifact_type=artifact_type,
                title=f"Artifact {artifact_type}",
                content=f"Content for {artifact_type}",
            )
            assert artifact.artifact_type == artifact_type

    def test_artifact_status_values(self):
        """Test valid status values."""
        from app.models.sdd_artifact import SddArtifact
        
        valid_statuses = ["draft", "active", "done"]
        
        for status in valid_statuses:
            artifact = SddArtifact(
                artifact_type="BRIEF",
                title=f"Status Test {status}",
                status=status,
            )
            assert artifact.status == status

    def test_artifact_with_github_issue(self):
        """Test artifact linked to GitHub issue."""
        from app.models.sdd_artifact import SddArtifact
        
        artifact = SddArtifact(
            artifact_type="TASK",
            title="GitHub Task",
            github_issue_number=123,
            github_issue_url="https://github.com/org/repo/issues/123",
        )
        
        assert artifact.github_issue_number == 123
        assert "123" in artifact.github_issue_url

    def test_artifact_with_file_path(self):
        """Test artifact with file path reference."""
        from app.models.sdd_artifact import SddArtifact
        
        artifact = SddArtifact(
            artifact_type="SPEC",
            title="File Spec",
            file_path="/pvc/specs/agent_spec.md",
        )
        
        assert artifact.file_path == "/pvc/specs/agent_spec.md"

    def test_artifact_without_content(self):
        """Test artifact without content (defaults to empty string)."""
        from app.models.sdd_artifact import SddArtifact
        
        artifact = SddArtifact(
            artifact_type="BRIEF",
            title="Empty Content Test",
        )
        
        assert artifact.content == ""

    def test_artifact_timestamps(self):
        """Test automatic timestamp creation."""
        from app.models.sdd_artifact import SddArtifact
        
        artifact = SddArtifact(
            artifact_type="BRIEF",
            title="Timestamp Test",
            content="Testing timestamps",
        )
        
        assert artifact.created_at is not None
        assert artifact.updated_at is not None
        assert isinstance(artifact.created_at, datetime)


class TestSddArtifactWorkflow:
    """Test artifact status workflow - UNIT TESTS ONLY."""

    def test_draft_to_active(self):
        """Test artifact transition from draft to active."""
        from app.models.sdd_artifact import SddArtifact
        
        artifact = SddArtifact(
            artifact_type="BRIEF",
            title="Workflow Test",
            status="draft",
        )
        
        artifact.status = "active"
        
        assert artifact.status == "active"

    def test_active_to_done(self):
        """Test artifact transition from active to done."""
        from app.models.sdd_artifact import SddArtifact
        
        artifact = SddArtifact(
            artifact_type="SPEC",
            title="Done Workflow",
            status="active",
        )
        
        artifact.status = "done"
        
        assert artifact.status == "done"

    def test_complete_workflow(self):
        """Test complete artifact workflow."""
        from app.models.sdd_artifact import SddArtifact
        
        artifact = SddArtifact(
            artifact_type="CLARIFY",
            title="Complete Workflow",
            status="draft",
        )
        
        artifact.status = "active"
        assert artifact.status == "active"
        
        artifact.status = "done"
        assert artifact.status == "done"


class TestSddArtifactTypes:
    """Test different SDD artifact types - UNIT TESTS ONLY."""

    def test_brief_artifact(self):
        """Test BRIEF artifact type."""
        from app.models.sdd_artifact import SddArtifact
        
        artifact = SddArtifact(
            artifact_type="BRIEF",
            title="System Brief",
            content="High-level system overview",
        )
        
        assert artifact.artifact_type == "BRIEF"

    def test_spec_artifact(self):
        """Test SPEC artifact type."""
        from app.models.sdd_artifact import SddArtifact
        
        artifact = SddArtifact(
            artifact_type="SPEC",
            title="Technical Specification",
            content="Detailed technical specs",
        )
        
        assert artifact.artifact_type == "SPEC"

    def test_plan_artifact(self):
        """Test PLAN artifact type."""
        from app.models.sdd_artifact import SddArtifact
        
        artifact = SddArtifact(
            artifact_type="PLAN",
            title="Implementation Plan",
            content="Steps for implementation",
        )
        
        assert artifact.artifact_type == "PLAN"

    def test_task_artifact(self):
        """Test TASK artifact type."""
        from app.models.sdd_artifact import SddArtifact
        
        artifact = SddArtifact(
            artifact_type="TASK",
            title="Development Task",
            github_issue_number=456,
        )
        
        assert artifact.artifact_type == "TASK"

    def test_validate_artifact(self):
        """Test VALIDATE artifact type."""
        from app.models.sdd_artifact import SddArtifact
        
        artifact = SddArtifact(
            artifact_type="VALIDATE",
            title="Validation Check",
            content="Validation criteria",
        )
        
        assert artifact.artifact_type == "VALIDATE"


class TestSddArtifactEdgeCases:
    """Test edge cases for SddArtifact model."""

    def test_artifact_id_is_uuid(self):
        """Test that artifact ID is UUID."""
        from app.models.sdd_artifact import SddArtifact
        
        artifact = SddArtifact(
            artifact_type="BRIEF",
            title="UUID Artifact",
            content="Content",
        )
        
        assert isinstance(artifact.id, UUID)
        assert len(str(artifact.id)) == 36

    def test_artifact_empty_content(self):
        """Test artifact with empty content."""
        from app.models.sdd_artifact import SddArtifact
        
        artifact = SddArtifact(
            artifact_type="BRIEF",
            title="Empty Content",
            content="",
        )
        
        assert artifact.content == ""

    def test_artifact_none_values(self):
        """Test artifact with None values."""
        from app.models.sdd_artifact import SddArtifact
        
        artifact = SddArtifact(
            artifact_type="BRIEF",
            title="None Values",
            content=None,
            github_issue_number=None,
            file_path=None,
        )
        
        assert artifact.content is None
        assert artifact.github_issue_number is None
        assert artifact.file_path is None

    def test_artifact_long_content(self):
        """Test artifact with long content."""
        from app.models.sdd_artifact import SddArtifact
        
        content = "x" * 100000
        
        artifact = SddArtifact(
            artifact_type="SPEC",
            title="Long Content",
            content=content,
        )
        
        assert len(artifact.content) == 100000
