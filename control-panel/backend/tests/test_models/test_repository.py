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
Unit tests for Repository model - 100% mocked, no external access.
"""

from datetime import datetime
from uuid import UUID


class TestRepositoryModel:
    """Test Repository model creation and validation - UNIT TESTS ONLY."""

    def test_repository_creation(self):
        """Test basic repository creation."""
        from app.models.repository import Repository

        repo = Repository(
            name="test-repo",
            full_name="org/test-repo",
        )

        assert repo.name == "test-repo"
        assert repo.full_name == "org/test-repo"
        assert repo.default_branch == "main"
        assert repo.is_active is True
        assert repo.id is not None
        assert isinstance(repo.id, UUID)

    def test_repository_with_description(self):
        """Test repository with description."""
        from app.models.repository import Repository

        repo = Repository(
            name="described-repo",
            full_name="org/described-repo",
            description="A test repository",
        )

        assert repo.description == "A test repository"

    def test_repository_with_custom_branch(self):
        """Test repository with custom default branch."""
        from app.models.repository import Repository

        repo = Repository(
            name="dev-repo",
            full_name="org/dev-repo",
            default_branch="develop",
        )

        assert repo.default_branch == "develop"

    def test_repository_inactive(self):
        """Test inactive repository."""
        from app.models.repository import Repository

        repo = Repository(
            name="inactive-repo",
            full_name="org/inactive-repo",
            is_active=False,
        )

        assert repo.is_active is False

    def test_repository_timestamps(self):
        """Test automatic timestamp creation."""
        from app.models.repository import Repository

        repo = Repository(
            name="timestamp-repo",
            full_name="org/timestamp-repo",
        )

        assert repo.created_at is not None
        assert repo.updated_at is not None
        assert isinstance(repo.created_at, datetime)

    def test_repository_with_all_fields(self):
        """Test repository with all fields populated."""
        from app.models.repository import Repository

        repo = Repository(
            name="complete-repo",
            full_name="org/complete-repo",
            description="Complete test repository",
            default_branch="main",
            is_active=True,
        )

        assert repo.name == "complete-repo"
        assert repo.full_name == "org/complete-repo"
        assert repo.description == "Complete test repository"
        assert repo.default_branch == "main"
        assert repo.is_active is True


class TestRepositoryStatus:
    """Test repository active/inactive states - UNIT TESTS ONLY."""

    def test_active_repository(self):
        """Test active repository (default)."""
        from app.models.repository import Repository

        repo = Repository(
            name="active-repo",
            full_name="org/active-repo",
        )

        assert repo.is_active is True

    def test_deactivate_repository(self):
        """Test deactivating a repository."""
        from app.models.repository import Repository

        repo = Repository(
            name="reactivate-repo",
            full_name="org/reactivate-repo",
        )

        repo.is_active = False

        assert repo.is_active is False

    def test_activate_repository(self):
        """Test reactivating a repository."""
        from app.models.repository import Repository

        repo = Repository(
            name="reactivated-repo",
            full_name="org/reactivated-repo",
            is_active=False,
        )

        repo.is_active = True

        assert repo.is_active is True


class TestRepositoryEdgeCases:
    """Test edge cases for Repository model."""

    def test_repository_id_is_uuid(self):
        """Test that repository ID is UUID."""
        from app.models.repository import Repository

        repo = Repository(
            name="uuid-repo",
            full_name="org/uuid-repo",
        )

        assert isinstance(repo.id, UUID)
        assert len(str(repo.id)) == 36

    def test_repository_empty_description(self):
        """Test repository with empty description."""
        from app.models.repository import Repository

        repo = Repository(
            name="empty-desc-repo",
            full_name="org/empty-desc-repo",
            description="",
        )

        assert repo.description == ""

    def test_repository_none_values(self):
        """Test repository with None values."""
        from app.models.repository import Repository

        repo = Repository(
            name="none-values-repo",
            full_name="org/none-values-repo",
            description=None,
            default_branch=None,
        )

        assert repo.description is None
        assert repo.default_branch is None

    def test_repository_long_values(self):
        """Test repository with long field values."""
        from app.models.repository import Repository

        long_name = "x" * 1000
        long_desc = "x" * 10000

        repo = Repository(
            name=long_name[:255],
            full_name=f"org/{long_name[:200]}",
            description=long_desc[:5000],
        )

        assert len(repo.name) > 0
        assert len(repo.full_name) > 0
        assert len(repo.description) > 0
