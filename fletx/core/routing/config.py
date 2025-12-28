"""
Advanced Route Configuration for FletX

Enhanced route configuration system supporting nested routes, 
module routing, and complex route hierarchies.
"""

from dataclasses import dataclass, field
import re
from typing import (
    Dict, List, Type, Optional, Callable, 
    Union, Any
)
from fletx.core.routing.models import (
    RouteType,
)
from fletx.core.routing.guards import RouteGuard
from fletx.core.routing.middleware import RouteMiddleware
from fletx.core.page import FletXPage
from fletx.utils import get_logger


####
##      ROUTE DEFINITION CLASS
#####
@dataclass
class RouteDefinition:
    """Complete route definition with all metadata."""

    path: str
    component: Union[Type, Callable]
    route_type: RouteType = RouteType.PAGE
    guards: List['RouteGuard'] = field(default_factory=list)
    middleware: List['RouteMiddleware'] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)
    children: List['RouteDefinition'] = field(default_factory=list)
    parent: Optional['RouteDefinition'] = None
    resolve: Dict[str, Callable] = field(default_factory=dict)  # Data resolvers
    meta: Dict[str, Any] = field(default_factory=dict)


####
##      ROUTE PATTERN
#####
class RoutePattern:
    """Handles route pattern matching with parameters and wildcards."""
    
    def __init__(self, pattern: str):
        self.pattern = pattern
        self.param_names = []
        self.regex_pattern = self._compile_pattern()
    
    def _compile_pattern(self) -> re.Pattern:
        """Compile route pattern to regex."""

        pattern = self.pattern
        
        # Handle parameters (:param)
        param_pattern = r':([a-zA-Z_][a-zA-Z0-9_]*)'
        matches = re.findall(param_pattern, pattern)
        self.param_names = matches
        
        # Replace parameters with regex groups
        regex_pattern = re.sub(param_pattern, r'([^/]+)', pattern)
        
        # Handle wildcards (*path)
        regex_pattern = regex_pattern.replace('*', '(.*)')
        
        # Ensure exact match
        regex_pattern = f'^{regex_pattern}$'
        
        return re.compile(regex_pattern)
    
    def match(self, path: str) -> Optional[Dict[str, str]]:
        """Match path against pattern and extract parameters."""

        match = self.regex_pattern.match(path)
        if not match:
            return None
        
        params = {}
        for i, param_name in enumerate(self.param_names):
            params[param_name] = match.group(i + 1)
        
        return params


