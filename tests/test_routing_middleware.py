"""
Unit tests for FletX Route Middleware System
"""

import pytest
from unittest.mock import Mock, AsyncMock
from typing import Optional

from fletx.core.routing.middleware import RouteMiddleware
from fletx.core.routing.models import RouteInfo, NavigationIntent


class TestRouteMiddleware:
    """Test RouteMiddleware base class."""

    def test_route_middleware_creation(self):
        """Test creating a route middleware instance."""
        middleware = RouteMiddleware()
        assert middleware is not None

    @pytest.mark.asyncio
    async def test_before_navigation_default(self):
        """Test default before_navigation behavior."""
        middleware = RouteMiddleware()
        from_route = Mock(spec=RouteInfo)
        to_route = Mock(spec=RouteInfo)
        
        result = await middleware.before_navigation(from_route, to_route)
        assert result is None

    @pytest.mark.asyncio
    async def test_after_navigation_default(self):
        """Test default after_navigation behavior."""
        middleware = RouteMiddleware()
        route_info = Mock(spec=RouteInfo)
        
        # Should not raise any exception
        await middleware.after_navigation(route_info)

    @pytest.mark.asyncio
    async def test_on_navigation_error_default(self):
        """Test default on_navigation_error behavior."""
        middleware = RouteMiddleware()
        error = Exception("Test error")
        route_info = Mock(spec=RouteInfo)
        
        # Should not raise any exception
        await middleware.on_navigation_error(error, route_info)


class LoggingMiddleware(RouteMiddleware):
    """Example logging middleware implementation."""
    
    def __init__(self):
        self.logs = []
    
    async def before_navigation(self, from_route: RouteInfo, to_route: RouteInfo) -> Optional[NavigationIntent]:
        self.logs.append(f"Before: {from_route.path} -> {to_route.path}")
        return None
    
    async def after_navigation(self, route_info: RouteInfo) -> None:
        self.logs.append(f"After: {route_info.path}")
    
    async def on_navigation_error(self, error: Exception, route_info: RouteInfo) -> None:
        self.logs.append(f"Error: {error} on {route_info.path}")


class TestLoggingMiddleware:
    """Test LoggingMiddleware implementation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.middleware = LoggingMiddleware()
        self.from_route = Mock(spec=RouteInfo)
        self.from_route.path = "/home"
        self.to_route = Mock(spec=RouteInfo)
        self.to_route.path = "/about"

    @pytest.mark.asyncio
    async def test_before_navigation_logging(self):
        """Test that before_navigation logs correctly."""
        result = await self.middleware.before_navigation(self.from_route, self.to_route)
        
        assert result is None
        assert len(self.middleware.logs) == 1
        assert "Before: /home -> /about" in self.middleware.logs[0]

    @pytest.mark.asyncio
    async def test_after_navigation_logging(self):
        """Test that after_navigation logs correctly."""
        await self.middleware.after_navigation(self.to_route)
        
        assert len(self.middleware.logs) == 1
        assert "After: /about" in self.middleware.logs[0]

    @pytest.mark.asyncio
    async def test_error_logging(self):
        """Test that error logging works correctly."""
        error = ValueError("Test error")
        await self.middleware.on_navigation_error(error, self.to_route)
        
        assert len(self.middleware.logs) == 1
        assert "Error: Test error on /about" in self.middleware.logs[0]


class RedirectMiddleware(RouteMiddleware):
    """Example redirect middleware implementation."""
    
    def __init__(self, redirect_path: Optional[str] = None):
        self.redirect_path = redirect_path
    
    async def before_navigation(self, from_route: RouteInfo, to_route: RouteInfo) -> Optional[NavigationIntent]:
        if self.redirect_path:
            return NavigationIntent(route=self.redirect_path)
        return None


class TestRedirectMiddleware:
    """Test RedirectMiddleware implementation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.from_route = Mock(spec=RouteInfo)
        self.from_route.path = "/home"
        self.to_route = Mock(spec=RouteInfo)
        self.to_route.path = "/admin"

    @pytest.mark.asyncio
    async def test_no_redirect(self):
        """Test middleware with no redirect."""
        middleware = RedirectMiddleware()
        result = await middleware.before_navigation(self.from_route, self.to_route)
        assert result is None

    @pytest.mark.asyncio
    async def test_with_redirect(self):
        """Test middleware with redirect."""
        middleware = RedirectMiddleware(redirect_path="/login")
        result = await middleware.before_navigation(self.from_route, self.to_route)
        
        assert result is not None
        assert isinstance(result, NavigationIntent)
        assert result.route == "/login"


