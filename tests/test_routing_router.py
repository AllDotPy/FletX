"""
Unit tests for FletX Router System
"""

import pytest
import flet as ft
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any

from fletx.core.routing.router import FletXRouter
from fletx.core.routing.models import (
    RouteInfo, NavigationIntent, RouterState,
    NavigationMode, NavigationResult
)
from fletx.core.routing.config import RouterConfig, RouteDefinition
from fletx.core.routing.guards import RouteGuard
from fletx.core.routing.middleware import RouteMiddleware
from fletx.core.routing.transitions import RouteTransition, TransitionType
from fletx.core.page import FletXPage


class MockPage(Mock):
    """Mock Flet Page for testing."""
    
    def __init__(self):
        super().__init__(spec=ft.Page)
        self.route = "/"
        self.controls = []
        self.views = []
        self.on_route_change = None
        self.on_view_pop = None
        
    def update(self):
        pass
    
    def clean(self):
        self.controls = []
    
    def add(self, *controls):
        self.controls.extend(controls)


class MockComponent(FletXPage):
    """Mock component for testing."""
    
    def __init__(self):
        super().__init__()
        self.route_info = None
        self.did_mount_called = False
    
    def did_mount(self):
        self.did_mount_called = True
    
    def _build_page(self):
        pass


class TestFletXRouterInitialization:
    """Test FletXRouter initialization."""

    def test_router_creation(self):
        """Test basic router creation."""
        page = MockPage()
        config = RouterConfig()
        
        router = FletXRouter(page, config)
        
        assert router.page == page
        assert router.config == config
        assert isinstance(router.state, RouterState)
        assert router.state.navigation_mode == NavigationMode.HYBRID

    def test_flet_integration_setup(self):
        """Test Flet integration is set up correctly."""
        page = MockPage()
        router = FletXRouter(page)
        
        assert page.on_route_change is not None
        assert page.on_view_pop is not None

    @patch('fletx.core.routing.router.get_event_loop')
    def test_router_initialize_singleton(self, mock_loop):
        """Test router singleton initialization."""
        mock_loop.return_value.create_task = Mock()
        page = MockPage()
        
        router = FletXRouter.initialize(page, initial_route="/home")
        
        assert FletXRouter._instance == router
        assert FletXRouter.get_instance() == router

    def test_get_instance_before_init_raises_error(self):
        """Test getting instance before initialization raises error."""
        FletXRouter._instance = None
        
        with pytest.raises(RuntimeError, match="Router not initialized"):
            FletXRouter.get_instance()


