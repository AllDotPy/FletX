"""
ObX Widget - Reactive Builder for FletX
"""

from typing import (
    Set, Callable, Optional,
    Type
)
from functools import wraps  # noqa: F401

import flet as ft
from flet import Control, Ref
from fletx.core.state import Reactive, ReactiveDependencyTracker
from fletx.utils import get_logger, get_page  # noqa: F401


####
##      OBX CONTROLLER
#####
class ObxController:
    """Controller for managing Obx widget reactivity"""

    def __init__(self):
        self._widget_ref: Optional[Ref] = None
        self._uid: Optional[str] = None
        self._dependencies: Set[Reactive] = set()
        self._builder: Optional[Callable] = None
        # self._current_uid = None 
        self._logger = get_logger("ObxController")
        self._is_building = False

    @property
    def logger(self):
        return self._logger
    
    def set_uid(self, uid:str):
        """ste the wapped control uid."""
        self._uid = uid
        # print(self._uid)

    def set_builder(self, builder_fn: Callable):
        """Set the builder function"""

        self._builder = builder_fn

    def set_widget_ref(self, widget_ref: Ref):
        """Set the widget reference"""

        self._widget_ref = widget_ref

    def add_dependency(self, reactive_obj: Reactive):
        """Add a reactive object as dependency"""

        if reactive_obj not in self._dependencies:
            # Subscribe to rebuild on changes
            reactive_obj.listen(self._rebuild, auto_dispose=True)
            # Add to dependencies list
            self._dependencies.add(reactive_obj)
            self.logger.debug(f"Added dependency: {reactive_obj}")

    def _rebuild(self):
        """Rebuild the widget when dependencies change"""

        self._logger.debug("Rebuilding widget due to dependency change")

        if self._is_building:
            self.logger.warning(
                "Cannot rebuild: widget is already in building."
            )
            return  # Prevent infinite rebuild loops
        
        if not self._widget_ref or not self._widget_ref.current:
            self.logger.warning(
                "Skipping rebuild - widget reference not available"
            )
            return

        current_widget = self._widget_ref.current

        try:
            self._is_building = True

            preserved_attrs = {
                'ref': self._widget_ref,
                '_Control__uid': current_widget.uid,
                '_Control__page': current_widget.page,
                'did_mount': getattr(current_widget, 'did_mount', None),
                'will_unmount': getattr(current_widget, 'will_unmount', None)
            }
            
            # Track dependencies during rebuild
            with ObserverContext(self):
                new_content = self._builder()
            
            # For other widget types, try to copy properties
            self._copy_widget_properties(new_content, current_widget)

            # Restore preserved attributs 
            for attr, value in preserved_attrs.items():
                if hasattr(current_widget, attr):
                    setattr(current_widget, attr, value)
            
            # Trigger UI update
            if current_widget.page:
                current_widget.update()
                
            self.logger.debug("Widget rebuilt successfully")
            
        except Exception as e:
            self.logger.error(f"Error during rebuild: {e}", exc_info=True)
        finally:
            self._is_building = False

    def _copy_widget_properties(
        self, 
        source: Control, 
        target: Control
    ):
        """Copy properties from source widget to target widget"""

        for attr_name in dir(source):
            if not attr_name.startswith('_') and hasattr(target, attr_name):
                try:
                    attr_value = getattr(source, attr_name)
                    if not callable(attr_value):
                        setattr(target, attr_name, attr_value)
                except (AttributeError, TypeError):
                    continue

    def dispose(self):
        """Clean up resources"""

        for dep in list(self._dependencies):
            try:
                dep._remove_observer(self)
            except:  # noqa: E722
                pass
        self._dependencies.clear()
        self._widget_ref = None
        self._builder = None


