"""
Decorators for route registration.

These decorators simplify the process of associating URL routes with 
their corresponding page handlers, enabling clear and concise routing 
definitions within the application.
"""

from fletx.core.routing.config import (
    router_config, ModuleRouter
)


####    REGISTER ROUTER
def register_router(cls: ModuleRouter):
    """Decorator that automatically registers module routes"""
    # Parent router initialization
    router = cls()
    
    # Register router to the globale config 
    if cls.is_root:
        router_config.add_module_routes('', router)
    
    return cls
