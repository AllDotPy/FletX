"""
Decorators for Controllers

Used to inject controllers into pages or widgets, 
these decorators add features such as registration, 
validation, security, etc. to controllers.
"""

from fletx import FletX
from typing import Type, Callable, Optional  # noqa: F401
from functools import wraps
from fletx.core.page import FletXPage
from fletx.core.controller import FletXController


####    PAGE CONTROLLER INJECTOR
def page_controller(
    controller_class: Optional[Type[FletXController]] = None, 
    tag: str = None
):
    """Auto-inject Controller Decorator"""
    
    def decorator(page_class: Type[FletXPage]):
        original_init = page_class.__init__
        original_build = page_class.build
        
        def __init__(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            
            # Inject the controller 
            self.controller = FletX.find(controller_class, tag)
            if self.controller is None:
                self.controller = controller_class()
                FletX.put(self.controller, tag)
        
        @wraps(original_build)
        def build(self, *args, **kwargs):
            # Ensure controller is ready
            if hasattr(self, 'controller'):
                self.controller.on_ready()
            return original_build(self, *args, **kwargs)
        
        page_class.__init__ = __init__
        page_class.build = build
        page_class.Controller = controller_class 
        
        return page_class
    
    # Allow to use @page_controller() or @page_controller(MyController)
    if controller_class is None or isinstance(controller_class, type):
        return decorator(controller_class) if controller_class else decorator
    else:
        raise TypeError(
            "controller class must be an instance of FletXController"
        )


def with_controller(cls):
    """Decorator for pages that require a controller"""
    original_build = cls.build
    
    def wrapped_build(self):
        # Auto-inject controller
        if hasattr(cls, 'Controller'):
            self.controller = FletX.find(cls.Controller)
            if self.controller is None:
                self.controller = cls.Controller()
                FletX.put(self.controller)
        
        return original_build(self)
    
    cls.build = wrapped_build
    return cls