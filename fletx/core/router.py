"""
Routing System for FletX

A routing system for the FletX Framework, enabling efficient and organized 
navigation between different pages and screens of the application.
"""

import re
import flet as ft
from threading import Lock
from urllib.parse import parse_qs, urlparse
from typing import Dict, Any, Optional, Type, List

from fletx.core.routing.guards import RouteGuard
from fletx.core.routing.middleware import RouteMiddleware
from fletx.core.routing.transitions import RouteTransition
from fletx.core.route_config import RouteConfig
from fletx.core.page import FletXPage
from fletx.utils.exceptions import RouteNotFoundError, NavigationError
from fletx.core.routing.models import RouteInfo
from fletx.utils import get_logger

import warnings

warnings.warn(
    'fletx.core.router.FletXRouter is deprecated and will be removed in next releases.'
    'Use fletx.routing.get_router instead.'
)


####
##      FLETX ROUTER CLASS
#####
class FletXRouter:
    """
    Main Router for FletX
    The main router for FletX, responsible for managing route
    s and navigating between different pages of the application, 
    providing a seamless and consistent user experience.
    """
    
    _instance = None
    _page: ft.Page = None
    _current_route: str = "/"
    _route_history: List[str] = []
    _logger = get_logger('FletX.Router')
    _middleware = RouteMiddleware()
    _guards: Dict[str, List[RouteGuard]] = {}

    @property
    def logger(cls):
        if not cls._logger:
            cls._logger = get_logger('FletX.Router')
        return cls._logger
    
    @classmethod
    def initialize(cls, page: ft.Page, initial_route: str = "/"):
        """
        Configures and sets up the router to manage routes 
        and navigation of the application, laying the foundation 
        for smooth and efficient navigation.
        """

        cls._page = page
        cls._route_history = []
        cls.to(initial_route, replace=True)

    @classmethod
    def add_route_guard(cls, path: str, guard: RouteGuard):
        """
        Associates a guard (or a protection function) with a specific route, 
        allowing to control access to this route and define custom navigation rules.
        """

        if path not in cls._guards:
            cls._guards[path] = []
        cls._guards[path].append(guard)
    
    @classmethod
    def to(
        cls,
        route: str,
        arguments: Dict[str, Any] = None,
        replace: bool = False,
        transition: Optional[RouteTransition] = None,
        _redirect_depth: int = 0  # Internal recursion protection
    ):
        """Enables complex and flexible navigation between routes."""

        warnings.warn(
            'fletx.core.router.FletXRouter.to() is deprecated '
            'and will be removed in next releases.'
            'Use fletx.routing.navigate() instead.'
        )

        MAX_REDIRECT_DEPTH = 10 
        
        try:
            # 1. Excessive recursion protection
            if _redirect_depth > MAX_REDIRECT_DEPTH:
                raise NavigationError(
                    f"Maximum redirect depth ({MAX_REDIRECT_DEPTH}) exceeded"
                )

            # 2. Noemalize the path
            parsed = urlparse(route)
            clean_path = parsed.path
            query_params = parse_qs(parsed.query)
            
            # 3. Current route checking (loop avoidance)
            if (clean_path == cls._current_route and 
                not arguments and 
                not replace and
                _redirect_depth == 0):
                cls._logger.debug(f"Already on route: {clean_path}")
                return

            # 4.  Preparing information for Route
            route_info = RouteInfo(
                path = clean_path,
                query = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()},
                params = arguments or {}
            )

            # 5. Checking guards
            guards = cls._get_guards_for_route(clean_path)

            for guard in guards:
                if not guard.can_activate(route_info):
                    # Get redirect path
                    redirect_path = guard.redirect(route_info)
                    if redirect_path == clean_path:  # Avoiding redirection loop
                        raise NavigationError(
                            f"Guard redirect loop detected on {clean_path}"
                        )
                    
                    # Then navigate to redirect_path
                    return cls.to(
                        redirect_path,
                        replace = True,
                        transition = transition,
                        _redirect_depth = _redirect_depth + 1
                    )

            # 6. Middleware before navigation
            redirect = cls._middleware.before_navigation(route_info,None)
            if redirect and redirect != clean_path:  # Avoid auto-redirection

                return cls.to(
                    redirect,
                    replace = replace,
                    transition = transition,
                    _redirect_depth = _redirect_depth + 1
                )

            # 7. Fing and instanciate the page
            page_class, route_params = cls._find_matching_route(clean_path)
            if not page_class:
                raise RouteNotFoundError(f"Route not found: {clean_path}")

            # Update parameters before instanciation
            route_info.params.update(route_params)
            
            # 8. Instanciation 
            # try:
            page_instance = page_class()
            if hasattr(page_instance, 'route_info'):
                page_instance.route_info = route_info
            
            content = page_instance.build()
            # except Exception as e:
            #     raise NavigationError(f"Page initialization failed: {str(e)}")

            # 9. History management (only if new navigation)
            if not replace and (clean_path != cls._current_route or _redirect_depth > 0):
                # Then add new route to the navigation history
                cls._route_history.append(cls._current_route)

            # 10. Apply transition
            controls = [content] if not isinstance(content, list) else content
            if transition:
                try:
                    controls = transition.apply(cls._page, controls)
                except Exception as e:
                    cls._logger.error(f"Transition failed: {e}")

            # 11. Page update
            cls._page.clean()
            cls._page.add(*controls) if isinstance(content, list) else cls._page.add(content)
            cls._current_route = clean_path

            # 12. Middleware after navigation
            cls._middleware.run_after(route_info)

            # 13. Lifecycle management
            if isinstance(page_instance, FletXPage):
                try:
                    page_instance.did_mount()
                except Exception as e:
                    cls._logger.error(f"did_mount() failed: {e}")

            cls._logger.info(f"Navigation successful to: {clean_path}")

        except Exception as e:
            cls._logger.error(f"Navigation error: {e}", exc_info=True)
            raise NavigationError(f"Navigation failed: {e}")
        
    @classmethod
    def back(cls):
        """Navigation action that goes back to the previous page in the navigation history."""

        if cls._route_history:
            previous_route = cls._route_history.pop()
            cls.to(previous_route, replace=True)
        else:
            cls._logger.warning("Aucune page précédente dans l'historique")
    
    @classmethod
    def replace(
        cls, 
        route: str, 
        arguments: Dict[str, Any] = None
    ):
        """
        Navigation action that replaces the current route with a new one, 
        without adding the current route to the navigation history
        """

        cls.to(route, arguments, replace=True)
    
    @classmethod
    def current_route(cls) -> str:
        """
        Retrieves and returns the currently displayed or 
        active route in the application.
        """

        return cls._current_route
    
    @classmethod
    def _find_matching_route(
        cls, 
        path: str
    ) -> tuple[Optional[Type[FletXPage]], Dict[str, str]]:
        """
        Searches and returns the route that matches the specified path.
        """

        routes = RouteConfig.get_routes()
        
        # Search for an exact matching first
        if path in routes:
            return routes[path], {}
        
        # Then with parameters
        for route_pattern, page_class in routes.items():
            params = cls._match_route_pattern(route_pattern, path)
            if params is not None:
                return page_class, params
        
        return None, {}
    
    @classmethod
    def _match_route_pattern(
        cls, 
        pattern: str, 
        path: str
    ) -> Optional[Dict[str, str]]:
        """Checks if a specified path matches a defined route pattern."""

        # Convert pattern into a regex
        pattern_parts = pattern.split('/')
        path_parts = path.split('/')
        
        if len(pattern_parts) != len(path_parts):
            return None
        
        params = {}
        
        for pattern_part, path_part in zip(pattern_parts, path_parts):
            if pattern_part.startswith(':'):
                # Route parameter
                param_name = pattern_part[1:]
                params[param_name] = path_part

            elif pattern_part != path_part:
                # uncoresponding static part
                return None
        
        return params
    
    @classmethod
    def _get_guards_for_route(cls, path: str) -> List[RouteGuard]:
        """
        Retrieves the guards associated with a specific route, 
        taking into account the route's parameters to determine 
        the relevant guards that should be applied.
        """

        guards = []
        for route_pattern in cls._guards:
            if route_pattern == path:
                guards.extend(cls._guards[route_pattern])
            elif ':' in route_pattern:
                # Check the pattern with parameters
                if cls._match_route_pattern(route_pattern, path) is not None:
                    guards.extend(cls._guards[route_pattern])
        return guards
    
    @classmethod
    def register_nested_routes(cls, parent_path: str, routes: dict):
        """Register nested routes."""

        for path, page_class in routes.items():
            full_path = f"{parent_path.rstrip('/')}/{path.lstrip('/')}"
            RouteConfig.register_route(full_path, page_class)
    
    @classmethod
    def get_nested_routes(cls, base_path: str) -> dict:
        """Retrieves the routes that are nested within a parent route."""
        return {
            path: page_class 
            for path, page_class in RouteConfig.get_routes().items()
            if path.startswith(base_path)
        }