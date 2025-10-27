"""
Unit tests for FletX Route Guard System
"""

import pytest
from unittest.mock import Mock
from typing import Optional

from fletx.core.routing.guards import RouteGuard
from fletx.core.routing.models import RouteInfo


class TestRouteGuard:
    """Test RouteGuard abstract base class."""

    def test_route_guard_is_abstract(self):
        """Test that RouteGuard is an abstract class."""
        with pytest.raises(TypeError):
            RouteGuard()

    def test_route_guard_has_abstract_methods(self):
        """Test that RouteGuard has required abstract methods."""
        assert hasattr(RouteGuard, 'can_activate')
        assert hasattr(RouteGuard, 'can_deactivate')
        assert hasattr(RouteGuard, 'redirect_to')


class ConcreteRouteGuard(RouteGuard):
    """Concrete implementation for testing."""
    
    def __init__(self, can_activate_result: bool = True, redirect_path: Optional[str] = None):
        self.can_activate_result = can_activate_result
        self.redirect_path = redirect_path
    
    async def can_activate(self, route: RouteInfo) -> bool:
        return self.can_activate_result
    
    async def can_deactivate(self, current_route: RouteInfo) -> bool:
        return True
    
    async def redirect_to(self, route: RouteInfo) -> Optional[str]:
        return self.redirect_path


class TestConcreteRouteGuard:
    """Test concrete RouteGuard implementation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.route_info = Mock(spec=RouteInfo)
        self.route_info.path = "/test"

    @pytest.mark.asyncio
    async def test_can_activate_allows_access(self):
        """Test can_activate when access is allowed."""
        guard = ConcreteRouteGuard(can_activate_result=True)
        result = await guard.can_activate(self.route_info)
        assert result is True

    @pytest.mark.asyncio
    async def test_can_activate_blocks_access(self):
        """Test can_activate when access is blocked."""
        guard = ConcreteRouteGuard(can_activate_result=False)
        result = await guard.can_activate(self.route_info)
        assert result is False

    @pytest.mark.asyncio
    async def test_redirect_to_with_path(self):
        """Test redirect_to when redirect path is provided."""
        guard = ConcreteRouteGuard(redirect_path="/login")
        result = await guard.redirect_to(self.route_info)
        assert result == "/login"

    @pytest.mark.asyncio
    async def test_redirect_to_without_path(self):
        """Test redirect_to when no redirect path is provided."""
        guard = ConcreteRouteGuard(redirect_path=None)
        result = await guard.redirect_to(self.route_info)
        assert result is None


class AuthenticationGuard(RouteGuard):
    """Authentication guard implementation."""
    
    def __init__(self, is_authenticated: bool = False, login_path: str = "/login"):
        self.is_authenticated = is_authenticated
        self.login_path = login_path
    
    async def can_activate(self, route: RouteInfo) -> bool:
        return self.is_authenticated
    
    async def can_deactivate(self, current_route: RouteInfo) -> bool:
        return True
    
    async def redirect_to(self, route: RouteInfo) -> Optional[str]:
        return self.login_path if not self.is_authenticated else None


class TestAuthenticationGuard:
    """Test AuthenticationGuard implementation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.route_info = Mock(spec=RouteInfo)
        self.route_info.path = "/protected"

    @pytest.mark.asyncio
    async def test_authenticated_user_can_access(self):
        """Test that authenticated users can access protected routes."""
        guard = AuthenticationGuard(is_authenticated=True)
        result = await guard.can_activate(self.route_info)
        assert result is True

    @pytest.mark.asyncio
    async def test_unauthenticated_user_cannot_access(self):
        """Test that unauthenticated users cannot access protected routes."""
        guard = AuthenticationGuard(is_authenticated=False)
        result = await guard.can_activate(self.route_info)
        assert result is False

    @pytest.mark.asyncio
    async def test_unauthenticated_user_redirected_to_login(self):
        """Test that unauthenticated users are redirected to login."""
        guard = AuthenticationGuard(is_authenticated=False, login_path="/login")
        result = await guard.redirect_to(self.route_info)
        assert result == "/login"


class PermissionGuard(RouteGuard):
    """Permission-based guard implementation."""
    
    def __init__(self, user_permissions: list = None, required_permission: str = None):
        self.user_permissions = user_permissions or []
        self.required_permission = required_permission
    
    async def can_activate(self, route: RouteInfo) -> bool:
        if not self.required_permission:
            return True
        return self.required_permission in self.user_permissions
    
    async def can_deactivate(self, current_route: RouteInfo) -> bool:
        return True
    
    async def redirect_to(self, route: RouteInfo) -> Optional[str]:
        if self.required_permission and self.required_permission not in self.user_permissions:
            return "/unauthorized"
        return None


class TestPermissionGuard:
    """Test PermissionGuard implementation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.route_info = Mock(spec=RouteInfo)
        self.route_info.path = "/admin"

    @pytest.mark.asyncio
    async def test_user_with_permission_can_access(self):
        """Test that users with required permission can access routes."""
        guard = PermissionGuard(
            user_permissions=["admin", "user"],
            required_permission="admin"
        )
        result = await guard.can_activate(self.route_info)
        assert result is True

    @pytest.mark.asyncio
    async def test_user_without_permission_cannot_access(self):
        """Test that users without required permission cannot access routes."""
        guard = PermissionGuard(
            user_permissions=["user"],
            required_permission="admin"
        )
        result = await guard.can_activate(self.route_info)
        assert result is False

    @pytest.mark.asyncio
    async def test_user_without_permission_redirected(self):
        """Test that users without permission are redirected."""
        guard = PermissionGuard(
            user_permissions=["user"],
            required_permission="admin"
        )
        result = await guard.redirect_to(self.route_info)
        assert result == "/unauthorized"


class TestRouteGuardEdgeCases:
    """Test edge cases and error conditions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.route_info = Mock(spec=RouteInfo)
        self.route_info.path = "/test"

    @pytest.mark.asyncio
    async def test_guard_with_exception(self):
        """Test guard behavior when method raises an exception."""
        class ExceptionGuard(RouteGuard):
            async def can_activate(self, route: RouteInfo) -> bool:
                raise ValueError("Test exception")
            
            async def can_deactivate(self, current_route: RouteInfo) -> bool:
                return True
            
            async def redirect_to(self, route: RouteInfo) -> Optional[str]:
                return None
        
        guard = ExceptionGuard()
        with pytest.raises(ValueError, match="Test exception"):
            await guard.can_activate(self.route_info)

    def test_guard_inheritance(self):
        """Test that guards properly inherit from RouteGuard."""
        class CustomGuard(RouteGuard):
            async def can_activate(self, route: RouteInfo) -> bool:
                return True
            
            async def can_deactivate(self, current_route: RouteInfo) -> bool:
                return True
            
            async def redirect_to(self, route: RouteInfo) -> Optional[str]:
                return None
        
        guard = CustomGuard()
        assert isinstance(guard, RouteGuard)
        assert issubclass(CustomGuard, RouteGuard)
