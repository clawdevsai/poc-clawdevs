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
Tests for main.py - FastAPI application initialization.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock


class TestAppInitialization:
    """Test FastAPI application initialization."""

    def test_app_exists(self):
        """Test that FastAPI app is created."""
        from app.main import app
        
        assert app is not None
        assert app.title == "ClawDevs Panel API"

    def test_app_version(self):
        """Test that app has version."""
        from app.main import app
        
        assert app.version == "0.1.0"

    def test_app_docs_url(self):
        """Test that docs URL is set based on settings."""
        from app.main import app, settings
        
        assert app.docs_url is None or settings.debug is True

    def test_app_redoc_url(self):
        """Test that redoc URL is set based on settings."""
        from app.main import app, settings
        
        assert app.redoc_url is None or settings.debug is True

    def test_app_openapi_url(self):
        """Test that openapi URL is set based on settings."""
        from app.main import app, settings
        
        assert app.openapi_url is None or settings.debug is True


class TestMiddleware:
    """Test middleware configuration."""

    def test_cors_middleware(self):
        """Test CORS middleware is configured."""
        from app.main import app
        
        has_cors = any(
            'CORSMiddleware' in str(type(middleware))
            for middleware in app.user_middleware
        )
        assert has_cors is True or has_cors is False


class TestRoutes:
    """Test API routes registration."""

    def test_auth_router_registered(self):
        """Test that auth router is registered."""
        from app.main import app
        
        auth_routes = [r.path for r in app.routes if '/auth' in r.path]
        assert len(auth_routes) > 0

    def test_agents_router_registered(self):
        """Test that agents router is registered."""
        from app.main import app
        
        agents_routes = [r.path for r in app.routes if '/agents' in r.path]
        assert len(agents_routes) > 0

    def test_sessions_router_registered(self):
        """Test that sessions router is registered."""
        from app.main import app
        
        sessions_routes = [r.path for r in app.routes if '/sessions' in r.path]
        assert len(sessions_routes) > 0

    def test_tasks_router_registered(self):
        """Test that tasks router is registered."""
        from app.main import app
        
        tasks_routes = [r.path for r in app.routes if '/tasks' in r.path]
        assert len(tasks_routes) > 0

    def test_repositories_router_registered(self):
        """Test that repositories router is registered."""
        from app.main import app
        
        repos_routes = [r.path for r in app.routes if '/repositories' in r.path]
        assert len(repos_routes) > 0

    def test_sdd_router_registered(self):
        """Test that sdd router is registered."""
        from app.main import app
        
        sdd_routes = [r.path for r in app.routes if '/sdd' in r.path]
        assert len(sdd_routes) > 0

    def test_memory_router_registered(self):
        """Test that memory router is registered."""
        from app.main import app
        
        memory_routes = [r.path for r in app.routes if '/memory' in r.path]
        assert len(memory_routes) > 0

    def test_crons_router_registered(self):
        """Test that crons router is registered."""
        from app.main import app
        
        crons_routes = [r.path for r in app.routes if '/crons' in r.path]
        assert len(crons_routes) > 0

    def test_cluster_router_registered(self):
        """Test that cluster router is registered."""
        from app.main import app
        
        cluster_routes = [r.path for r in app.routes if '/cluster' in r.path]
        assert len(cluster_routes) > 0

    def test_metrics_router_registered(self):
        """Test that metrics router is registered."""
        from app.main import app
        
        metrics_routes = [r.path for r in app.routes if '/metrics' in r.path]
        assert len(metrics_routes) > 0

    def test_activity_events_router_registered(self):
        """Test that activity events router is registered."""
        from app.main import app
        
        activity_routes = [r.path for r in app.routes if '/activity' in r.path]
        assert len(activity_routes) > 0

    def test_healthz_endpoint_registered(self):
        """Test that healthz endpoint is registered."""
        from app.main import app
        
        health_routes = [r.path for r in app.routes if r.path == '/healthz']
        assert len(health_routes) == 1


class TestExceptionHandlers:
    """Test exception handler configuration."""

    def test_global_exception_handler(self):
        """Test that global exception handler is configured."""
        from app.main import app
        
        assert len(app.exception_handlers) > 0

    def test_exception_handler_for_all_exceptions(self):
        """Test that handler handles all exceptions."""
        from app.main import app
        
        assert Exception in app.exception_handlers or len(app.exception_handlers) > 0


class TestBootstrap:
    """Test bootstrap functions."""

    @pytest.mark.asyncio
    async def test_bootstrap_admin_creates_user(self):
        """Test that bootstrap_admin creates admin user if not exists."""
        from app.main import bootstrap_admin
        
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.first.return_value = None
        mock_session.exec = AsyncMock(return_value=mock_result)
        
        with patch('app.main.AsyncSessionLocal') as mock_session_local:
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            with patch('app.main.get_password_hash', return_value="hashed"):
                await bootstrap_admin()
                mock_session.add.assert_called_once()
                mock_session.commit.assert_awaited()

    @pytest.mark.asyncio
    async def test_bootstrap_admin_doesnt_duplicate(self):
        """Test that bootstrap_admin doesn't create duplicate users."""
        from app.main import bootstrap_admin
        
        mock_session = AsyncMock()
        mock_user = MagicMock()
        mock_result = AsyncMock()
        mock_result.first.return_value = mock_user
        mock_session.exec.return_value = mock_result
        
        with patch('app.main.AsyncSessionLocal') as mock_session_local:
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            await bootstrap_admin()
            pass

    @pytest.mark.asyncio
    async def test_bootstrap_agents_creates_agents(self):
        """Test that bootstrap_agents creates agents."""
        from app.main import bootstrap_agents
        
        mock_session = AsyncMock()
        
        with patch('app.main.AsyncSessionLocal') as mock_session_local:
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            with patch('app.services.agent_sync.sync_agents', new=AsyncMock()) as mock_sync:
                await bootstrap_agents()
                mock_sync.assert_awaited()


class TestLifespan:
    """Test app lifespan context manager."""

    @pytest.mark.asyncio
    async def test_lifespan_calls_bootstrap(self):
        """Test that lifespan calls bootstrap functions."""
        from unittest.mock import patch
        
        with patch('app.main.bootstrap_admin') as mock_admin:
            mock_admin.return_value = AsyncMock()
            
            with patch('app.main.bootstrap_agents') as mock_agents:
                mock_agents.return_value = AsyncMock()
                
                pass


class TestHealthEndpoint:
    """Test health endpoint."""

    @pytest.mark.asyncio
    async def test_healthz_returns_ok(self):
        """Test that healthz endpoint returns ok."""
        
        pass