####
##      OBSERVER CONTEXT
#####
class ObserverContext:
    """Context manager for tracking reactive dependencies"""

    def __init__(self, controller: ObxController):
        self.controller: ObxController = controller
        self._previous_tracker = None

    def __enter__(self):
        # Save previous tracker
        self._previous_tracker = ReactiveDependencyTracker._current_tracker
        
        # Create a custom tracker that adds dependencies to the controller
        class CustomTracker:
            def __init__(self, controller: ObxController):
                self.controller = controller
                self.dependencies = set()
            
            def add(self, reactive_obj):
                self.dependencies.add(reactive_obj)
                self.controller.add_dependency(reactive_obj)
        
        ReactiveDependencyTracker._current_tracker = CustomTracker(self.controller)
        return self.controller

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore previous tracker when exiting Obx Context"""
        # Restore previous tracker
        # ReactiveDependencyTracker._current_tracker = self._previous_tracker


####
##      OBX CLASS WIDGET
#####
class Obx:
    """
    Obx reactive wrapper that automatically detects Reactive 
    dependencies within its content builder and rebuilds when
    those dependencies change. Preserves the original widget identity.
    """

    def __init__(
        self,
        builder_fn: Callable[[], Control]
    ):
        self.builder_fn = builder_fn
        self.controller = ObxController()
        self._widget = None
        self.ref: Optional[Ref] = None
        self._final_uid = f"obx_{id(self)}"  
        self._is_mounted = False
        self._logger = get_logger("Obx")
        
        # Set up controller
        self.controller.set_builder(builder_fn)

    @property
    def logger(self):
        if not self._logger:
            self._logger = get_logger('Obx')
        return self._logger
    
    @property
    def widget(self) -> Control:
        """Get the actual widget"""
        return self._widget

    def _build_widget(self):
        """Build the widget with dependency tracking"""
        try:
            with ObserverContext(self.controller):
                self._widget = self.builder_fn()
            
            # Set up reference for the actual widget
            if not hasattr(self._widget, 'ref') or self._widget.ref is None:
                self.ref = Ref[Type[self._widget.__class__]]()
                self.ref.current = self._widget

            # Setup the wrapped widget ID
            self._widget._Control__attrs['id'] = self._final_uid
            
            # Set the widget references in controller
            self.controller.set_uid(self._final_uid)
            self.controller.set_widget_ref(self.ref)
            
            self.logger.debug(f"Built widget: {type(self._widget).__name__} #{self._widget._id}")
        
        # Error building widget
        except Exception as e:
            self.logger.error(f"Error building widget: {e}", exc_info=True)
            self._widget = ft.Text("Error building content")

            if not hasattr(self._widget, 'ref'):
                self._widget.ref = Ref()
            self.controller.set_widget_ref(self._widget.ref)
    
    def _build_add_commands(self, *args,**kwargs):
        """
        Override '_build_add_commands' to peform widget build and avoid 
        ref and uid changes within build process.
        """

        # Build initial widget with dependency tracking
        self._build_widget()

        # Build commands and get final id
        commands = self._widget._build_add_commands(*args,**kwargs)
        self._final_uid = commands[0].attrs['id']

        self.controller.set_uid(self._final_uid)
        return commands
    
    def build_update_commands(self, *args, **kwargs):
        return self._widget.build_update_commands(*args, **kwargs)
    
    def get_control_name(self):
        return self._widget._get_control_name()
    
    def is_isolated(self):
        return self._widget.is_isolated()

    def will_unmount(self):
        self._widget.will_unmount()
        self.dispose()
    
    def dispose(self):
        """Clean up resources when wrapper is disposed"""

        if hasattr(self, 'controller') and self.controller:
            self.controller.dispose()
        
        # Also dispose the wrapped widget if it has a dispose method
        if hasattr(self._widget, 'dispose'):
            try:
                self._widget.dispose()
            except:  # noqa: E722
                pass

    def __getattr__(self, name):
        """Delegate attribute access to the wrapped widget"""

        if (
            not hasattr(self._widget, name) 
            or name in ['builder_fn', 'controller', 'widget', 'logger']
        ):
            raise AttributeError(
                f"'{type(self._widget).__name__}' object has no attribute '{name}'"
            )
        
        if self._widget and hasattr(self._widget, name):
            return getattr(self._widget, name)
        
        raise AttributeError(
            f"'{type(self._widget).__name__}' object has no attribute '{name}'"
        )
    