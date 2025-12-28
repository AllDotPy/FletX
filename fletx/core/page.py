"""
FletX - Enhanced Core Page module.
Advanced page with integrated controller, effects, and reactivity management
A page that incorporates advanced features such as controller, effects, and reactivity management, 
enabling the creation of interactive and dynamic user experiences.
"""

import flet as ft
from typing import (
    Union, List, Optional, Any, Dict, Type, TypeVar, Callable, Tuple
)
from abc import ABC, abstractmethod
from fletx.core.controller import FletXController
from fletx.core.routing.models import RouteInfo
from fletx.core.di import DI
from fletx.core.effects import EffectManager

from fletx.core.state import Reactive
from fletx.utils import get_logger, get_page
import weakref
from datetime import datetime
from enum import Enum

T = TypeVar('T', bound=FletXController)


####
##      FLETX PAGE STATES
#####
class PageState(Enum):
    """Enum for page lifecycle states"""

    INITIALIZING = "initializing"
    MOUNTED = "mounted"
    ACTIVE = "active"
    INACTIVE = "inactive"
    UNMOUNTING = "unmounting"
    DISPOSED = "disposed"


####
##      FLETX ENHANCED PAGE CLASS
#####
class FletXPage(ft.Container, ABC):
    """
    Enhanced base class for FletX pages that inherits from ft.Container.
    Provides comprehensive lifecycle management, event handling, and utilities
    for building robust and interactive pages.
    """
    
    def __init__(
        self,
        *,
        # Container properties
        padding: Optional[ft.PaddingValue]= None,
        bgcolor: Optional[str] = None,
        # Page specific properties
        auto_dispose_controllers: bool = True,
        enable_keyboard_shortcuts: bool = True,
        enable_gestures: bool = True,
        safe_area: bool = True,
        **kwargs
    ):        
        # Page properties
        self.route_info: Optional[RouteInfo] = None
        self._controllers: Dict[str, FletXController] = {}
        self._effects = EffectManager()
        self._logger = get_logger(f"FletX.Page.{self.__class__.__name__}")
        self._state = PageState.INITIALIZING
        self._safe_area = safe_area
        self._auto_dispose_controllers = auto_dispose_controllers
        
        # Event handlers storage
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._keyboard_shortcuts: Dict[str, Callable] = {}
        self._gesture_handlers: Dict[str, Callable] = {}
        
        # Lifecycle tracking
        self._mount_time: Optional[datetime] = None
        self._last_update_time: Optional[datetime] = None
        self._update_count = 0
        
        # Performance metrics
        self._render_times: List[float] = []
        self._max_render_history = 10
        
        # Reactive properties
        self._reactive_subscriptions: List[Any] = []
        self._child_pages: weakref.WeakSet = weakref.WeakSet()
        
        # Configuration
        self._enable_keyboard_shortcuts = enable_keyboard_shortcuts
        self._enable_gestures = enable_gestures
        
        # Register page instance
        DI.put(self._effects, f"page_effects_{id(self)}")
        
        # Set up built-in event handlers
        self._setup_built_in_handlers()

        # Build the page content
        # self._build_page()

        # Initialize Container
        super().__init__(
            expand = True,
            padding = padding,
            bgcolor = bgcolor,
            width = get_page().width,
            **kwargs
        )
    
    @property
    def logger(self):
        """Logger instance for this page"""

        return self._logger
    
    @property
    def state(self) -> PageState:
        """Current state of the page"""

        return self._state
    
    @property
    def is_mounted(self) -> bool:
        """Check if page is mounted"""

        return self._state in [PageState.MOUNTED, PageState.ACTIVE]
    
    @property
    def is_active(self) -> bool:
        """Check if page is active"""

        return self._state == PageState.ACTIVE
    
    @property
    def mount_time(self) -> Optional[datetime]:
        """Time when page was mounted"""

        return self._mount_time
    
    @property
    def page_instance(self) -> Optional[ft.Page]:
        """Get the Flet page instance"""

        return get_page()
    
    @property
    def average_render_time(self) -> float:
        """Average render time in milliseconds"""

        if not self._render_times:
            return 0.0
        return sum(self._render_times) / len(self._render_times)

    @property
    def view(self):
        """Get the Flet active view"""

        return self.page_instance.views[-1]

    # Abstract methods
    @abstractmethod
    def build(self) -> Union[ft.Control, List[ft.Control]]:
        """
        Abstract method to implement for building the page content.
        Must be implemented by derived classes.
        """
        pass

    # Navigation widgets
    def build_app_bar(self) -> Optional[ft.AppBar]:
        """
        Override this method to build a custom app bar.
        Return None to use the default app bar or hide it.
        """
        
        return None
    
    def build_floating_action_button(self) -> Optional[ft.FloatingActionButton]:
        """
        Override this method to build a custom floating action button.
        Return None if no floating action button is needed.
        """

        return None
    
    def build_floating_action_button_location(self) -> Optional[ft.FloatingActionButtonLocation]:
        """
        Override this method to build a custom floating action button Location.
        Return None if no floating action button is needed.
        """

        return None
    
    def build_drawer(self) -> Optional[ft.NavigationDrawer]:
        """
        Override this method to build a custom navigation drawer.
        Return None if no drawer is needed.
        """

        return None
    
    def build_end_drawer(self) -> Optional[ft.NavigationDrawer]:
        """
        Override this method to build a custom navigation end drawer.
        Return None if no drawer is needed.
        """

        return None
    
    def build_bottom_app_bar(self) -> Optional[ft.BottomAppBar]:
        """
        Override this method to build a custom bottom app bar.
        Return None if no bottom app bar is needed.
        """

        return None
    
    def build_navigation_bar(self):
        """
        Override this method to build a custom navigation bar.
        Return None if no bottom app bar is needed.
        """

        return None
    
    def build_bottom_sheet(
        self, 
        *args, 
        **extra_kwargs
    ) -> ft.BottomSheet:
        """
        Builds bottom sheet.
        Override this method to use a custom bottom sheet.
        """

        return ft.BottomSheet()
    
    def build_navigation_widgets(self):
        """Build all needed Navigation widgets."""

        # AppBar
        self.view.appbar = self.build_app_bar()

        # Bottom AppBar
        self.view.bottom_appbar = self.build_bottom_app_bar()

        # Nav Drawer
        self.view.drawer = self.build_drawer()

        # Navigation Bar
        self.view.navigation_bar = self.build_navigation_bar()

        # Floating Action Button
        self.view.floating_action_button = self.build_floating_action_button()

        # Floating Action Button Location
        self.view.floating_action_button_location = self.build_floating_action_button_location()

        # End Drawer
        self.view.end_drawer = self.build_end_drawer()
    
    # Lifecycle methods
    def before_on_init(self):
        """Calls the on_init() hook"""

        self.logger.debug(f"Page {self.__class__.__name__} will mount")
        self._state = PageState.ACTIVE

        # Call On init hook
        self.on_init()
        self.logger.debug(f"Page {self.__class__.__name__}.on_init() hook called.")
    
    def did_mount(self):
        """Called when the page is mounted"""
        
        self._state = PageState.MOUNTED
        self._mount_time = datetime.now()
        self._is_mounted = True
        self._effects.runEffects()
        self.logger.debug(f"Page {self.__class__.__name__} did mount")
        
        # On Init
        self.before_on_init()
    
    def on_init(self):
        """Hook called when the page is about to appear"""
        pass
    
    def on_destroy(self):
        """Hook called when the page will unmount"""
        pass
    
    def will_unmount(self):
        """Called when the page is about to be unmounted"""

        self._state = PageState.UNMOUNTING

        # Call hooks
        self.on_destroy()
        self.logger.debug(f"Page {self.__class__.__name__} will unmount")
        self.did_unmount()
    
    def did_unmount(self):
        """Called when the page has been unmounted"""

        self._state = PageState.DISPOSED
        self._is_mounted = True
        self._effects.dispose()

        # Dispose controlers if needed
        if self._auto_dispose_controllers:
            self._dispose_controllers()
        self._cleanup_subscriptions()

        self.logger.debug(f"Page {self.__class__.__name__} disposed")

        # Call on Destroy hook
        self.logger.debug(f"Page {self.__class__.__name__}.on_destroy() called")
        self.on_destroy()

    # Controller management
    def get_controller(
        self, 
        controller_class: Type[T], 
        tag: str = None,
        lazy: bool = True
    ) -> T:
        """Gets or creates a controller with automatic lifecycle management"""

        controller_key = (
            f"{controller_class.__name__}_{tag}" 
            if tag 
            else controller_class.__name__
        )
        
        if controller_key in self._controllers:
            return self._controllers[controller_key]
        
        if not lazy:
            controller = DI.find(controller_class, tag)
            if not controller:
                controller = controller_class()
                DI.put(controller, tag)
            
            self._controllers[controller_key] = controller
            return controller
        
        # Lazy loading
        def _lazy_controller():

            if controller_key not in self._controllers:
                controller = DI.find(controller_class, tag)
                if not controller:
                    controller = controller_class()
                    DI.put(controller, tag)
                self._controllers[controller_key] = controller
            return self._controllers[controller_key]
        
        return _lazy_controller()
    
    def inject_controller(
        self, 
        controller: FletXController, 
        tag: str = None
    ):
        """Manually inject a controller instance"""

        controller_key = (
            f"{controller.__class__.__name__}_{tag}" 
            if tag 
            else controller.__class__.__name__
        )
        self._controllers[controller_key] = controller
    
    def remove_controller(
        self, 
        controller_class: Type[T], 
        tag: str = None
    ) -> bool:
        """Remove a controller from the page"""

        controller_key = (
            f"{controller_class.__name__}_{tag}" 
            if tag 
            else controller_class.__name__
        )
        if controller_key in self._controllers:
            controller = self._controllers.pop(controller_key)
            controller.dispose()
            return True
        return False

    # Effect management
    def add_effect(
        self, 
        effect_fn: Callable, 
        dependencies: List[Any] = None,
        cleanup_fn: Optional[Callable] = None
    ):
        """Adds an effect to the page with optional cleanup"""

        def enhanced_effect():
            result = effect_fn()
            if cleanup_fn:
                self.add_cleanup(cleanup_fn)
            return result
        
        self._effects.useEffect(enhanced_effect, dependencies)
    
    def add_cleanup(self, cleanup_fn: Callable):
        """Add a cleanup function to be called on unmount"""

        self.add_effect(lambda: cleanup_fn, [])

    # Reactive object management
    def watch(
        self, 
        reactive_obj: Reactive, 
        callback: Callable,
        immediate: bool = False
    ):
        """Observes a reactive object with automatic cleanup"""

        if hasattr(reactive_obj, 'listen'):
            if immediate:
                self._safe_callback(callback)
            
            observer = reactive_obj.listen(lambda: self._safe_callback(callback))
            self._reactive_subscriptions.append(observer)
            self.add_cleanup(
                lambda: observer.dispose() 
                if hasattr(observer, 'dispose') 
                else None
            )
            return observer
        else:
            self.logger.warning(f"{reactive_obj} is not a reactive object")
            return None
    
    def watch_multiple(
        self, 
        reactive_objects: List[Any], 
        callback: Callable,
        immediate: bool = False
    ):
        """Watch multiple reactive objects"""
        observers = []
        for obj in reactive_objects:
            observer = self.watch(obj, callback, immediate and len(observers) == 0)
            if observer:
                observers.append(observer)
        return observers

    # Event handling
    def on_resize(self, callback: Callable[[ft.ControlEvent], None]):
        """
        Listen to page resize events.
        Event handler argument is of type `WindowResizeEvent`.
        """

        self._add_event_handler("resized", callback)
    
    def on_keyboard(self, callback: Callable[[ft.KeyboardEvent], None]):
        """Listen to keyboard events"""

        self._add_event_handler("keyboard_event", callback)
    
    def on_error(self, callback: Callable[[Exception], None]):
        """Listen to error events"""

        self._add_event_handler("error", callback)
    
    def on_media_change(self, callback: Callable[[ft.ControlEvent], None]):
        """
        Listen to Page media change events.
        Event handler argument is of type `PageMediaData`
        """

        self._add_event_handler("media_change", callback)
    
    def on_brigthness_change(self, callback: Callable[[ft.ControlEvent], None]):
        """Listen to platform brigthness change events."""

        self._add_event_handler("platform_brigthness_change", callback)
    
    def on_scroll(self, callback: Callable[[ft.ControlEvent], None]):
        """Listen to scroll events"""

        self._add_event_handler("scroll", callback)

    # Keyboard shortcuts
    def add_keyboard_shortcut(
        self, 
        key_combination: str, 
        callback: Callable,
        description: str = ""
    ):
        """Add a keyboard shortcut"""

        if self._enable_keyboard_shortcuts:
            self._keyboard_shortcuts[key_combination] = {
                'callback': callback,
                'description': description
            }
            self.logger.debug(
                f'{key_combination} shortcut callback registered for {self.__class__.__name__}'
            )
            # Finally re-setup handlers
            self._setup_built_in_handlers()
    
    def remove_keyboard_shortcut(
        self, key_combination: str
    ) -> bool:
        """Remove a keyboard shortcut"""

        self.logger.debug(
                f'{key_combination} shortcut handler removed.'
            )
        return self._keyboard_shortcuts.pop(key_combination, None) is not None
    
    def get_keyboard_shortcuts(self) -> Dict[str, Dict]:
        """Get all keyboard shortcuts"""

        return self._keyboard_shortcuts.copy()

    # Gesture handling
    def on_tap(self, callback: Callable[[ft.TapEvent], None]):
        """Handle tap gestures"""

        if self._enable_gestures:
            self._gesture_handlers['tap'] = callback
            self.on_click = callback
    
    def on_long_press(
        self, 
        callback: Callable[[ft.LongPressStartEvent], None]
    ):
        """Handle long press gestures"""

        if self._enable_gestures:
            self._gesture_handlers['long_press'] = callback
    
    def on_scale(
        self, 
        callback: Callable[[ft.ScaleUpdateEvent], None]
    ):
        """Handle scale gestures"""

        if self._enable_gestures:
            self._gesture_handlers['scale'] = callback

    def set_app_bar(self, app_bar: Optional[ft.AppBar]):
        """Set the app bar"""

        self.view.appbar = app_bar
        self.refresh()
    
    def set_floating_action_button(
        self, 
        fab: Optional[ft.FloatingActionButton],
        location: Optional[ft.FloatingActionButtonLocation] = None
    ):
        """Set the floating action button"""

        self.view.floating_action_button = fab
        if location:
            self.view.floating_action_button_location = location
        self.refresh()
    
    def set_drawer(self, drawer: Optional[ft.NavigationDrawer]):
        """Set the navigation drawer"""

        self.view.drawer = drawer
        self.refresh()
    
    def set_end_drawer(self, end_drawer: Optional[ft.NavigationDrawer]):
        """Set the end navigation drawer"""

        self.view.end_drawer = end_drawer
        self.refresh()
    
    def set_bottom_app_bar(self, bottom_app_bar: Optional[ft.BottomAppBar]):
        """Set the bottom app bar"""

        self.view.bottom_appbar = bottom_app_bar
        self.refresh()
    
    def open_drawer(self):
        """Open the navigation drawer"""

        page = self.page_instance
        if page and self.view.drawer:
            page.open(self.view.drawer)
    
    def close_drawer(self):
        """Close the navigation drawer"""

        page = self.page_instance
        if page and self.view.drawer:
            page.close(self.view.drawer)
    
    def open_end_drawer(self):
        """Open the end navigation drawer"""

        page = self.page_instance
        if page and self.view.end_drawer:
            page.open(self.view.end_drawer)
    
    def close_end_drawer(self):
        """Close the end navigation drawer"""

        page = self.page_instance
        if page and self.view.end_drawer:
            page.close(self.view.end_drawer)

    def open_bottom_sheet(
        self, content: ft.Control, 
        on_dismiss: Optional[Callable[[ft.ControlEvent], Any]] = None
    ):
        """Shows a given content in a bottom sheet"""

        # First get the bottom sheet widget to use
        bts = self.build_bottom_sheet()

        # Set content 
        bts.content = content
        bts.on_dismiss = on_dismiss

        self.page_instance.open(bts)

    def show_loader(
        self, 
        content: Optional[ft.Control] = None, 
        on_dismiss: Optional[Callable[[ft.ControlEvent], Any]] = None
    ):
        """Show a given content in a ft.AlertDialog"""

        dialog = ft.AlertDialog(
            content = content if content else ft.ProgressRing(),
            on_dismiss = on_dismiss
        )
        self.page_instance.open(dialog)
    
    def refresh(self):
        """Refresh the page"""

        self._update_count += 1
        self._last_update_time = datetime.now()
        if self.page_instance:
            self.page_instance.update()
    
    def set_title(self, title: str):
        """Set the page title"""

        page = self.page_instance
        if page:
            page.title = title
            page.update()
    
    def set_theme_mode(self, theme_mode: ft.ThemeMode):
        """Set the theme mode"""

        page = self.page_instance
        if page:
            page.theme_mode = theme_mode
            page.update()

    # Performance monitoring
    def measure_render_time(self, func: Callable):
        """Decorator to measure render time"""

        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            result = func(*args, **kwargs)
            end_time = datetime.now()
            
            render_time = (end_time - start_time).total_seconds() * 1000
            self._render_times.append(render_time)
            
            if len(self._render_times) > self._max_render_history:
                self._render_times.pop(0)
            
            self.logger.debug(f"Render time: {render_time:.2f}ms")
            return result
        return wrapper
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""

        return {
            'mount_time': self._mount_time,
            'last_update_time': self._last_update_time,
            'update_count': self._update_count,
            'average_render_time': self.average_render_time,
            'render_times': self._render_times.copy(),
            'controller_count': len(self._controllers),
            'effect_count': (
                len(self._effects._effects) 
                if hasattr(self._effects, '_effects') 
                else 0
            ),
            'subscription_count': len(self._reactive_subscriptions)
        }

    # Private methods
    def _setup_built_in_handlers(self):
        """Set up built-in event handlers"""

        if self._enable_keyboard_shortcuts:
            self.on_keyboard(self._handle_keyboard_shortcuts)

        # AUTO Page resize
        def resize(e: ft.WindowResizeEvent):
            """resizee page and refresh"""

            self.width = e.width
            self.height = e.height
            self.refresh()
            
        self.on_resize(resize)
    
    def _handle_keyboard_shortcuts(self, e: ft.KeyboardEvent):
        """Handle keyboard shortcuts"""

        key_combo = self._get_key_combination(e)
        if key_combo in self._keyboard_shortcuts:
            try:
                self._keyboard_shortcuts[key_combo]['callback']()
            except Exception as ex:
                self.logger.error(f"Error in keyboard shortcut handler: {ex}")
    
    def _get_key_combination(self, e: ft.KeyboardEvent) -> str:
        """Get key combination string from keyboard event"""

        modifiers = []

        # CTRL
        if e.ctrl:
            modifiers.append("ctrl")
        
        # ALT
        if e.alt:
            modifiers.append("alt")

        # SHIFT
        if e.shift:
            modifiers.append("shift")

        # META
        if e.meta:
            modifiers.append("meta")
        
        key_combo = "+".join(modifiers)
        if key_combo:
            key_combo += f"+{e.key}"
        else:
            key_combo = e.key
        
        return key_combo.lower()
    
    def _build_page(self):
        """Build the page content"""

        try:
            start_time = datetime.now()
            # Build Page Content
            content = self.build()

            # Then Navigation widgets
            self.build_navigation_widgets()
            end_time = datetime.now()
            
            # Measure build time
            build_time = (end_time - start_time).total_seconds() * 1000
            self.logger.debug(f"Page build time: {build_time:.2f}ms")
            
            # Set content
            if isinstance(content, list):
                self.content = ft.Column(content, expand=True)
            else:
                self.content = content
                
        except Exception as e:
            self.logger.error(f"Error building page: {e}", exc_info=True)
            self.content = ft.Container(
                content = ft.Text(f"Error building page: {str(e)}"),
                padding = 20
            )
    
    def _add_event_handler(
        self, 
        event_name: str, 
        callback: Callable
    ):
        """Add an event handler"""

        if event_name not in self._event_handlers:
            self._event_handlers[event_name] = []
        
        self._event_handlers[event_name].append(callback)
        
        # Connect to actual Flet events
        self.add_effect(
            lambda: self._connect_event_handler(event_name, callback),
            []
        )
    
    def _connect_event_handler(
        self, 
        event_name: str, 
        handler: Callable
    ):
        """Connect an event handler to Flet events"""

        page = self.page_instance
        if page and hasattr(page, f'on_{event_name}'):
            def safe_handler(*args, **kwargs):
                if self.is_mounted:
                    try:
                        handler(*args, **kwargs)
                    except Exception as e:
                        self.logger.error(f"Error in {event_name} handler: {e}")
                        self._trigger_error_handlers(e)
            
            setattr(page, f'on_{event_name}', safe_handler)
            return lambda: setattr(page, f'on_{event_name}', None)
        return None
    
    def _trigger_error_handlers(self, error: Exception):
        """Trigger error handlers"""

        if 'error' in self._event_handlers:
            for handler in self._event_handlers['error']:
                try:
                    handler(error)
                except Exception as e:
                    self.logger.error(f"Error in error handler: {e}")
    
    def _safe_callback(self, callback: Callable, *args, **kwargs):
        """Execute a callback safely"""

        if self.is_mounted:
            try:
                return callback(*args, **kwargs)
            except Exception as e:
                self.logger.error(f"Callback error: {e}", exc_info=True)
                self._trigger_error_handlers(e)
    
    def _dispose_controllers(self):
        """Clean up controllers"""

        for controller in self._controllers.values():
            if hasattr(controller, 'dispose'):
                controller.dispose()
        self._controllers.clear()
    
    def _cleanup_subscriptions(self):
        """Clean up reactive subscriptions"""

        for subscription in self._reactive_subscriptions:
            if hasattr(subscription, 'dispose'):
                subscription.dispose()
        self._reactive_subscriptions.clear()
    
    def dispose(self):
        """Clean up all page resources"""

        self.will_unmount()
        self.did_unmount()
        DI.delete(EffectManager, f"page_effects_{id(self)}")
        
        # Clear all handlers
        self._event_handlers.clear()
        self._keyboard_shortcuts.clear()
        self._gesture_handlers.clear()
        
        super().dispose() if hasattr(super(), 'dispose') else None
