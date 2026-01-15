import asyncio

from fletx.core.routing.router import (
    FletXRouter
)
from fletx.core.routing.config import (
    RoutePattern, RouterConfig, router_config,
    ModuleRouter
)
from fletx.core.routing.guards import RouteGuard
from fletx.core.routing.middleware import RouteMiddleware
from fletx.core.routing.transitions import (
    TransitionType, RouteTransition
)
from fletx.core.routing.models import (
    RouteInfo, RouterState, RouteType,
    NavigationIntent, NavigationMode, 
    NavigationResult, IRouteResolver
)
from fletx.utils import (
    get_event_loop, run_async, get_logger  # noqa: F401
)


# Convenience functions for global router access

def get_router() -> FletXRouter:
    """Get the global router instance."""
    
    return FletXRouter.get_instance()

async def navigate_to(route: str, **kwargs) -> NavigationResult:
    """Navigate using the global router."""

    router = get_router()
    try:
        # Run the navigation task and wait for completion
        result = await router.navigate(route, **kwargs)
        return result
    
    except asyncio.CancelledError:
        get_logger('FletX.Navigation').warning("Navigation was cancelled")
        return NavigationResult.CANCELLED
    
def navigate(route: str, **kwargs) -> NavigationResult:
    """Synchronous wrapper for navigation that schedules the task properly."""

    return run_async(
        lambda: navigate_to(route, **kwargs)
    )

def go_back() -> bool:
    """Go back using the global router."""
    return get_router().go_back()

def go_forward() -> bool:
    """Go forward using the global router."""
    return get_router().go_forward()


__all__ = [
    'RouteGuard',
    'RouteMiddleware',
    'TransitionType',
    'RouteTransition',
    'RoutePattern',
    'RouterConfig',
    'FletXRouter',
    'NavigationResult',
    'RouteInfo',
    'RouterState',
    'RouteType',
    'NavigationIntent',
    'NavigationMode',
    'IRouteResolver',
    'ModuleRouter',
    'router_config',

    # FUNCTIONS
    'get_router',
    'navigate',
    'go_back',
    'go_forward'
]