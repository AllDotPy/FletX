"""
Route Configuration and Registration.
Route configuration and registration module for FletX, 
allowing to define and manage application routes, including nested routes, 
parameters, and security guards.
"""

from typing import Dict, Type
from fletx.core.page import FletXPage
from fletx.utils import get_logger


####
##      ROUTE CONFIG CLASS
#####
class RouteConfig:
    """
    Route Configuration Manager responsible for managing route configuration.
    """
    
    _routes: Dict[str, Type[FletXPage]] = {}  # pragma: no cover
    _logger = get_logger(__name__)

    @property
    def logger(cls):
        if not cls._logger:
            cls._logger = get_logger('FletX.RouterConfig')
        return cls._logger
    
    @classmethod
    def register_routes(cls, routes: Dict[str, Type[FletXPage]]):
        """Register a route dictionary"""

        for path, page_class in routes.items():
            cls.register_route(path, page_class)
    
    @classmethod
    def register_route(cls, path: str, page_class: Type[FletXPage]):
        """Register a single route"""

        if not issubclass(page_class, FletXPage):
            raise ValueError(f"{page_class} must be an instance of FletXPage")
        
        cls._routes[path] = page_class
        cls.logger.debug(f"Route registered: {path} -> {page_class.__name__}")
    
    @classmethod
    def get_routes(cls) -> Dict[str, Type[FletXPage]]:
        """Retrieves and returns the list of all registered routes."""

        return cls._routes.copy()
    
    @classmethod
    def get_route(cls, path: str) -> Type[FletXPage]:
        """Retrieves and returns the page class associated with a specific route path."""
        
        return cls._routes.get(path)