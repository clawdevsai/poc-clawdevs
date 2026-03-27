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
Tests for API dependencies.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException
from fastapi.security import HTTPBearer


class TestGetCurrentUser:
    """Test get_current_user dependency."""

    @pytest.mark.asyncio
    async def test_get_current_user_success(self):
        """Test successful current user retrieval."""
        from app.api.deps import get_current_user
        
        mock_credentials = MagicMock()
        mock_credentials.credentials = "valid-jwt-token"
        
        mock_user = MagicMock()
        mock_user.username = "testuser"
        mock_user.is_active = True
        
        with patch('app.api.deps.decode_token', return_value={"sub": "testuser"}):
            mock_result = MagicMock()
            mock_result.first.return_value = mock_user

            mock_session = AsyncMock()
            mock_session.exec = AsyncMock(return_value=mock_result)

            user = await get_current_user(mock_credentials, mock_session)
            assert user.username == "testuser"

    @pytest.mark.asyncio
    async def test_get_current_user_no_credentials(self):
        """Test get_current_user with no credentials."""
        from app.api.deps import get_current_user
        
        with pytest.raises(HTTPException) as exc_info:
            # get_current_user expects an HTTPAuthorizationCredentials-like object
            await get_current_user(MagicMock(credentials=""), AsyncMock())
        
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self):
        """Test get_current_user with invalid token."""
        from app.api.deps import get_current_user
        
        mock_credentials = MagicMock()
        mock_credentials.credentials = "invalid-token"
        
        with patch('app.api.deps.decode_token', return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(mock_credentials, AsyncMock())
            
            assert exc_info.value.status_code == 401
            assert "Could not validate credentials" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_no_username(self):
        """Test get_current_user with token but no username."""
        from app.api.deps import get_current_user
        
        mock_credentials = MagicMock()
        mock_credentials.credentials = "token-without-username"
        
        with patch('app.api.deps.decode_token', return_value={}):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(mock_credentials, AsyncMock())
            
            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_user_not_found(self):
        """Test get_current_user when user not found."""
        from app.api.deps import get_current_user
        
        mock_credentials = MagicMock()
        mock_credentials.credentials = "token-for-nonexistent-user"
        
        with patch('app.api.deps.decode_token', return_value={"sub": "nobody"}):
            mock_result = MagicMock()
            mock_result.first.return_value = None

            mock_session = AsyncMock()
            mock_session.exec = AsyncMock(return_value=mock_result)

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(mock_credentials, mock_session)

            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_user_inactive(self):
        """Test get_current_user when user is inactive."""
        from app.api.deps import get_current_user
        
        mock_credentials = MagicMock()
        mock_credentials.credentials = "token-for-inactive-user"
        
        mock_user = MagicMock()
        mock_user.username = "inactiveuser"
        mock_user.is_active = False
        
        with patch('app.api.deps.decode_token', return_value={"sub": "inactiveuser"}):
            mock_result = MagicMock()
            mock_result.first.return_value = mock_user

            mock_session = AsyncMock()
            mock_session.exec = AsyncMock(return_value=mock_result)

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(mock_credentials, mock_session)

            assert exc_info.value.status_code == 401


class TestRequireAdmin:
    """Test require_admin dependency."""

    @pytest.mark.asyncio
    async def test_require_admin_success(self):
        """Test require_admin with admin user."""
        from app.api.deps import require_admin
        
        mock_user = MagicMock()
        mock_user.role = "admin"
        
        admin_user = await require_admin(mock_user)
        
        assert admin_user.role == "admin"

    @pytest.mark.asyncio
    async def test_require_admin_not_admin(self):
        """Test require_admin with non-admin user."""
        from app.api.deps import require_admin
        
        mock_user = MagicMock()
        mock_user.role = "viewer"
        
        with pytest.raises(HTTPException) as exc_info:
            await require_admin(mock_user)
        
        assert exc_info.value.status_code == 403
        assert "Admin access required" in exc_info.value.detail


class TestCurrentUser:
    """Test CurrentUser alias."""

    def test_current_user_alias(self):
        """Test that CurrentUser is properly defined."""
        from app.api.deps import CurrentUser
        
        # CurrentUser should be an annotated dependency
        assert CurrentUser is not None


class TestAdminUser:
    """Test AdminUser alias."""

    def test_admin_user_alias(self):
        """Test that AdminUser is properly defined."""
        from app.api.deps import AdminUser
        
        # AdminUser should be an annotated dependency
        assert AdminUser is not None


class TestBearerScheme:
    """Test bearer authentication scheme."""

    def test_bearer_scheme_exists(self):
        """Test that bearer scheme is created."""
        from app.api.deps import bearer_scheme
        
        assert bearer_scheme is not None
        assert isinstance(bearer_scheme, HTTPBearer)