class TestRouterNavigation:
    """Test router navigation functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.page = MockPage()
        self.config = RouterConfig()
        self.router = FletXRouter(self.page, self.config)
        
        # Add test route
        self.config.add_route("/test", MockComponent)

    @pytest.mark.asyncio
    async def test_navigate_to_existing_route(self):
        """Test navigation to an existing route."""
        result = await self.router.navigate("/test")
        
        assert result == NavigationResult.SUCCESS
        assert self.router.state.current_route.path == "/test"

    @pytest.mark.asyncio
    async def test_navigate_with_data(self):
        """Test navigation with data."""
        data = {"user_id": 123}
        result = await self.router.navigate("/test", data=data)
        
        assert result == NavigationResult.SUCCESS
        assert self.router.state.current_route.data == data

    @pytest.mark.asyncio
    async def test_navigate_to_nonexistent_route(self):
        """Test navigation to non-existent route."""
        result = await self.router.navigate("/nonexistent")
        
        assert result == NavigationResult.ERROR

    @pytest.mark.asyncio
    async def test_navigate_with_query_params(self):
        """Test navigation with query parameters."""
        result = await self.router.navigate("/test?id=1&tab=main")
        
        assert result == NavigationResult.SUCCESS
        assert self.router.state.current_route.query["id"] == "1"
        assert self.router.state.current_route.query["tab"] == "main"

    @pytest.mark.asyncio
    async def test_navigate_with_replace(self):
        """Test navigation with replace flag."""
        await self.router.navigate("/test")
        history_len = len(self.router.state.history)
        
        await self.router.navigate("/test", replace=True)
        
        assert len(self.router.state.history) == history_len

    @pytest.mark.asyncio
    async def test_navigate_with_clear_history(self):
        """Test navigation with clear history flag."""
        await self.router.navigate("/test")
        self.router.state.history.append(RouteInfo(path="/old"))
        
        await self.router.navigate("/test", clear_history=True)
        
        assert len(self.router.state.history) == 0


class TestNavigationIntent:
    """Test navigation with intents."""

    def setup_method(self):
        """Set up test fixtures."""
        self.page = MockPage()
        self.config = RouterConfig()
        self.router = FletXRouter(self.page, self.config)
        self.config.add_route("/test", MockComponent)

    @pytest.mark.asyncio
    async def test_navigate_with_intent(self):
        """Test navigation using NavigationIntent."""
        intent = NavigationIntent(
            route="/test",
            data={"key": "value"},
            replace=True
        )
        
        result = await self.router.navigate_with_intent(intent)
        
        assert result == NavigationResult.SUCCESS
        assert self.router.state.current_route.path == "/test"


class TestHistoryManagement:
    """Test navigation history management."""

    def setup_method(self):
        """Set up test fixtures."""
        self.page = MockPage()
        self.config = RouterConfig()
        self.router = FletXRouter(self.page, self.config)
        
        self.config.add_route("/home", MockComponent)
        self.config.add_route("/about", MockComponent)

    @pytest.mark.asyncio
    async def test_history_tracking(self):
        """Test that navigation history is tracked."""
        await self.router.navigate("/home")
        await self.router.navigate("/about")
        
        assert len(self.router.state.history) == 1
        assert self.router.state.history[0].path == "/home"

    def test_can_go_back(self):
        """Test can_go_back detection."""
        assert self.router.can_go_back() is False
        
        self.router.state.history.append(RouteInfo(path="/home"))
        assert self.router.can_go_back() is True

    def test_can_go_forward(self):
        """Test can_go_forward detection."""
        assert self.router.can_go_forward() is False
        
        self.router.state.forward_stack.append(RouteInfo(path="/next"))
        assert self.router.can_go_forward() is True

    @patch('fletx.core.routing.router.run_async')
    def test_go_back(self, mock_run_async):
        """Test go_back functionality."""
        self.router.state.history.append(RouteInfo(path="/previous"))
        
        result = self.router.go_back()
        
        assert result is True
        assert len(self.router.state.forward_stack) == 1

    @patch('fletx.core.routing.router.run_async')
    def test_go_forward(self, mock_run_async):
        """Test go_forward functionality."""
        self.router.state.forward_stack.append(RouteInfo(path="/next"))
        
        result = self.router.go_forward()
        
        assert result is True
        assert len(self.router.state.history) == 1

    def test_get_history(self):
        """Test getting navigation history."""
        self.router.state.history.append(RouteInfo(path="/home"))
        self.router.state.history.append(RouteInfo(path="/about"))
        
        history = self.router.get_history()
        
        assert len(history) == 2
        assert history[0].path == "/home"


class TestGuardsAndMiddleware:
    """Test route guards and middleware."""

    def setup_method(self):
        """Set up test fixtures."""
        self.page = MockPage()
        self.config = RouterConfig()
        self.router = FletXRouter(self.page, self.config)

    @pytest.mark.asyncio
    async def test_add_global_guard(self):
        """Test adding global guard."""
        guard = Mock(spec=RouteGuard)
        guard.can_activate = AsyncMock(return_value=True)
        guard.can_deactivate = AsyncMock(return_value=True)
        
        self.router.add_global_guard(guard)
        
        assert guard in self.router._global_guards

    @pytest.mark.asyncio
    async def test_add_global_middleware(self):
        """Test adding global middleware."""
        middleware = Mock(spec=RouteMiddleware)
        middleware.before_navigation = AsyncMock(return_value=None)
        
        self.router.add_global_middleware(middleware)
        
        assert middleware in self.router._global_middleware

    @pytest.mark.asyncio
    async def test_guard_blocks_navigation(self):
        """Test that guard can block navigation."""
        self.config.add_route("/protected", MockComponent)
        
        guard = Mock(spec=RouteGuard)
        guard.can_activate = AsyncMock(return_value=False)
        guard.redirect_to = AsyncMock(return_value=None)
        guard.can_deactivate = AsyncMock(return_value=True)
        
        self.router.add_global_guard(guard)
        
        result = await self.router.navigate("/protected")
        
        assert result == NavigationResult.BLOCKED_BY_GUARD


class TestNavigationModes:
    """Test different navigation modes."""

    def setup_method(self):
        """Set up test fixtures."""
        self.page = MockPage()
        self.config = RouterConfig()
        self.router = FletXRouter(self.page, self.config)
        self.config.add_route("/test", MockComponent)

    def test_set_navigation_mode(self):
        """Test setting navigation mode."""
        self.router.set_navigation_mode(NavigationMode.VIEWS)
        
        assert self.router.state.navigation_mode == NavigationMode.VIEWS

    @pytest.mark.asyncio
    async def test_views_mode_creates_views(self):
        """Test that VIEWS mode creates Flet views."""
        self.router.set_navigation_mode(NavigationMode.VIEWS)
        
        await self.router.navigate("/test")
        
        assert len(self.page.views) > 0
        assert len(self.router.state.active_views) > 0


class TestRouterUtilities:
    """Test router utility methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.page = MockPage()
        self.config = RouterConfig()
        self.router = FletXRouter(self.page, self.config)

    def test_get_current_route(self):
        """Test getting current route."""
        self.router.state.current_route = RouteInfo(path="/test")
        
        current = self.router.get_current_route()
        
        assert current.path == "/test"

    @pytest.mark.asyncio
    async def test_component_lifecycle_called(self):
        """Test that component lifecycle methods are called."""
        component = MockComponent()
        route_info = RouteInfo(path="/test")
        
        route_def = RouteDefinition(path="/test", component=lambda ri: component)
        
        await self.router._apply_transition_and_update(
            component, route_info, None
        )
        
        assert component.did_mount_called is True


class TestFletIntegration:
    """Test Flet native integration."""

    def setup_method(self):
        """Set up test fixtures."""
        self.page = MockPage()
        self.config = RouterConfig()
        self.router = FletXRouter(self.page, self.config)
        self.config.add_route("/test", MockComponent)

    @pytest.mark.asyncio
    async def test_flet_route_sync(self):
        """Test that Flet's page.route is synced."""
        await self.router.navigate("/test")
        
        # In HYBRID or NATIVE mode, page.route should be updated
        if self.router.state.navigation_mode in [NavigationMode.HYBRID, NavigationMode.NATIVE]:
            assert self.page.route == "/test"

    @patch('fletx.core.routing.router.get_event_loop')
    def test_flet_route_change_handler(self, mock_loop):
        """Test Flet route change handler."""
        mock_loop.return_value.create_task = Mock()
        
        event = Mock()
        event.route = "/new-route"
        
        self.router._on_flet_route_change(event)
        
        mock_loop.return_value.create_task.assert_called_once()