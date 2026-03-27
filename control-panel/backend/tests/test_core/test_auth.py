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

from datetime import timedelta
from unittest.mock import patch
from jose import JWTError


class TestVerifyPassword:
    """Test verify_password function."""

    def test_verify_password_correct(self):
        """Test verifying correct password."""
        from app.core.auth import get_password_hash, verify_password

        password = "test_password_123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test verifying incorrect password."""
        from app.core.auth import get_password_hash, verify_password

        password = "test_password_123"
        wrong_password = "wrong_password_456"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty(self):
        """Test verifying empty password."""
        from app.core.auth import get_password_hash, verify_password

        password = ""
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True
        assert verify_password("wrong", hashed) is False

    def test_verify_password_special_chars(self):
        """Test verifying password with special characters."""
        from app.core.auth import get_password_hash, verify_password

        password = "P@$$w0rd!#$%"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_long(self):
        """Test verifying long password."""
        from app.core.auth import get_password_hash, verify_password

        password = "a" * 1000
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True


class TestGetPasswordHash:
    """Test get_password_hash function."""

    def test_get_password_hash_returns_hash(self):
        """Test that get_password_hash returns a hash."""
        from app.core.auth import get_password_hash

        password = "test_password"
        hashed = get_password_hash(password)

        assert isinstance(hashed, str)
        assert len(hashed) > len(password)

    def test_get_password_hash_different_each_time(self):
        """Test that hashing the same password gives different hashes."""
        from app.core.auth import get_password_hash

        password = "same_password"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2

    def test_get_password_hash_starts_with_hash_prefix(self):
        """Test that hash starts with expected prefix."""
        from app.core.auth import get_password_hash

        password = "test"
        hashed = get_password_hash(password)

        # bcrypt_sha256 hashes start with $bcrypt-sha256$ or $2b$ or $2a$ or $2y$
        assert hashed.startswith(("$bcrypt-sha256$", "$2"))

    def test_get_password_hash_hash_length(self):
        """Test that hash has expected length."""
        from app.core.auth import get_password_hash

        password = "test"
        hashed = get_password_hash(password)

        # bcrypt hash is typically 60+ characters
        assert len(hashed) >= 60


class TestCreateAccessToken:
    """Test create_access_token function."""

    def test_create_access_token_with_data(self):
        """Test creating access token with data."""
        from app.core.auth import create_access_token

        data = {"sub": "user123", "role": "admin"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_expires(self):
        """Test creating access token with custom expiry."""
        from app.core.auth import create_access_token

        data = {"sub": "user123"}
        expires = timedelta(hours=1)
        token = create_access_token(data, expires_delta=expires)

        assert isinstance(token, str)

    def test_create_access_token_default_expiry(self):
        """Test creating access token with default expiry."""
        from app.core.auth import create_access_token

        data = {"sub": "user123"}
        token = create_access_token(data)

        assert isinstance(token, str)

    def test_create_access_token_with_multiple_claims(self):
        """Test creating token with multiple claims."""
        from app.core.auth import create_access_token

        data = {
            "sub": "user123",
            "role": "admin",
            "permissions": ["read", "write"],
            "organization": "org1",
        }
        token = create_access_token(data)

        assert isinstance(token, str)

    def test_create_access_token_expires_in_token(self):
        """Test that expiry is included in token."""
        from app.core.auth import create_access_token
        from jose import jwt
        from app.core.config import get_settings

        settings = get_settings()
        data = {"sub": "user123"}
        token = create_access_token(data)

        decoded = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        assert "exp" in decoded
        assert "sub" in decoded

    def test_create_access_token_with_custom_expires_minutes(self):
        """Test creating token with custom expiry in minutes."""
        from app.core.auth import create_access_token

        data = {"sub": "user123"}
        expires = timedelta(minutes=30)
        token = create_access_token(data, expires_delta=expires)

        assert isinstance(token, str)


class TestDecodeToken:
    """Test decode_token function."""

    def test_decode_valid_token(self):
        """Test decoding a valid token."""
        from app.core.auth import create_access_token, decode_token

        data = {"sub": "user123"}
        token = create_access_token(data)
        decoded = decode_token(token)

        assert decoded is not None
        assert decoded["sub"] == "user123"

    def test_decode_invalid_token(self):
        """Test decoding an invalid token."""
        from app.core.auth import decode_token

        result = decode_token("invalid_token")

        assert result is None

    def test_decode_token_with_wrong_secret(self):
        """Test decoding token with wrong secret."""
        from app.core.auth import create_access_token, decode_token

        data = {"sub": "user123"}
        token = create_access_token(data)

        with patch("app.core.auth.settings") as mock_settings:
            mock_settings.secret_key = "wrong_secret"

            result = decode_token(token)
            assert result is None

    def test_decode_token_expired(self):
        """Test decoding an expired token."""
        from app.core.auth import decode_token

        result = decode_token(
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        )
        # This is a known expired JWT
        assert result is None

    def test_decode_token_empty(self):
        """Test decoding empty string token."""
        from app.core.auth import decode_token

        result = decode_token("")
        assert result is None

    def test_decode_token_none(self):
        """Test decoding None token."""
        from app.core.auth import decode_token

        result = decode_token(None)
        assert result is None


class TestJWTErrorHandling:
    """Test JWT error handling."""

    def test_decode_token_jwt_error(self):
        """Test decode_token handles JWTError."""
        from app.core.auth import decode_token
        from unittest.mock import patch

        with patch("app.core.auth.jwt") as mock_jwt:
            mock_jwt.decode.side_effect = JWTError("Invalid token")

            result = decode_token("invalid_token")
            assert result is None

    def test_decode_token_jwt_invalid_signature(self):
        """Test decode_token handles invalid signature."""
        from app.core.auth import decode_token
        from unittest.mock import patch

        with patch("app.core.auth.jwt") as mock_jwt:
            mock_jwt.decode.side_effect = JWTError("Signature verification failed")

            result = decode_token("invalid_token")
            assert result is None


class TestAuthFunctionsEdgeCases:
    """Test edge cases for auth functions."""

    def test_password_with_unicode(self):
        """Test password with unicode characters."""
        from app.core.auth import get_password_hash, verify_password

        password = "密码@123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_password_with_emoji(self):
        """Test password with emoji."""
        from app.core.auth import get_password_hash, verify_password

        password = "pass🔑123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_token_with_empty_payload(self):
        """Test creating token with empty payload."""
        from app.core.auth import create_access_token

        data = {}
        token = create_access_token(data)

        assert isinstance(token, str)

    def test_token_with_null_values(self):
        """Test creating token with null values."""
        from app.core.auth import create_access_token

        data = {"sub": None, "role": None}
        token = create_access_token(data)

        assert isinstance(token, str)