####
##      ROUTE CONFIG
#####
class RouterConfig:
    """Advanced router configuration manager."""
    
    def __init__(self):
        self._routes: Dict[str, RouteDefinition] = {}
        self._route_patterns: List[tuple[RoutePattern, RouteDefinition]] = []
        self._modules: Dict[str, 'ModuleRouter'] = {}

    @property
    def logger(cls):
        return get_logger('FletX.RouterConfig')
    
    def add_route(
        self,
        path: str,
        component: Union[Type[FletXPage], Callable],
        *,
        route_type: RouteType = RouteType.PAGE,
        guards: List[RouteGuard] = None,
        middleware: List[RouteMiddleware] = None,
        data: Dict = None,
        children: List[RouteDefinition] = None,
        resolve: Dict[str, Callable] = None,
        meta: Dict = None
    ) -> RouteDefinition:
        """Add a route to the configuration."""
        
        route_def = RouteDefinition(
            path = path,
            component = component,
            route_type = route_type,
            guards = guards or [],
            middleware = middleware or [],
            data = data or {},
            children = children or [],
            resolve = resolve or {},
            meta = meta or {}
        )
        
        # Set parent-child relationships
        for child in route_def.children:
            child.parent = route_def
        
        self._routes[path] = route_def
        
        # Add to pattern matching if route has parameters
        if ':' in path or '*' in path:
            pattern = RoutePattern(path)
            self._route_patterns.append((pattern, route_def))

        self.logger.debug(f"Route added: {path} -> {component}")
        return route_def
    
    def add_routes(self, routes: List[Dict]) -> None:
        """Add multiple routes from configuration list."""

        for route_config in routes:
            self.add_route(**route_config)
    
    def add_nested_routes(
        self, 
        parent_path: str, 
        routes: List[Dict]
    ) -> None:
        """Add nested routes under a parent path."""

        parent_route = self.get_route(parent_path)
        if not parent_route:
            raise ValueError(f"Parent route not found: {parent_path}")
        
        for route_config in routes:
            child_path = f"{parent_path.rstrip('/')}/{route_config['path'].lstrip('/')}"
            child_route = self.add_route(child_path, **route_config)
            child_route.parent = parent_route
            parent_route.children.append(child_route)
    
    def add_module_routes(
        self, 
        base_path: str, 
        module_router: 'ModuleRouter'
    ) -> None:
        """Add routes from a module router."""

        self._modules[base_path] = module_router
        
        # Register module routes with base path prefix
        for route in module_router.get_routes():
            # build full path
            full_path = f"{base_path.rstrip('/')}/{route.path.lstrip('/')}"

            route.meta.update(
                {'module': module_router, 'original_path': route.path}
            )

            module_route = RouteDefinition(
                path = full_path,
                component = route.component,
                route_type = RouteType.MODULE,
                guards = route.guards,
                middleware = route.middleware,
                data = route.data,
                meta = route.meta
            )
            self._routes[full_path] = module_route

            # Add subrouter patterns too
            self._route_patterns.extend(module_router._config._route_patterns)
    
    def get_route(self, path: str) -> Optional[RouteDefinition]:
        """Get route definition by exact path match."""

        return self._routes.get(path)
    
    def match_route(self, path: str) -> Optional[tuple[RouteDefinition, Dict[str, str]]]:
        """Match path against all route patterns."""

        # Try exact match first
        exact_route = self.get_route(path)
        if exact_route:
            return exact_route, {}
        
        # Try pattern matching
        for pattern, route_def in self._route_patterns:
            params = pattern.match(path)

            if params is not None:
                return route_def, params
        
        return None
    
    def get_all_routes(self) -> Dict[str, RouteDefinition]:
        """Get all registered routes."""

        return self._routes.copy()
    
    def get_routes_by_type(self, route_type: RouteType) -> List[RouteDefinition]:
        """Get routes filtered by type."""

        return [
            route for route in self._routes.values() 
            if route.route_type == route_type
        ]
    
    def get_child_routes(self, parent_path: str) -> List[RouteDefinition]:
        """Get child routes of a parent route."""

        parent = self.get_route(parent_path)
        return parent.children if parent else []
    
    def get_route_hierarchy(self, path: str) -> List[RouteDefinition]:
        """Get the full hierarchy of a route (parents + self)."""

        route = self.get_route(path)
        if not route:
            return []
        
        hierarchy = []
        current = route
        while current:
            hierarchy.insert(0, current)
            current = current.parent
        
        return hierarchy


####
##      MODULE ROUTER (SUB-ROUTER)
#####
class ModuleRouter:
    """Sub-router for handling module-specific routes."""
    
    name: str = ''
    base_path: str = ''
    routes: List[Dict[str,Any]] = []
    sub_routers: List['ModuleRouter']
    is_root: bool = False
    _config: RouterConfig = RouterConfig()

    def __init__(self):
        # Add routes to the config.
        self.add_routes(self.routes)

        # Add subrouters 
        self.add_subrouters(self.sub_routers)

    @property
    def logger(self):
        return get_logger(f'FletX.ModuleRouter.{self.name}')
    
    def add_route(
        self, 
        path: str, 
        component: Union[Type[FletXPage], Callable], 
        **kwargs
    ) -> RouteDefinition:
        """Add route to this module."""

        return self._config.add_route(path, component, **kwargs)
    
    def add_routes(self, routes: List[Dict]) -> None:
        """Add multiple routes to this module."""

        self._config.add_routes(routes)
    
    def get_routes(self) -> List[RouteDefinition]:
        """Get all routes in this module."""

        return list(self._config.get_all_routes().values())
    
    def match_route(self, path: str) -> Optional[tuple[RouteDefinition, Dict[str, str]]]:
        """Match route within this module."""

        return self._config.match_route(path)
    
    def add_subrouters(self,routers: List[Type['ModuleRouter']]):
        """Add Sub routers to the router"""

        for router in routers:
            # Instanciate the router to recursively
            # register its routes and subrouters
            router_instance = router()

            # Then add it to the config
            self._config.add_module_routes(
                router_instance.base_path,
                router_instance
            )


# Global router configuration instance
router_config = RouterConfig()