class AnalyticsMiddleware(RouteMiddleware):
    """Example analytics middleware implementation."""
    
    def __init__(self):
        self.page_views = []
        self.errors = []
    
    async def after_navigation(self, route_info: RouteInfo) -> None:
        self.page_views.append({
            'path': route_info.path,
            'timestamp': '2024-01-01T00:00:00Z'
        })
    
    async def on_navigation_error(self, error: Exception, route_info: RouteInfo) -> None:
        self.errors.append({
            'error': str(error),
            'path': route_info.path,
            'timestamp': '2024-01-01T00:00:00Z'
        })


class TestAnalyticsMiddleware:
    """Test AnalyticsMiddleware implementation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.middleware = AnalyticsMiddleware()
        self.route_info = Mock(spec=RouteInfo)
        self.route_info.path = "/dashboard"

    @pytest.mark.asyncio
    async def test_track_page_view(self):
        """Test that page views are tracked."""
        await self.middleware.after_navigation(self.route_info)
        
        assert len(self.middleware.page_views) == 1
        assert self.middleware.page_views[0]['path'] == "/dashboard"

    @pytest.mark.asyncio
    async def test_track_error(self):
        """Test that errors are tracked."""
        error = RuntimeError("Navigation failed")
        await self.middleware.on_navigation_error(error, self.route_info)
        
        assert len(self.middleware.errors) == 1
        assert self.middleware.errors[0]['error'] == "Navigation failed"
        assert self.middleware.errors[0]['path'] == "/dashboard"


class TestRouteMiddlewareEdgeCases:
    """Test edge cases and error conditions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.middleware = RouteMiddleware()
        self.route_info = Mock(spec=RouteInfo)
        self.route_info.path = "/test"

    @pytest.mark.asyncio
    async def test_middleware_with_exception(self):
        """Test middleware behavior when method raises an exception."""
        class ExceptionMiddleware(RouteMiddleware):
            async def before_navigation(self, from_route: RouteInfo, to_route: RouteInfo) -> Optional[NavigationIntent]:
                raise ValueError("Middleware error")
        
        middleware = ExceptionMiddleware()
        with pytest.raises(ValueError, match="Middleware error"):
            await middleware.before_navigation(self.route_info, self.route_info)

    @pytest.mark.asyncio
    async def test_middleware_with_none_routes(self):
        """Test middleware behavior with None route parameters."""
        middleware = RouteMiddleware()
        
        # Should handle None gracefully or raise appropriate error
        with pytest.raises(AttributeError):
            await middleware.before_navigation(None, self.route_info)

    def test_middleware_inheritance(self):
        """Test that middleware properly inherits from RouteMiddleware."""
        class CustomMiddleware(RouteMiddleware):
            async def before_navigation(self, from_route: RouteInfo, to_route: RouteInfo) -> Optional[NavigationIntent]:
                return None
        
        middleware = CustomMiddleware()
        assert isinstance(middleware, RouteMiddleware)
        assert issubclass(CustomMiddleware, RouteMiddleware)


class TestMiddlewareIntegration:
    """Integration tests for middleware."""

    def setup_method(self):
        """Set up test fixtures."""
        self.from_route = Mock(spec=RouteInfo)
        self.from_route.path = "/home"
        self.to_route = Mock(spec=RouteInfo)
        self.to_route.path = "/profile"

    @pytest.mark.asyncio
    async def test_multiple_middleware_chain(self):
        """Test multiple middleware working together."""
        logging_middleware = LoggingMiddleware()
        analytics_middleware = AnalyticsMiddleware()
        
        # Test before navigation
        result1 = await logging_middleware.before_navigation(self.from_route, self.to_route)
        result2 = await analytics_middleware.before_navigation(self.from_route, self.to_route)
        
        assert result1 is None
        assert result2 is None
        assert len(logging_middleware.logs) == 1
        
        # Test after navigation
        await logging_middleware.after_navigation(self.to_route)
        await analytics_middleware.after_navigation(self.to_route)
        
        assert len(logging_middleware.logs) == 2
        assert len(analytics_middleware.page_views) == 1

    @pytest.mark.asyncio
    async def test_middleware_with_redirect_chain(self):
        """Test middleware chain with redirect."""
        redirect_middleware = RedirectMiddleware(redirect_path="/login")
        logging_middleware = LoggingMiddleware()
        
        # First middleware redirects
        result = await redirect_middleware.before_navigation(self.from_route, self.to_route)
        assert result is not None
        assert result.route == "/login"
        
        # Second middleware should not be called due to redirect
        # This simulates the router stopping the chain on redirect
        assert len(logging_middleware.logs) == 0
        