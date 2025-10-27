"""
Unit tests for FletX Routing Models
"""

import pytest
import flet as ft
from unittest.mock import Mock

from fletx.core.routing.models import (
    RouteInfo,
    NavigationIntent,
    RouteType,
    NavigationMode,
    RouterState,
    NavigationResult,
    IRouteResolver
)


class TestRouteInfo:
    """Test RouteInfo class."""

    def test_creation_with_defaults(self):
        """Test basic creation with defaults."""
        route = RouteInfo(path="/home")
        
        assert route.path == "/home"
        assert route.params == {}
        assert route.query == {}
        assert route.fragment is None

    def test_creation_with_all_params(self):
        """Test creation with all parameters."""
        route = RouteInfo(
            path="/user",
            params={"id": "123"},
            query={"tab": "settings"},
            data={"user": "john"},
            fragment="section"
        )
        
        assert route.params == {"id": "123"}
        assert route.query == {"tab": "settings"}
        assert route.fragment == "section"

    def test_extra_data(self):
        """Test adding and getting extra data."""
        route = RouteInfo(path="/test")
        route.add_extra("key", "value")
        
        assert route.get_extra("key") == "value"
        assert route.get_extra("missing", "default") == "default"

    def test_full_url_generation(self):
        """Test full URL generation with query and fragment."""
        route = RouteInfo(
            path="/page",
            query={"id": "1", "tab": "main"},
            fragment="top"
        )
        
        url = route.full_url
        assert url.startswith("/page?")
        assert "id=1" in url
        assert "tab=main" in url
        assert url.endswith("#top")


class TestNavigationIntent:
    """Test NavigationIntent class."""

    def test_creation_with_defaults(self):
        """Test basic creation with defaults."""
        intent = NavigationIntent(route="/home")
        
        assert intent.route == "/home"
        assert intent.data == {}
        assert intent.replace is False
        assert intent.clear_history is False
        assert intent.transition is None

    def test_creation_with_all_params(self):
        """Test creation with all parameters."""
        intent = NavigationIntent(
            route="/profile",
            data={"user_id": 123},
            replace=True,
            clear_history=True
        )
        
        assert intent.data == {"user_id": 123}
        assert intent.replace is True
        assert intent.clear_history is True


class TestEnums:
    """Test enum classes."""

    def test_route_type_values(self):
        """Test RouteType enum values."""
        assert RouteType.PAGE.value == "page"
        assert RouteType.VIEW.value == "view"
        assert RouteType.MODULE.value == "module"

    def test_navigation_mode_values(self):
        """Test NavigationMode enum values."""
        assert NavigationMode.NATIVE.value == "native"
        assert NavigationMode.VIEWS.value == "views"
        assert NavigationMode.HYBRID.value == "hybrid"

    def test_navigation_result_values(self):
        """Test NavigationResult enum values."""
        assert NavigationResult.SUCCESS.value == "success"
        assert NavigationResult.BLOCKED_BY_GUARD.value == "blocked_by_guard"
        assert NavigationResult.ERROR.value == "error"


class TestRouterState:
    """Test RouterState class."""

    def test_creation_with_defaults(self):
        """Test basic creation with defaults."""
        route = RouteInfo(path="/home")
        state = RouterState(current_route=route)
        
        assert state.current_route == route
        assert state.history == []
        assert state.forward_stack == []
        assert state.navigation_mode == NavigationMode.HYBRID
        assert state.active_views == []

    def test_mutable_collections(self):
        """Test that collections can be modified."""
        route = RouteInfo(path="/test")
        state = RouterState(current_route=route)
        
        state.history.append(RouteInfo(path="/home"))
        state.forward_stack.append(RouteInfo(path="/forward"))
        state.active_views.append(Mock(spec=ft.View))
        
        assert len(state.history) == 1
        assert len(state.forward_stack) == 1
        assert len(state.active_views) == 1


class TestIRouteResolver:
    """Test IRouteResolver interface."""

    def test_is_abstract(self):
        """Test that IRouteResolver cannot be instantiated."""
        with pytest.raises(TypeError):
            IRouteResolver()

    def test_concrete_implementation(self):
        """Test concrete implementation works."""
        class ConcreteResolver(IRouteResolver):
            def resolve(self, route_info: RouteInfo):
                return {"data": route_info.path}
        
        resolver = ConcreteResolver()
        route = RouteInfo(path="/test")
        result = resolver.resolve(route)
        
        assert result == {"data": "/test"}
        assert isinstance(resolver, IRouteResolver)


class TestIntegration:
    """Integration tests."""

    def test_navigation_flow(self):
        """Test complete navigation flow with all models."""
        # Setup initial state
        home = RouteInfo(path="/home")
        state = RouterState(current_route=home)
        
        # Create navigation intent
        intent = NavigationIntent(
            route="/profile",
            data={"user_id": 123}
        )
        
        # Simulate navigation
        profile = RouteInfo(path=intent.route, data=intent.data)
        state.history.append(state.current_route)
        state.current_route = profile
        
        # Verify
        assert state.current_route.path == "/profile"
        assert state.current_route.data["user_id"] == 123
        assert len(state.history) == 1
        assert state.history[0].path == "/home"