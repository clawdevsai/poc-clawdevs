import pytest
from unittest.mock import patch, MagicMock
import os


class TestSettings:
    """Test Settings class."""

    def test_settings_default_database_url(self):
        """Test default database URL."""
        from app.core.config import Settings
        
        settings = Settings()
        assert "postgresql+asyncpg" in settings.database_url
        assert "clawdevs-panel-db" in settings.database_url
        assert "5432" in settings.database_url
        assert "clawdevs_panel" in settings.database_url

    def test_settings_default_redis_url(self):
        """Test default Redis URL."""
        from app.core.config import Settings
        
        settings = Settings()
        assert "redis://" in settings.redis_url
        assert "clawdevs-panel-redis" in settings.redis_url
        assert "6379" in settings.redis_url

    def test_settings_default_auth_config(self):
        """Test default authentication settings."""
        from app.core.config import Settings
        
        settings = Settings()
        assert len(settings.secret_key) >= 32  # Minimum length
        assert settings.algorithm == "HS256"
        assert settings.access_token_expire_minutes == 7 * 24 * 60  # 7 days

    def test_settings_default_admin_credentials(self):
        """Test default admin credentials."""
        from app.core.config import Settings
        
        settings = Settings()
        assert settings.admin_username == "admin"
        assert "change-me" in settings.admin_password

    def test_settings_openclaw_gateway(self):
        """Test OpenClaw gateway settings."""
        from app.core.config import Settings
        
        settings = Settings()
        assert "clawdevs-ai" in settings.openclaw_gateway_url
        assert "18789" in settings.openclaw_gateway_url

    def test_settings_openclaw_data_path(self):
        """Test OpenClaw data path."""
        from app.core.config import Settings
        
        settings = Settings()
        assert settings.openclaw_data_path == "/data/openclaw"

    def test_settings_kubernetes_namespace(self):
        """Test Kubernetes namespace."""
        from app.core.config import Settings
        
        settings = Settings()
        assert settings.k8s_namespace == "default"

    def test_settings_debug_false(self):
        """Test debug mode is disabled by default."""
        from app.core.config import Settings
        
        settings = Settings()
        assert settings.debug is False

    def test_settings_all_fields_present(self):
        """Test that all expected fields are present."""
        from app.core.config import Settings
        
        settings = Settings()
        
        # Check all required fields
        assert hasattr(settings, 'database_url')
        assert hasattr(settings, 'redis_url')
        assert hasattr(settings, 'secret_key')
        assert hasattr(settings, 'algorithm')
        assert hasattr(settings, 'access_token_expire_minutes')
        assert hasattr(settings, 'admin_username')
        assert hasattr(settings, 'admin_password')
        assert hasattr(settings, 'openclaw_gateway_url')
        assert hasattr(settings, 'openclaw_gateway_token')
        assert hasattr(settings, 'github_token')
        assert hasattr(settings, 'github_org')
        assert hasattr(settings, 'github_default_repository')
        assert hasattr(settings, 'openclaw_data_path')
        assert hasattr(settings, 'k8s_namespace')
        assert hasattr(settings, 'debug')
        assert hasattr(settings, 'allowed_origins')


class TestAllowedOrigins:
    """Test allowed origins configuration."""

    def test_allowed_origins_default(self):
        """Test default allowed origins."""
        from app.core.config import Settings
        
        settings = Settings()
        assert len(settings.allowed_origins) > 0
        assert "http://localhost:3000" in settings.allowed_origins
        assert "http://clawdevs-panel-frontend:3000" in settings.allowed_origins

    def test_allowed_origins_contains_frontend(self):
        """Test that frontend URL is in allowed origins."""
        from app.core.config import Settings
        
        settings = Settings()
        assert "clawdevs-panel-frontend" in settings.allowed_origins[1]

    def test_allowed_origins_is_list(self):
        """Test that allowed_origins is a list."""
        from app.core.config import Settings
        
        settings = Settings()
        assert isinstance(settings.allowed_origins, list)


