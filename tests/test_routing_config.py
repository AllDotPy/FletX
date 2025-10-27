"""
Unit tests for FletX Routing Configuration Module
"""

import pytest
import re
from unittest.mock import Mock, patch

from fletx.core.routing.config import (
    RouteDefinition,
    RoutePattern,
    RouterConfig,
    ModuleRouter,
    router_config
)
from fletx.core.routing.models import RouteType
from fletx.core.routing.guards import RouteGuard
from fletx.core.routing.middleware import RouteMiddleware


class TestRouteDefinition:
    """Test RouteDefinition class."""

    def test_creation_with_defaults(self):
        """Test basic creation with default values."""
        component = Mock()
        route_def = RouteDefinition(path="/test", component=component)
        
        assert route_def.path == "/test"
        assert route_def.component == component
        assert route_def.route_type == RouteType.PAGE
        assert route_def.guards == []
        assert route_def.middleware == []
        assert route_def.data == {}
        assert route_def.children == []
        assert route_def.parent is None

    def test_creation_with_all_params(self):
        """Test creation with all parameters."""
        guard, middleware = Mock(spec=RouteGuard), Mock(spec=RouteMiddleware)
        
        route_def = RouteDefinition(
            path="/test",
            component=Mock(),
            route_type=RouteType.MODULE,
            guards=[guard],
            middleware=[middleware],
            data={"key": "value"},
            resolve={"resolver": Mock()},
            meta={"meta_key": "meta_value"}
        )
        
        assert route_def.route_type == RouteType.MODULE
        assert route_def.guards == [guard]
        assert route_def.data == {"key": "value"}
        assert "resolver" in route_def.resolve

    def test_parent_child_relationship(self):
        """Test parent-child relationships."""
        parent = RouteDefinition(path="/parent", component=Mock())
        child = RouteDefinition(path="/child", component=Mock(), parent=parent)
        parent.children.append(child)
        
        assert child.parent == parent
        assert child in parent.children


class TestRoutePattern:
    """Test RoutePattern class."""

    def test_simple_path(self):
        """Test simple path matching."""
        pattern = RoutePattern("/test")
        
        assert pattern.match("/test") == {}
        assert pattern.match("/other") is None

    def test_parameters(self):
        """Test parameter extraction."""
        pattern = RoutePattern("/user/:id/profile/:section")
        
        assert pattern.param_names == ["id", "section"]
        assert pattern.match("/user/123/profile/settings") == {
            "id": "123", "section": "settings"
        }
        assert pattern.match("/user/123") is None

    def test_wildcard(self):
        """Test wildcard matching."""
        pattern = RoutePattern("/files/*")
        
        assert pattern.match("/files/doc.pdf") == {}
        assert pattern.match("/files/folder/file.txt") == {}
        assert pattern.match("/files") is None

    def test_mixed_params_and_wildcard(self):
        """Test mixed parameters and wildcards."""
        pattern = RoutePattern("/api/:version/*")
        
        assert pattern.match("/api/v1/users") == {"version": "v1"}
        assert pattern.match("/api/v2/data/export") == {"version": "v2"}

    def test_regex_compilation(self):
        """Test regex pattern compilation."""
        pattern = RoutePattern("/user/:id")
        
        assert isinstance(pattern.regex_pattern, re.Pattern)
        assert pattern.regex_pattern.match("/user/123").group(1) == "123"


