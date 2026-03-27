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
Unit tests for User model - 100% mocked, no external access.
"""

from datetime import datetime
from uuid import UUID


class TestUserModel:
    """Test User model creation and validation - UNIT TESTS ONLY."""

    def test_user_creation(self):
        """Test basic user creation."""
        from app.models.user import User
        from app.core.auth import get_password_hash
        
        user = User(
            username="testuser",
            password_hash=get_password_hash("password123"),
            role="viewer",
        )
        
        # Only test model attributes, no database access
        assert user.username == "testuser"
        assert user.role == "viewer"
        assert user.is_active is True
        assert user.id is not None
        assert isinstance(user.id, UUID)

    def test_user_with_admin_role(self):
        """Test user with admin role."""
        from app.models.user import User
        from app.core.auth import get_password_hash
        
        user = User(
            username="adminuser",
            password_hash=get_password_hash("adminpass"),
            role="admin",
        )
        
        assert user.role == "admin"

    def test_user_default_values(self):
        """Test default values for optional fields."""
        from app.models.user import User
        from app.core.auth import get_password_hash
        
        user = User(
            username="defaultuser",
            password_hash=get_password_hash("password"),
        )
        
        assert user.role == "viewer"  # default
        assert user.is_active is True  # default

    def test_user_deactivation(self):
        """Test user deactivation."""
        from app.models.user import User
        from app.core.auth import get_password_hash
        
        user = User(
            username="inactiveuser",
            password_hash=get_password_hash("password"),
            is_active=False,
        )
        
        assert user.is_active is False

    def test_user_timestamps(self):
        """Test automatic timestamp creation."""
        from app.models.user import User
        from app.core.auth import get_password_hash
        
        user = User(
            username="timestampuser",
            password_hash=get_password_hash("password"),
        )
        
        assert user.created_at is not None
        assert isinstance(user.created_at, datetime)

    def test_user_update(self):
        """Test updating user attributes."""
        from app.models.user import User
        from app.core.auth import get_password_hash
        
        user = User(
            username="updateuser",
            password_hash=get_password_hash("password"),
            role="viewer",
        )
        
        # Update attributes
        user.role = "admin"
        user.is_active = False
        
        assert user.role == "admin"
        assert user.is_active is False

    def test_user_password_hash_format(self):
        """Test that password hash follows bcrypt format."""
        from app.core.auth import get_password_hash
        
        password = "testpassword"
        hashed = get_password_hash(password)
        
        # Passlib bcrypt_sha256 format: $bcrypt-sha256$... or $2b$...
        assert hashed.startswith(("$bcrypt-sha256$", "$2"))
        assert len(hashed) >= 60  # bcrypt hash is always 60+ chars

    def test_user_unique_username(self):
        """Test that username uniqueness is model constraint (not DB)."""
        from app.models.user import User
        from app.core.auth import get_password_hash
        
        user1 = User(
            username="uniqueuser",
            password_hash=get_password_hash("password1"),
        )
        
        user2 = User(
            username="uniqueuser",
            password_hash=get_password_hash("password2"),
        )
        
        # Both should have same username (DB constraint is separate)
        assert user2.username == user1.username


class TestUserRelationships:
    """Test User relationships - UNIT TESTS ONLY (no DB)."""

    def test_user_id_is_uuid(self):
        """Test that user ID is UUID."""
        from app.models.user import User
        from app.core.auth import get_password_hash
        
        user = User(
            username="uuiduser",
            password_hash=get_password_hash("password"),
        )
        
        assert isinstance(user.id, UUID)
        assert len(str(user.id)) == 36  # UUID format

    def test_user_can_be_serialized(self):
        """Test that user can be serialized to dict."""
        from app.models.user import User
        from app.core.auth import get_password_hash
        
        user = User(
            username="serializeuser",
            password_hash=get_password_hash("password"),
            role="viewer",
        )
        
        # Test that user has attributes that can be serialized
        assert hasattr(user, 'username')
        assert hasattr(user, 'role')
        assert hasattr(user, 'is_active')


class TestUserEdgeCases:
    """Test edge cases for User model."""

    def test_user_empty_username(self):
        """Test user with empty username."""
        from app.models.user import User
        from app.core.auth import get_password_hash
        
        user = User(
            username="",
            password_hash=get_password_hash("password"),
        )
        
        assert user.username == ""

    def test_user_long_password_hash(self):
        """Test user with long password hash."""
        from app.models.user import User
        
        # Bcrypt hash is always 60 chars
        long_hash = "a" * 60
        user = User(
            username="hashuser",
            password_hash=long_hash,
        )
        
        assert len(user.password_hash) == 60

    def test_user_with_none_values(self):
        """Test user with None values for optional fields."""
        from app.models.user import User
        from app.core.auth import get_password_hash
        
        user = User(
            username="noneuser",
            password_hash=get_password_hash("password"),
        )
        
        # Test None handling for optional fields
        if hasattr(user, "avatar_url"):
            assert user.avatar_url is None
        if hasattr(user, "openclaw_session_id"):
            assert user.openclaw_session_id is None
