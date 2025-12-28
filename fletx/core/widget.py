"""
Base Widget for FletX

The base widget for FletX is a fundamental component that serves 
as a template for all other widgets. It provides a basic structure 
for creating custom widgets and offers common features such as event handling, 
layout, and appearance customization.
"""

import flet as ft
import warnings
from abc import ABC, abstractmethod
from typing import Union, List, Optional, Any, Dict
from fletx.core.state import (
    Reactive, RxBool, RxInt, RxList, RxDict
)
from fletx.utils import get_logger, get_page
from fletx.core.factory import FletXWidgetRegistry
# from fletx.utils.context import AppContext


####
##      FLETX WIDGET CLASS
#####
class FletXWidget(ABC):
    """
    Base reactive widget that inherits from flet.Control.
    Combines Flet's rendering with FletX's reactivity system.
    """
    
    _logger = get_logger('FletX.Widget')

    def __init__(self, **kwargs):
        self._reactives: Dict[str, Reactive] = {}   # Deprecated
        self._props = kwargs                        # Deprecated
        self._is_mounted = False        
        # self.content = self.build()
        super().__init__()
        
    def __init_subclass__(cls, **kwargs):
        """Automatically register widget classes with FletXWidgetRegistry"""

        # Automatic registration for cleanup
        cls.page = get_page()
        cls.page.controls.append(cls)
        
        super().__init_subclass__(**kwargs)
        # Register the widget class
        FletXWidgetRegistry.register(cls)
        cls.page.update()
        
    @property
    def logger(cls):
        if not cls._logger:
            cls._logger = get_logger('FletX.Widget')
        return cls._logger
    
    @abstractmethod
    def build(self) -> Union[ft.Control, List[ft.Control]]:
        """
        Builds the widget
        This method is responsible for creating and configuring the widget. 
        It defines the widget's properties and behaviors, such as its appearance, 
        content, and user interactions.
        """
        pass

    def did_mount(self):
        """Called when widget is added to the page"""
        self._is_mounted = True

    def will_unmount(self):
        """Called before widget is removed"""
        self._dispose_reactives()
        self._is_mounted = False
    
    def bind(
        self, 
        prop_name: str, 
        reactive_obj: Union[Reactive, RxBool, RxInt, RxList, RxDict]
    ):
        """
        Binds a widget property to a reactive object
        Usage: self.bind("text", rx_text)
        """

        warnings.warn('FletXWidget.bind is deprecated and will be removed soon.')

        if not isinstance(reactive_obj, (Reactive, RxBool, RxInt, RxList, RxDict)):
            self.logger.error(
                f"Attempted to bind {prop_name} to a non-reactive object: {reactive_obj}"
            )
            return 
        
        if prop_name in self._reactives:
            self._reactives[prop_name].dispose()
        
        reactive_obj.listen(self._create_update_callback(prop_name))
        self._reactives[prop_name] = reactive_obj
        setattr(self, prop_name, reactive_obj.value)

        self.logger.debug(
                f"bound {prop_name} to the reactive object: {reactive_obj}"
            )

    def _create_update_callback(self, prop_name: str):
        """Generates a safe update callback"""

        warnings.warn(
            'FletXWidget._create_update_callback is '
            'deprecated and will be removed soon.'
        )
        def callback():
            if not self._is_mounted:
                self.logger.warning(
                    f"Attempted to update {self.__class__.__name__}.{prop_name} "
                    "but the widget is not mounted."
                )
                # Optionally, you could raise an exception or log an error
                # raise RuntimeError(f"{self.__class__.__name__} is not mounted")
                # or return to prevent further processing
                # return
                
            new_value = self._reactives[prop_name].value
            setattr(self, prop_name, new_value)
            self.logger.debug(
                f"Updating {self.__class__.__name__}.{prop_name} to {new_value}"
            )
            
            # Special handling for Control properties
            if hasattr(self, "content") and isinstance(self.content, ft.Control):
                if hasattr(self.content, prop_name):
                    # Update the property on the content control
                    self.logger.debug(
                        f"Updating {self.__class__.__name__}.content.{prop_name} to {new_value}"
                    )
                    setattr(self.content, prop_name, new_value)

                if hasattr(self, prop_name):
                    # If the widget has a property with the same name, update it
                    self.logger.debug(
                        f"Updating {self.__class__.__name__}.{prop_name} to {new_value}"
                    )
                    setattr(self, prop_name, new_value)

                if hasattr(self,'build'):
                    # If the widget has a build method, call it to update the UI
                    self.logger.debug(
                        f"Rebuilding {self.__class__.__name__} after updating {prop_name}"
                    )
                    self.content = self.build()

            # Special for handling for List[ft.Control] properties
            elif hasattr(self, "controls") and isinstance(self.controls, list):
                if hasattr(self, 'build'):
                    # If the widget has a build method, call it to update the UI
                    self.logger.debug(
                        f"Rebuilding {self.__class__.__name__} after updating {prop_name}"
                    )
                    self.controls = self.build()

            else:
                # If the widget has "prop_name" as a property, update it
                if hasattr(self, prop_name):
                    self.logger.debug(
                        f"Updating {self.__class__.__name__}.{prop_name} to {new_value}"
                    )
                    setattr(self, prop_name, new_value)

                # If the widget has a build method, call it to update the UI
                if hasattr(self, 'build'):
                    self.logger.debug(
                        f"Rebuilding {self.__class__.__name__} after updating {prop_name}"
                    )
                    self.build()
            
            # Finally, update the widget
            self.update()
        return callback

    def _dispose_reactives(self):
        """Cleanup all reactive bindings"""

        for reactive in self._reactives.values():
            reactive.dispose()
        self._reactives.clear()
    
    # Maintain backwards compatibility
    def get_prop(self, key: str, default: Any = None) -> Any:
        """Retrieves the value of a specific property of the widget."""

        return self._props.get(key, default)
    
    def update_props(self, **kwargs):
        """Updates the widget's properties to reflect changes or new values."""

        self._props.update(kwargs)
        if self._is_mounted:
            self.update()

    # Override ft.Control's methods
    # def _get_control_name(self):
    #     return "fletxwidget"
    
    def _get_children(self):
        content = self.build()
        if isinstance(content, list):
            return content
        return [content] if content else []
    
    def before_update(self):
        """Called before Flet updates the UI"""

        super().before_update()
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self.did_mount()
    
    def render(self) -> Union[ft.Control, List[ft.Control]]:
        """Renders the widget"""
        try:
            return self.build()
        except Exception as e:
            self.logger.error(
                f"Error when trying to render the {self.__class__.__name__} Widget: {e}"
            )
            return ft.Text(f"Error: {e}", color=ft.Colors.RED)