class TestRouterConfig:
    """Test RouterConfig class."""

    def setup_method(self):
        self.config = RouterConfig()
        self.component = Mock()

    def test_add_route_simple(self):
        """Test adding a simple route."""
        route_def = self.config.add_route("/test", self.component)
        
        assert route_def.path == "/test"
        assert "/test" in self.config._routes

    def test_add_route_with_params(self):
        """Test adding route with parameters."""
        self.config.add_route("/user/:id", self.component)
        
        assert len(self.config._route_patterns) == 1
        assert self.config._route_patterns[0][0].pattern == "/user/:id"

    def test_add_multiple_routes(self):
        """Test adding multiple routes."""
        routes = [
            {"path": "/route1", "component": self.component},
            {"path": "/route2", "component": self.component},
        ]
        self.config.add_routes(routes)
        
        assert len(self.config._routes) == 2

    def test_add_nested_routes(self):
        """Test nested route creation."""
        parent = self.config.add_route("/parent", self.component)
        nested = [{"path": "/child", "component": self.component}]
        
        self.config.add_nested_routes("/parent", nested)
        
        child = self.config._routes["/parent/child"]
        assert child.parent == parent
        assert child in parent.children

    def test_nested_routes_parent_not_found(self):
        """Test error when parent route doesn't exist."""
        with pytest.raises(ValueError, match="Parent route not found"):
            self.config.add_nested_routes("/nonexistent", [])

    def test_add_module_routes(self):
        """Test adding module routes."""
        module = Mock(spec=ModuleRouter)
        module.get_routes.return_value = [
            RouteDefinition(path="/mod", component=self.component)
        ]
        module._config._route_patterns = []
        
        self.config.add_module_routes("/api", module)
        
        route = self.config._routes["/api/mod"]
        assert route.route_type == RouteType.MODULE
        assert route.meta["module"] == module

    def test_get_route(self):
        """Test getting route by path."""
        route = self.config.add_route("/test", self.component)
        
        assert self.config.get_route("/test") == route
        assert self.config.get_route("/nonexistent") is None

    def test_match_route_exact(self):
        """Test exact route matching."""
        route = self.config.add_route("/test", self.component)
        
        matched, params = self.config.match_route("/test")
        assert matched == route
        assert params == {}

    def test_match_route_pattern(self):
        """Test pattern route matching."""
        route = self.config.add_route("/user/:id", self.component)
        
        matched, params = self.config.match_route("/user/123")
        assert matched == route
        assert params == {"id": "123"}

    def test_match_route_no_match(self):
        """Test no route matches."""
        self.config.add_route("/test", self.component)
        
        assert self.config.match_route("/other") is None

    def test_get_routes_by_type(self):
        """Test filtering routes by type."""
        page = self.config.add_route("/page", self.component, route_type=RouteType.PAGE)
        module = self.config.add_route("/mod", self.component, route_type=RouteType.MODULE)
        
        assert self.config.get_routes_by_type(RouteType.PAGE) == [page]
        assert self.config.get_routes_by_type(RouteType.MODULE) == [module]

    def test_get_child_routes(self):
        """Test getting child routes."""
        self.config.add_route("/parent", self.component)
        self.config.add_nested_routes("/parent", [
            {"path": "/child", "component": self.component}
        ])
        
        assert len(self.config.get_child_routes("/parent")) == 1
        assert self.config.get_child_routes("/nonexistent") == []

    def test_get_route_hierarchy(self):
        """Test getting route hierarchy."""
        gp = self.config.add_route("/gp", self.component)
        p = self.config.add_route("/gp/p", self.component)
        c = self.config.add_route("/gp/p/c", self.component)
        
        p.parent, c.parent = gp, p
        gp.children.append(p)
        p.children.append(c)
        
        hierarchy = self.config.get_route_hierarchy("/gp/p/c")
        assert hierarchy == [gp, p, c]


class TestModuleRouter:
    """Test ModuleRouter class."""

    def setup_method(self):
        self.component = Mock()

    def test_initialization(self):
        """Test module router initialization."""
        class TestRouter(ModuleRouter):
            name = "test"
            base_path = "/test"
            routes = [{"path": "/r1", "component": Mock()}]
            sub_routers = []
        
        router = TestRouter()
        assert router.name == "test"
        assert len(router.get_routes()) == 1

    def test_add_route(self):
        """Test adding route to module."""
        class TestRouter(ModuleRouter):
            name = "test"
            base_path = "/test"
            routes = []
            sub_routers = []
        
        router = TestRouter()
        route = router.add_route("/new", self.component)
        
        assert route.path == "/new"

    def test_match_route(self):
        """Test route matching in module."""
        class TestRouter(ModuleRouter):
            name = "test"
            base_path = "/test"
            routes = [{"path": "/user/:id", "component": Mock()}]
            sub_routers = []
        
        router = TestRouter()
        matched, params = router.match_route("/user/123")
        
        assert params == {"id": "123"}

    def test_add_subrouters(self):
        """Test adding sub-routers."""
        class SubRouter(ModuleRouter):
            name = "sub"
            base_path = "/sub"
            routes = [{"path": "/r", "component": Mock()}]
            sub_routers = []
        
        class MainRouter(ModuleRouter):
            name = "main"
            base_path = "/main"
            routes = []
            sub_routers = [SubRouter]
        
        router = MainRouter()
        routes = router.get_routes()
        
        assert len(routes) == 1
        assert routes[0].path == "/sub/r"


class TestGlobalConfig:
    """Test global router configuration."""

    def test_singleton(self):
        """Test router_config is singleton."""
        from fletx.core.routing.config import router_config as c1, router_config as c2
        assert c1 is c2


class TestIntegration:
    """Integration tests."""

    def setup_method(self):
        self.config = RouterConfig()
        self.component = Mock()

    def test_complex_routing(self):
        """Test complex routing scenario."""
        self.config.add_route("/", self.component)
        self.config.add_route("/user/:id", self.component)
        self.config.add_route("/files/*", self.component)
        
        assert self.config.match_route("/")[0] is not None
        _, params = self.config.match_route("/user/123")
        assert params == {"id": "123"}
        assert self.config.match_route("/files/doc.pdf")[0] is not None

    def test_deep_hierarchy(self):
        """Test deep route hierarchy."""
        self.config.add_route("/app", self.component)
        self.config.add_nested_routes("/app", [
            {"path": "/dashboard", "component": self.component}
        ])
        self.config.add_nested_routes("/app/dashboard", [
            {"path": "/settings", "component": self.component}
        ])
        
        hierarchy = self.config.get_route_hierarchy("/app/dashboard/settings")
        assert len(hierarchy) == 3