class TestEnvPrefix:
    """Test environment variable prefix."""

    def test_env_prefix_is_panel(self):
        """Test that settings use PANEL_ prefix."""
        from app.core.config import Settings
        
        settings = Settings()
        assert settings.model_config.get("env_prefix") == "PANEL_"

    def test_env_file_is_env(self):
        """Test that settings use .env file."""
        from app.core.config import Settings
        
        settings = Settings()
        assert settings.model_config.get("env_file") == ".env"


class TestGetSettings:
    """Test get_settings function."""

    def test_get_settings_returns_settings(self):
        """Test that get_settings returns Settings instance."""
        from app.core.config import get_settings
        
        settings = get_settings()
        assert settings is not None

    def test_get_settings_is_cached(self):
        """Test that get_settings is cached (lru_cache)."""
        from app.core.config import get_settings
        
        settings1 = get_settings()
        settings2 = get_settings()
        
        assert settings1 is settings2  # Same instance (cached)

    def test_get_settings_same_as_direct(self):
        """Test that get_settings returns same as Settings()."""
        from app.core.config import get_settings, Settings
        
        direct = Settings()
        from_func = get_settings()
        
        assert direct.database_url == from_func.database_url
        assert direct.redis_url == from_func.redis_url


class TestSettingsValidation:
    """Test settings validation."""

    def test_database_url_format(self):
        """Test database URL format."""
        from app.core.config import Settings
        
        settings = Settings()
        assert "+" in settings.database_url  # async driver
        assert "@" in settings.database_url  # host
        assert "/" in settings.database_url  # database name

    def test_redis_url_format(self):
        """Test Redis URL format."""
        from app.core.config import Settings
        
        settings = Settings()
        assert "redis://" in settings.redis_url
        assert "@" in settings.redis_url  # Has password

    def test_secret_key_length(self):
        """Test secret key minimum length."""
        from app.core.config import Settings
        
        settings = Settings()
        assert len(settings.secret_key) >= 32

    def test_algorithm_is_hs256(self):
        """Test algorithm is HS256."""
        from app.core.config import Settings
        
        settings = Settings()
        assert settings.algorithm == "HS256"

    def test_access_token_expire_minutes(self):
        """Test access token expire minutes is 7 days."""
        from app.core.config import Settings
        
        settings = Settings()
        expected = 7 * 24 * 60  # 7 days in minutes
        assert settings.access_token_expire_minutes == expected

    def test_openclaw_gateway_url_format(self):
        """Test OpenClaw gateway URL format."""
        from app.core.config import Settings
        
        settings = Settings()
        assert settings.openclaw_gateway_url.startswith("http")
        assert "18789" in settings.openclaw_gateway_url


class TestSettingsEdgeCases:
    """Test edge cases for settings."""

    def test_settings_multiple_instances(self):
        """Test creating multiple Settings instances."""
        from app.core.config import Settings
        
        settings1 = Settings()
        settings2 = Settings()
        
        # Both should have same values
        assert settings1.database_url == settings2.database_url

    def test_settings_field_types(self):
        """Test field types are correct."""
        from app.core.config import Settings
        
        settings = Settings()
        
        assert isinstance(settings.database_url, str)
        assert isinstance(settings.redis_url, str)
        assert isinstance(settings.secret_key, str)
        assert isinstance(settings.algorithm, str)
        assert isinstance(settings.admin_username, str)
        assert isinstance(settings.admin_password, str)
        assert isinstance(settings.openclaw_gateway_url, str)
        assert isinstance(settings.k8s_namespace, str)
        assert isinstance(settings.debug, bool)
        assert isinstance(settings.allowed_origins, list)
        assert isinstance(settings.access_token_expire_minutes, int)


class TestSettingsWithMock:
    """Test settings with mocked environment."""

    def test_settings_with_mock_env(self):
        """Test settings with mocked environment variables."""
        from app.core.config import Settings
        
        with patch.dict(os.environ, {
            "PANEL_DATABASE_URL": "postgresql+asyncpg://test:test@localhost:5432/testdb",
            "PANEL_SECRET_KEY": "test-secret-key-for-testing"
        }):
            settings = Settings()
            
            assert "test" in settings.database_url
            assert "test-secret-key-for-testing" in settings.secret_key
