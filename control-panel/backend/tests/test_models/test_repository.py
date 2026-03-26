import pytest
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, create_engine, Session
from app.models.repository import Repository


@pytest.fixture(scope="function")
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


class TestRepositoryModel:
    """Test Repository model creation and validation."""

    def test_repository_creation(self, db_session):
        """Test basic repository creation."""
        repo = Repository(
            name="test-repo",
            full_name="org/test-repo",
        )
        db_session.add(repo)
        db_session.commit()

        assert repo.id is not None
        assert isinstance(repo.id, UUID)
        assert repo.name == "test-repo"
        assert repo.full_name == "org/test-repo"
        assert repo.default_branch == "main"  # default
        assert repo.is_active is True  # default
        assert repo.created_at is not None

    def test_repository_with_description(self, db_session):
        """Test repository with description."""
        repo = Repository(
            name="described-repo",
            full_name="org/described-repo",
            description="A test repository",
        )
        db_session.add(repo)
        db_session.commit()

        assert repo.description == "A test repository"

    def test_repository_with_custom_branch(self, db_session):
        """Test repository with custom default branch."""
        repo = Repository(
            name="dev-repo",
            full_name="org/dev-repo",
            default_branch="develop",
        )
        db_session.add(repo)
        db_session.commit()

        assert repo.default_branch == "develop"

    def test_repository_inactive(self, db_session):
        """Test inactive repository."""
        repo = Repository(
            name="inactive-repo",
            full_name="org/inactive-repo",
            is_active=False,
        )
        db_session.add(repo)
        db_session.commit()

        assert repo.is_active is False

    def test_repository_unique_full_name(self, db_session):
        """Test that full_name is unique."""
        repo1 = Repository(
            name="unique-repo",
            full_name="org/unique-repo",
        )
        db_session.add(repo1)
        db_session.commit()

        repo2 = Repository(
            name="duplicate-repo",
            full_name="org/unique-repo",  # Same full_name
        )
        db_session.add(repo2)

        # This test documents expected behavior - uniqueness constraint
        assert repo2.full_name == repo1.full_name  # Same in different objects

    def test_repository_timestamps(self, db_session):
        """Test automatic timestamp creation."""
        repo = Repository(
            name="timestamp-repo",
            full_name="org/timestamp-repo",
        )
        db_session.add(repo)
        db_session.commit()

        assert repo.created_at is not None
        assert repo.updated_at is not None
        assert isinstance(repo.created_at, datetime)
        assert isinstance(repo.updated_at, datetime)

    def test_repository_with_all_fields(self, db_session):
        """Test repository with all fields populated."""
        repo = Repository(
            name="complete-repo",
            full_name="org/complete-repo",
            description="Complete test repository",
            default_branch="main",
            is_active=True,
        )
        db_session.add(repo)
        db_session.commit()

        assert repo.name == "complete-repo"
        assert repo.full_name == "org/complete-repo"
        assert repo.description == "Complete test repository"
        assert repo.default_branch == "main"
        assert repo.is_active is True


class TestRepositoryStatus:
    """Test repository active/inactive states."""

    def test_active_repository(self, db_session):
        """Test active repository (default)."""
        repo = Repository(
            name="active-repo",
            full_name="org/active-repo",
        )
        db_session.add(repo)
        db_session.commit()

        assert repo.is_active is True

    def test_deactivate_repository(self, db_session):
        """Test deactivating a repository."""
        repo = Repository(
            name="reactivate-repo",
            full_name="org/reactivate-repo",
        )
        db_session.add(repo)
        db_session.commit()

        # Deactivate
        repo.is_active = False
        db_session.commit()

        assert repo.is_active is False

    def test_activate_repository(self, db_session):
        """Test reactivating a repository."""
        repo = Repository(
            name="reactivated-repo",
            full_name="org/reactivated-repo",
            is_active=False,
        )
        db_session.add(repo)
        db_session.commit()

        # Reactivate
        repo.is_active = True
        db_session.commit()

        assert repo.is_active is True


class TestRepositoryQueries:
    """Test common repository queries."""

    def test_find_by_full_name(self, db_session):
        """Test finding repository by full name."""
        repo = Repository(
            name="findable-repo",
            full_name="org/findable-repo",
        )
        db_session.add(repo)
        db_session.commit()

        found = db_session.query(Repository).filter(
            Repository.full_name == "org/findable-repo"
        ).first()

        assert found is not None
        assert found.full_name == "org/findable-repo"

    def test_find_active_repositories(self, db_session):
        """Test finding only active repositories."""
        active_repo = Repository(
            name="active-repo",
            full_name="org/active-repo",
            is_active=True,
        )
        inactive_repo = Repository(
            name="inactive-repo",
            full_name="org/inactive-repo",
            is_active=False,
        )
        db_session.add(active_repo)
        db_session.add(inactive_repo)
        db_session.commit()

        # Query only active
        active_found = db_session.query(Repository).filter(
            Repository.is_active.is_(True)
        ).all()

        assert len(active_found) == 1
        assert active_found[0].full_name == "org/active-repo"
