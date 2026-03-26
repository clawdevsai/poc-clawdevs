import pytest
from datetime import timedelta
from unittest.mock import patch, MagicMock
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


class TestGetPasswordHash:
    """Test get_password_hash function."""

    def test_get_password_hash_returns_hash(self):
        """Test that get_password_hash returns a hash."""
        from app.core.auth import get_password_hash
        
        password = "test_password"
        hashed = get_password_hash(password)
        
        # Hash should be a string longer than the password
        assert isinstance(hashed, str)
        assert len(hashed) > len(password)

    def test_get_password_hash_different_each_time(self):
        """Test that hashing the same password gives different hashes."""
        from app.core.auth import get_password_hash
        
        password = "same_password"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different (bcrypt uses salt)
        assert hash1 != hash2


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
        
        # Mock different secret key
        with patch('app.core.auth.settings') as mock_settings:
            mock_settings.secret_key = "wrong_secret"
            
            result = decode_token(token)
            assert result is None


class TestJWTErrorHandling:
    """Test JWT error handling."""

    def test_decode_token_jwt_error(self):
        """Test decode_token handles JWTError."""
        from app.core.auth import decode_token
        from unittest.mock import patch
        
        with patch('app.core.auth.jwt') as mock_jwt:
            mock_jwt.decode.side_effect = JWTError("Invalid token")
            
            result = decode_token("invalid_token")
            assert result is None
