"""
Test package for core modules.
"""

from .test_auth import (
    TestVerifyPassword, TestGetPasswordHash, TestCreateAccessToken,
    TestDecodeToken, TestJWTErrorHandling, TestAuthFunctionsEdgeCases
)
from .test_config import (
    TestSettings, TestAllowedOrigins, TestEnvPrefix, TestGetSettings,
    TestSettingsValidation, TestSettingsEdgeCases, TestSettingsWithMock
)
from .test_database import (
    TestDatabaseEngine, TestAsyncSessionLocal, TestGetSession,
    TestCreateDbAndTables, TestDatabaseDependencies, TestDatabaseFunctions,
    TestDatabaseConfiguration, TestDatabaseEdgeCases
)

__all__ = [
    # Auth
    "TestVerifyPassword",
    "TestGetPasswordHash",
    "TestCreateAccessToken",
    "TestDecodeToken",
    "TestJWTErrorHandling",
    "TestAuthFunctionsEdgeCases",
    # Config
    "TestSettings",
    "TestAllowedOrigins",
    "TestEnvPrefix",
    "TestGetSettings",
    "TestSettingsValidation",
    "TestSettingsEdgeCases",
    "TestSettingsWithMock",
    # Database
    "TestDatabaseEngine",
    "TestAsyncSessionLocal",
    "TestGetSession",
    "TestCreateDbAndTables",
    "TestDatabaseDependencies",
    "TestDatabaseFunctions",
    "TestDatabaseConfiguration",
    "TestDatabaseEdgeCases",
]
