"""
FletX Main Router System

Advanced routing system with support for nested routes, dynamic routing,
navigation with data, history management, guards, middleware, and transitions.
Integrates with Flet's native navigation system (Page.route and Views).
"""

import flet as ft
from typing import Dict, Any, Optional, List, Union, Callable
from urllib.parse import parse_qs, urlparse
import asyncio
from contextlib import asynccontextmanager

from fletx.core.routing.models import (
    RouteInfo, NavigationIntent, RouterState, NavigationMode, 
    NavigationResult
)
from fletx.core.routing.config import (
    RouterConfig, router_config, 
    RouteGuard, RouteMiddleware
)
from fletx.core.page import FletXPage
from fletx.core.routing.transitions import RouteTransition, TransitionType
from fletx.utils.exceptions import RouteNotFoundError, NavigationError

from fletx.utils import get_logger, get_event_loop, run_async


####
##      MAIN FLETX ROUTER CLASS
#####
class FletXRouter:
    """
    Advanced Router for FletX Framework
    
    Provides comprehensive routing with:
    - Main router with sub-routers for modules
    - Nested routes support
    - Dynamic routing with parameters
    - Navigation with data (intents)
    - Navigation history management
    - Route guards and middleware
    - Page transitions
    - Integration with Flet's native navigation
    """
    
    _instance: Optional['FletXRouter'] = None
    
    def __init__(
        self, 
        page: ft.Page, 
        config: Optional[RouterConfig] = None
    ):
        """Initialize the router with a Flet page."""

        self.page = page
        self.config = config or router_config
        self.state = RouterState(
            current_route = RouteInfo(path='/'),
            navigation_mode = NavigationMode.HYBRID
        )
        self._resolvers: Dict[str, Callable] = {}
        self._global_guards: List[RouteGuard] = []
        self._global_middleware: List[RouteMiddleware] = []
        
        # Setup Flet integration
        self._setup_flet_integration()

        # setup "to" method for those who still using 
        # an old version of fletx router
        self.to = self.navigate

    @property
    def logger(cls):
        return get_logger('FletX.Router')
    
    @classmethod
    def get_instance(cls) -> 'FletXRouter':
        """Get the singleton router instance."""

        if cls._instance is None:
            raise RuntimeError(
                "Router not initialized. Call initialize() first."
            )
        return cls._instance
    
    @classmethod
    def initialize(
        cls, 
        page: ft.Page, 
        initial_route: str = '/',
        config: RouterConfig = None
    ) -> 'FletXRouter':
        """Initialize the global router instance."""

        cls._instance = cls(page, config)
        # Navigate to current root
        get_event_loop().create_task(
            cls._instance.navigate(initial_route, replace = True)
        )
            
        return cls._instance
    
    def _setup_flet_integration(self):
        """Setup integration with Flet's native navigation."""

        # Handle Flet's native route changes
        self.page.on_route_change = self._on_flet_route_change
        self.page.on_view_pop = self._on_flet_view_pop
        
        # Set initial route
        initial_route = self.page.route or "/"
        self.state.current_route = RouteInfo(path=initial_route)
    
    def _on_flet_route_change(self, e: ft.RouteChangeEvent):
        """Handle Flet's native route change events."""

        if self.state.navigation_mode in [NavigationMode.NATIVE, NavigationMode.HYBRID]:
            self.logger.debug(f"Flet route changed to: {e.route}")
            # Sync with our internal state
            get_event_loop().create_task(
                self.navigate(e.route, sync_only=True)
            )
    
    def _on_flet_view_pop(self, e: ft.ViewPopEvent):
        """Handle Flet's native view pop events."""

        if self.state.navigation_mode in [NavigationMode.VIEWS, NavigationMode.HYBRID]:
            self.logger.debug("Flet view popped")
            self.go_back()

    def set_navigation_mode(self, mode: NavigationMode):
        """Set Router Navigation mode"""

        self.state.navigation_mode = mode
    
    # @worker_task
    async def navigate(
        self,
        route: str,
        *,
        data: Dict[str, Any] = None,
        replace: bool = False,
        clear_history: bool = False,
        transition: Optional[RouteTransition] = None,
        sync_only: bool = False
    ) -> NavigationResult:
        """
        Navigate to a route with comprehensive options.
        
        Args:
            route: Target route path
            data: Navigation intent data
            replace: Replace current route in history
            clear_history: Clear navigation history
            transition: Custom transition animation
            sync_only: Only sync state, don't trigger navigation
        """
        try:
            # Parse route
            parsed = urlparse(route)
            path = parsed.path
            query_params = parse_qs(parsed.query)
            fragment = parsed.fragment
            
            # Create route info
            route_info = RouteInfo(
                path = path,
                query = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()},
                data = data or {},
                fragment = fragment
            )
            
            # Find matching route
            match_result = self.config.match_route(path)
            if not match_result:
                raise RouteNotFoundError(f"Route not found: {path}")
            
            route_def, params = match_result
            route_info.params = params
            
            # Skip navigation if sync_only
            if sync_only:
                self.state.current_route = route_info
                return NavigationResult.SUCCESS

            # Check deactivation guards for current route
            if not await self._check_deactivation_guards():
                return NavigationResult.BLOCKED_BY_GUARD
        
            # Check activation guards for target route
            guard_result = await self._check_activation_guards(route_info, route_def)
            if guard_result != NavigationResult.SUCCESS:
                return guard_result
        
            # Run middleware before navigation
            middleware_result = await self._run_before_middleware(
                self.state.current_route, route_info
            )
            if middleware_result:

                # Middleware requested redirect
                return await self.navigate(
                    middleware_result.route,
                    data = middleware_result.data,
                    replace = middleware_result.replace,
                    transition = middleware_result.transition
                )
        
            # Resolve route data
            resolved_data = await self._resolve_route_data(route_info, route_def)
            route_info.data.update(resolved_data)
            
            # Update history
            if clear_history:
                self.state.history.clear()
                self.state.forward_stack.clear()
            elif not replace:
                self.state.history.append(self.state.current_route)
                self.state.forward_stack.clear()
        
            # Create and setup component
            component_instance = await self._create_component(route_def, route_info)
            self.logger.debug(f'created Component: {component_instance.__class__.__name__}')
            
            # Apply transition and update UI
            await self._apply_transition_and_update(
                component_instance, 
                route_info, 
                transition or self._get_default_transition(route_def)
            )
        
            # Update state
            self.state.current_route = route_info
            
            # Update Flet's native routing
            if self.state.navigation_mode in [NavigationMode.NATIVE, NavigationMode.HYBRID]:
                self.page.route = path
                self.page.update()
            
            # Run middleware after navigation
            await self._run_after_middleware(route_info)
            
            self.logger.info(f"Navigation successful: {path}")
            return NavigationResult.SUCCESS
            
        except Exception as e:
            self.logger.error(f"Navigation failed: {e}", exc_info=True)
            await self._run_error_middleware(e, route_info)
            return NavigationResult.ERROR
    
    # @parallel_task(priority = Priority.HIGH)
    async def navigate_with_intent(self, intent: NavigationIntent) -> NavigationResult:
        """Navigate using a navigation intent object."""

        return await self.navigate(
            intent.route,
            data = intent.data,
            replace = intent.replace,
            clear_history = intent.clear_history,
            transition = intent.transition
        )
    
    def go_back(self) -> bool:
        """Navigate back in history."""

        if not self.state.history:
            self._logger.warning("No previous route in history")
            return False
        
        previous_route = self.state.history.pop()
        self.state.forward_stack.append(self.state.current_route)
        
        # Use async task for navigation
        run_async(
            lambda: self.navigate(previous_route.path, replace = True)
        )
        return True
    
    def go_forward(self) -> bool:
        """Navigate forward in history."""

        if not self.state.forward_stack:
            self._logger.warning("No forward route in history")
            return False
        
        forward_route = self.state.forward_stack.pop()
        self.state.history.append(self.state.current_route)
        
        # Use async task for navigation
        run_async(
            lambda: self.navigate(forward_route.path, replace = True)
        )
        return True
    
    def can_go_back(self) -> bool:
        """Check if can navigate back."""

        return len(self.state.history) > 0
    
    def can_go_forward(self) -> bool:
        """Check if can navigate forward."""

        return len(self.state.forward_stack) > 0
    
    def get_current_route(self) -> RouteInfo:
        """Get current route information."""

        return self.state.current_route
    
    def get_history(self) -> List[RouteInfo]:
        """Get navigation history."""

        return self.state.history.copy()
    
    def add_global_guard(self, guard: RouteGuard):
        """Add a global route guard."""

        self._global_guards.append(guard)
    
    def add_global_middleware(
        self, 
        middleware: RouteMiddleware
    ):
        """Add global middleware."""

        self._global_middleware.append(middleware)
    
    def set_navigation_mode(self, mode: NavigationMode):
        """Set navigation mode for Flet integration."""

        self.state.navigation_mode = mode
        self._logger.debug(f"Navigation mode set to: {mode}")
    
    # @worker_task(priority = Priority.HIGH)
    async def _check_deactivation_guards(self) -> bool:
        """Check if current route can be deactivated."""

        current_route_def = self.config.get_route(self.state.current_route.path)
        if not current_route_def:
            return True
        
        # Check route-specific guards
        for guard in current_route_def.guards:
            if not await guard.can_deactivate(self.state.current_route):
                return False
        
        # Check global guards
        for guard in self._global_guards:
            if not await guard.can_deactivate(self.state.current_route):
                return False
        
        return True
    
    # @worker_task(priority = Priority.HIGH)
    async def _check_activation_guards(
        self, 
        route_info: RouteInfo, 
        route_def
    ) -> NavigationResult:
        """Check if route can be activated."""

        all_guards = route_def.guards + self._global_guards
        
        for guard in all_guards:
            if not await guard.can_activate(route_info):
                redirect_path = await guard.redirect_to(route_info)
                if redirect_path:
                    await self.navigate(redirect_path, replace=True)
                    return NavigationResult.REDIRECTED
                return NavigationResult.BLOCKED_BY_GUARD
        
        return NavigationResult.SUCCESS
    
    # @worker_task(priority = Priority.HIGH)
    async def _run_before_middleware(
        self, 
        from_route: RouteInfo, 
        to_route: RouteInfo
    ) -> Optional[NavigationIntent]:
        """Run before navigation middleware."""

        all_middleware = self._global_middleware
        
        # Add route-specific middleware
        route_def = self.config.get_route(to_route.path)
        if route_def:
            all_middleware.extend(route_def.middleware)
        
        for middleware in all_middleware:
            result = await middleware.before_navigation(from_route, to_route)
            if result:
                return result
        
        return None
    
    # @worker_task(priority = Priority.HIGH)
    async def _run_after_middleware(self, route_info: RouteInfo):
        """Run after navigation middleware."""

        all_middleware = self._global_middleware
        
        route_def = self.config.get_route(route_info.path)
        if route_def:
            all_middleware.extend(route_def.middleware)
        
        for middleware in all_middleware:
            await middleware.after_navigation(route_info)
    
    # @worker_task(priority = Priority.HIGH)
    async def _run_error_middleware(
        self, 
        error: Exception, 
        route_info: RouteInfo
    ):
        """Run error middleware."""

        all_middleware = self._global_middleware
        
        route_def = self.config.get_route(route_info.path)
        if route_def:
            all_middleware.extend(route_def.middleware)
        
        for middleware in all_middleware:
            await middleware.on_navigation_error(error, route_info)
    
    # @worker_task(priority = Priority.HIGH)
    async def _resolve_route_data(
        self, 
        route_info: RouteInfo, 
        route_def
    ) -> Dict[str, Any]:
        """Resolve route data using resolvers."""

        resolved_data = {}
        
        for key, resolver in route_def.resolve.items():
            try:
                if asyncio.iscoroutinefunction(resolver):
                    resolved_data[key] = await resolver(route_info)
                else:
                    resolved_data[key] = resolver(route_info)
            except Exception as e:
                self._logger.error(f"Data resolver failed for {key}: {e}")
        
        return resolved_data
    
    # @worker_task(priority = Priority.HIGH)
    async def _create_component(
        self, 
        route_def, 
        route_info: RouteInfo
    ):
        """Create and initialize the route component."""

        component_class = route_def.component
        
        if (
            isinstance(component_class, type) 
            and 
            issubclass(component_class, FletXPage)
        ):
            # FletX page
            instance = component_class()
            if hasattr(instance, 'route_info'):
                instance.route_info = route_info
            return instance
        
        elif callable(component_class):
            # Callable component
            return await component_class(route_info)
        
        else:
            raise NavigationError(f"Invalid component type: {type(component_class)}")
    
    # @worker_task(priority = Priority.CRITICAL)
    async def _apply_transition_and_update(
        self, 
        component: FletXPage, 
        route_info: RouteInfo, 
        transition: Optional[RouteTransition]
    ):
        """Apply transition and update the UI."""

        content = component
        # print('Sortie............................')

        if hasattr(component, '_build_page'):
            content._build_page()
        
        # Handle different navigation modes
        if self.state.navigation_mode == NavigationMode.VIEWS:
            self.logger.debug(
                f"router navigation mode is {self.state.navigation_mode}."
                "FletX will use Flet Views navigation."
            )

            # Use Flet Views
            view = ft.View(
                route = route_info.path,
                controls = [content] if not isinstance(content, list) else content
            )
            self.page.views.append(view)
            self.state.active_views.append(view)

        else:

            self.logger.debug(
                f"router navigation mode is {self.state.navigation_mode}. "
                "FletX will apply a direct page update."
            )

            # Get current controls for transition
            current_controls = self.page.controls.copy() if self.page.controls else None

            # Direct page update
            if transition and transition.type != TransitionType.NONE:
                content = await transition.apply(
                    self.page, 
                    [content] if not isinstance(content, list) else content,
                    current_controls
                )

            self.page.clean()
            if isinstance(content, list):
                self.page.add(*content)
            else:
                self.page.add(content)

        self.page.update()
        
        # Call lifecycle methods
        if hasattr(component, 'did_mount'):
            try:
                if asyncio.iscoroutinefunction(component.did_mount):
                    await component.did_mount()
                else:
                    component.did_mount()
            except Exception as e:
                self._logger.error(f"did_mount() failed: {e}")
    
    def _get_default_transition(self, route_def) -> Optional[RouteTransition]:
        """Get default transition for route."""

        if 'transition' in route_def.meta:
            return route_def.meta['transition']
        return None
