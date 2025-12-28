"""
resize Application routing module.
Version: 0.1.0
"""


# Import your pages here
from fletx.navigation import (
    ModuleRouter, TransitionType, RouteTransition
)
from fletx.decorators import register_router

from .pages import CounterPage, NotFoundPage

# Define Resize routes here
routes = [
    {
        'path': '/',
        'component': CounterPage,
    },
    {
        'path': '/**',
        'component': NotFoundPage,
    },
]

@register_router
class ResizeRouter(ModuleRouter):
    """resize Routing Module."""

    name = 'resize'
    base_path = '/'
    is_root = True
    routes = routes
    sub_routers = []