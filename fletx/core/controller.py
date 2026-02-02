"""
Base Controller for FletX.
fletx.core.controller module that provides a basic implementation for 
controllers in FletX, allowing to manage interactions between views and data models, 
and to facilitate the creation of robust and maintainable applications.
"""

from typing import (
    List, Callable, Any, Dict, 
    Optional, TypeVar, Union
)
import asyncio
import weakref
import logging
from enum import Enum

from fletx.core.di import DI
from fletx.core.effects import EffectManager
from fletx.core.state import (
    Reactive, RxInt, RxStr, RxBool, RxList, RxDict, 
    Computed, Observer, # ReactiveDependencyTracker
)
from fletx.utils import get_logger, get_event_loop

# GENERIC TYPE
T = TypeVar('T')


####
##      CONTROLLER STATE
#####
class ControllerState(Enum):
    """Lifrcycle states of a controller"""

    CREATED = "created"
    INITIALIZED = "initialized" 
    READY = "ready"
    DISPOSED = "disposed"


####
##      CONTROLLER EVENT
#####
class ControllerEvent:
    """Represents a fletx contoller event"""

    def __init__(
        self, 
        type: str, 
        data: Any = None, 
        source: Any = None
    ):
        self.type = type
        self.data = data
        self.source = source
        # self.timestamp = get_event_loop().time()


####
##      CONTROLLER EVENT BUS
#####
class EventBus:
    """Reactive Event Bus for inter-controller communication"""

    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
        self._once_listeners: Dict[str, List[Callable]] = {}
        self._event_history: RxList[ControllerEvent] = RxList([])
        self._last_event: Reactive[Optional[ControllerEvent]] = Reactive(None)
        self.logger = get_logger('FletX.EventBus')

    @property
    def last_event(self) -> Reactive[Optional[ControllerEvent]]:
        """Last emited event (reactive)"""
        return self._last_event
    
    @property
    def event_history(self) -> RxList[ControllerEvent]:
        """Events history (reactive)"""
        return self._event_history
    
    def on(self, event_type: str, callback: Callable):
        """Listen to an event"""

        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)
    
    def once(self, event_type: str, callback: Callable):
        """Liste to an event only one time (once)"""

        if event_type not in self._once_listeners:
            self._once_listeners[event_type] = []
        self._once_listeners[event_type].append(callback)
    
    def off(self, event_type: str, callback: Callable = None):
        """Remove a listener"""

        if callback is None:
            # Remove all listenrs of this event_type
            self._listeners.pop(event_type, None)
            self._once_listeners.pop(event_type, None)

        # Remove a specific listener
        else:
            # Remove it from Normal listeners
            if event_type in self._listeners:
                self._listeners[event_type] = [
                    l for l in self._listeners[event_type] if l != callback
                ]

            # Try removing it from Once listeners
            if event_type in self._once_listeners:
                self._once_listeners[event_type] = [
                    l for l in self._once_listeners[event_type] if l != callback
                ]
    
    def emit(
        self, 
        event: Union[str, ControllerEvent], 
        data: Any = None
    ):
        """Emit a Controller Event"""

        # Parse event if needed
        if isinstance(event, str):
            event = ControllerEvent(event, data)

        # Update reactive state
        self._last_event.value = event
        self._event_history.append(event)
        
        # Execute normal listeners
        if event.type in self._listeners:
            for callback in self._listeners[event.type]:

                try:
                    # Coroutine callback
                    if asyncio.iscoroutinefunction(callback):
                        get_event_loop().create_task(callback(event))

                    # A non coroutine function
                    else:
                        callback(event)

                # Error in the callback
                except Exception as e:
                    self.logger.error(
                        f"Error when executing {callback.__name__} callback: {e}"
                    )
        
        # Execute Once listeners and then remove them
        if event.type in self._once_listeners:
            listeners = self._once_listeners[event.type].copy()

            # Clear event type listeners
            self._once_listeners[event.type].clear()

            # Then Execute each callback
            for callback in listeners:

                try:
                    # Coroutine callback
                    if asyncio.iscoroutinefunction(callback):
                        get_event_loop.create_task(callback(event))

                    # Non coroutine callback
                    else:
                        callback(event)

                except Exception as e:
                    logging.error(
                        f"Error when executing {callback.__name__} callback: {e}"
                    )

    def listen_reactive(
        self, 
        event_type: str
    ) -> Computed[List[ControllerEvent]]:
        """Return a computed property that filters events by type"""

        return Computed(
            lambda: [e for e in self._event_history.value if e.type == event_type]
        )
    
    def dispose(self):
        """Clean up event bus"""

        self._listeners.clear()
        self._once_listeners.clear()
        self._event_history.dispose()
        self._last_event.dispose()


####
##      REACTIVE CONTEXT
#####
class ControllerContext:
    """Reactive context with integrated state management."""

    def __init__(self):
        self._context: RxDict[Any] = RxDict({})
        self._logger = get_logger("FletX.ControllerContext")

    @property
    def data(self) -> RxDict[Any]:
        """Returns context data (reactive)"""

        return self._context
    
    def set(self, key: str, value: Any):
        """Defines a new key value in the context"""

        self._context[key] = value

    def get(self, key: str, default: Any = None):
        """Get a context value by key"""

        return self._context.get(key, default)
    
    def get_reactive(
        self, 
        key: str, 
        default: Any = None
    ) -> Computed[Any]:
        """Get a reactive value from context"""

        return Computed(lambda: self._context.get(key, default))
    
    def has(self, key: str) -> bool:
        """Checks if context has a given key"""

        return key in self._context.value
    
    def has_reactive(self, key: str) -> Computed[bool]:
        """Reactive version of has() method"""

        return Computed(lambda: key in self._context.value)
    
    def remove(self, key: str):
        """Removes a given key from context data"""

        if key in self._context.value:
            del self._context[key]

    def update(self, **kwargs):
        """Updates many values"""

        for key, value in kwargs.items():
            self._context[key] = value
    
    def clear(self):
        """Clear context"""
        self._context.clear()
    
    def listen(self, callback: Callable[[], None]) -> Observer:
        """Handles a context change."""

        return self._context.listen(callback)
    
    def dispose(self):
        """Dispose context."""

        self._context.dispose()


####
##      FLETX BASE CONTROLLER CLASS
#####
class FletXController:
    """
    Advanced Controller with Reactivity and Enhanced Features.
    A controller that incorporates reactivity features, lifecycle management,
    event handling, and dependency injection to create robust applications.
    """
    
    _instances: weakref.WeakSet = weakref.WeakSet()
    _global_event_bus: EventBus = EventBus()
    _global_context: ControllerContext = ControllerContext()
    _logger = get_logger("FletXController")
    # _effects_manager: EffectManager = None

    def __init__(self,auto_initialize: bool = True):
        self._effects = EffectManager()
        self._state: Reactive[ControllerState] = Reactive(ControllerState.CREATED)
        self._event_bus: EventBus = EventBus()
        self._children: RxList['FletXController'] = RxList([])
        self._parent: Reactive[Optional['FletXController']] = Reactive(None)
        self._context: ControllerContext = ControllerContext()
        self._cleanup_tasks: List[Callable] = []
        self._disposed: bool = False
        self._id: int = id(self)

        # Reactive states
        self._is_loading: RxBool = RxBool(False)
        self._error_message: RxStr = RxStr("")
        self._is_ready: RxBool = RxBool(False)

        # Global registration
        FletXController._instances.add(self)
        
        # Register effets Manager
        DI.put(self._effects, f"effects_{self._id}")
        DI.put(self, f"controller_{self._id}")

        # Setup lifecycle effects
        self._setup_lifecycle_effects()

        # Auto Initialize
        if auto_initialize:
            self.initialize()

    @property
    def state(self) -> ControllerState:
        """Current state of the controller"""
        return self._state
    
    @property
    def is_disposed(self) -> bool:
        """Check if controller is disposed"""
        return self._state == ControllerState.DISPOSED

    @property
    def effects(self) -> EffectManager:
        """Gets the effect manager"""

        self._check_not_disposed()
        return DI.find(EffectManager, f"effects_{self._id}")
    
    @property
    def event_bus(self) -> EventBus:
        f"""{self.__class__.__name__}'s Local Event Bus"""

        return self._event_bus
    
    @property
    def global_event_bus(self) -> EventBus:
        """Global Event Bus"""

        return FletXController._global_event_bus
    
    @property
    def context(self) -> Dict[str, Any]:
        """Controller's shared context"""

        return self._context
    
    def _setup_lifecycle_effects(self):
        """Setup reactive lifecycle effets"""

        # State Change effects
        self._state.listen(lambda: self._on_state_change())
        
        # Controller loading state effects
        self._is_loading.listen(lambda: self._on_loading_change())
        
        # Errors 
        self._error_message.listen(lambda: self._on_error_change())

    def _on_state_change(self):
        """Handler for state changes"""

        current_state = self._state.value
        self._logger.debug(f"State changes: {current_state}")
        
        # Update ready state
        self._is_ready.value = current_state == ControllerState.READY
        
        # Emit appropiated events
        self.emit_local("state_changed", current_state)
        
        # Call the appropriate lifecycle hook
        # Controller is initialized
        if current_state == ControllerState.INITIALIZED:
            self.on_initialized()

            # Now ready the controller
            self.ready()
        
        # Controller is ready?
        elif current_state == ControllerState.READY:
            self.on_ready()

        # Controller is disposed?
        elif current_state == ControllerState.DISPOSED:
            self.on_disposed()

    def _on_loading_change(self):
        """Loading state changes handler"""

        self.emit_local("loading_changed", self._is_loading.value)

    def _on_error_change(self):
        """Error changes handler"""

        if self._error_message.value:
            self.emit_local("error", self._error_message.value)
    
    def _check_not_disposed(self):
        """Ensure the controller is not disposed"""

        if self.is_disposed:
            raise RuntimeError(
                f"Controller {self.__class__.__name__} is disposed"
            )

    def initialize(self):
        """Initialize the controller"""

        if self._state.value != ControllerState.CREATED:
            return self
        
        self._state.value = ControllerState.INITIALIZED
        return self
    
    def ready(self):
        """Mark the controller as ready"""

        if self._state != ControllerState.INITIALIZED:
            return self
            
        self._effects.runEffects()
        self._state.value = ControllerState.READY
        return self

    def dispose(self):
        """Nettoie toutes les ressources"""
        if self.is_disposed:
            return
        
        # Dispose children
        for child in self._children.copy():
            child.dispose()
        
        # Remove from tree
        if self._parent:
            self._parent._remove_child(self)
        
        # Execute cleanup tasks
        for cleanup_task in self._cleanup_tasks:
            try:
                cleanup_task()
            except Exception as e:
                self._logger.error(
                    f"Error during execution of {cleanup_task.__name__} task: {e}"
                )
        
        # Clean up effects
        self._effects.dispose()
        
        # Clean up event bus and context
        self._event_bus.dispose()
        self._context.dispose()

        # Clean up reactive states
        self._state.dispose()
        self._children.dispose()
        self._parent.dispose()
        self._is_loading.dispose()
        self._error_message.dispose()
        self._is_ready.dispose()
                
        self._state.value = ControllerState.DISPOSED

    def on_initialized(self):
        """Hook called when initializing controller"""
        pass

    def on_ready(self):
        """Hook called when the controller is ready"""
        pass
    
    def on_disposed(self):
        """Hook called when disposing controller"""
        pass
    
    def add_child(self, child: 'FletXController'):
        """Add a child Controller"""

        self._check_not_disposed()

        if child not in self._children.value:
            self._children.append(child)
            child._parent.value = self

            # Emit child added
            self.emit_local("child_added", child)
    
    def remove_child(self, child: 'FletXController'):
        """Remode a child controller"""

        if child in self._children.value:
            self._children.remove(child)
            child._parent.value = None

            # Emit child removed
            self.emit_local("child_removed", child)
            
    def use_effect(
        self, 
        effect_fn: Callable, 
        deps: List[Any] = None, 
        key: Optional[str] = None
    ):
        """Add a reactive effect to the controller."""
        self._check_not_disposed()
        
        # Create a wrapper if dependencies are provided
        if deps and any(isinstance(dep, Reactive) for dep in deps):
            reactive_deps = [dep for dep in deps if isinstance(dep, Reactive)]
            
            def reactive_effect():
                # Track reactive deps
                for dep in reactive_deps:
                    _ = dep.value  # Start tracking
                return effect_fn()
            
            return self._effects.useEffect(reactive_effect, deps, key)
        
        # juste run the effect
        else:
            return self._effects.useEffect(effect_fn, deps, key)
    
    def add_effect(
        self, 
        effect_fn: Callable, 
        deps: List[Any] = None, 
        key: Optional[str] = None
    ):
        """Alias for use_effect"""

        return self.use_effect(effect_fn, deps, key)
    
    def emit_local(self, event_type: str, data: Any = None):
        """Emit an event locally (reactive)"""

        self._check_not_disposed()
        self._event_bus.emit(event_type, data)

    def emit_global(self, event_type: str, data: Any = None):
        """Emit an event globally (reactive)"""

        self._check_not_disposed()
        self._global_event_bus.emit(event_type, data)

    def on_local(self, event_type: str, callback: Callable):
        """Listen to a local event"""

        self._check_not_disposed()
        self._event_bus.on(event_type, callback)
        return self
    
    def on_global(self, event_type: str, callback: Callable):
        """Listen to a global event"""

        self._check_not_disposed()
        self._global_event_bus.on(event_type, callback)
        return self
    
    def listen_reactive_local(
        self, event_type: str
    ) -> Computed[List[ControllerEvent]]:
        """Listen reactively to a local event"""

        self._check_not_disposed()
        return self._event_bus.listen_reactive(event_type)
    
    def listen_reactive_global(
        self, event_type: str
    ) -> Computed[List[ControllerEvent]]:
        
        """Listen reactively to a global event"""
        self._check_not_disposed()
        return self._global_event_bus.listen_reactive(event_type)
    
    def once_local(
        self, 
        event_type: str, 
        callback: Callable
    ):
        """Listen a local event only one time"""

        self._check_not_disposed()
        self._event_bus.once(event_type, callback)
        return self
    
    def once_global(
        self, 
        event_type: str, 
        callback: Callable
    ):
        """Listen to a global event only one time"""

        self._check_not_disposed()
        self._global_event_bus.once(event_type, callback)
        return self
    
    def off_local(
        self, 
        event_type: str, 
        callback: Callable = None
    ):
        """Remove a local event listener"""

        if not self.is_disposed:
            self._event_bus.off(event_type, callback)
        return self
    
    def off_global(
        self, 
        event_type: str, 
        callback: Callable = None
    ):
        """Remove a global event listener"""

        if not self.is_disposed:
            self._global_event_bus.off(event_type, callback)
        return self
    
    def set_context(self, key: str, value: Any):
        """Define a value in local context"""

        self._check_not_disposed()
        self._context.set(key, value)
        return self
    
    def get_context(self, key: str, default: Any = None):
        """Get value from local context"""

        return self._context.get(key, default)
    
    def get_context_reactive(
        self, 
        key: str, 
        default: Any = None
    ) -> Computed[Any]:
        """Get a reactive value from local context"""

        self._check_not_disposed()
        return self._context.get_reactive(key, default)
    
    def has_context(self, key: str) -> bool:
        """Check a given key exists in local context"""

        return self._context.has(key)
    
    def has_context_reactive(self, key: str) -> Computed[bool]:
        """Reactive version of has_context"""

        self._check_not_disposed()
        return self._context.has_reactive(key)
    
    def remove_context(self, key: str):
        """Remove a given key value from local context"""

        self._context.remove(key)
        return self
    
    def update_context(self, **kwargs):
        """Update many values in local context"""

        self._check_not_disposed()
        self._context.update(**kwargs)
        return self
    
    def listen_context(
        self, 
        callback: Callable[[], None]
    ) -> Observer:
        """Listen changes within local context"""

        self._check_not_disposed()
        return self._context.listen(callback)
    
    def set_global_context(self, key: str, value: Any):
        """Define or update a value in global context"""

        self._check_not_disposed()
        self._global_context.set(key, value)
        return self
    
    def get_global_context(
        self, 
        key: str, 
        default: Any = None
    ):
        """get a given key value from global context"""

        return self._global_context.get(key, default)
    
    def get_global_context_reactive(
        self, 
        key: str, 
        default: Any = None
    ) -> Computed[Any]:
        """get a reactive value from global context"""

        self._check_not_disposed()
        return self._global_context.get_reactive(key, default)
    
    def create_reactive(self, initial_value: T) -> Reactive[T]:
        """Create a reactive object attached to the controller"""

        self._check_not_disposed()
        reactive_var = Reactive(initial_value)
        self.add_cleanup(reactive_var.dispose)
        return reactive_var
    
    def create_rx_int(self, initial_value: int = 0) -> RxInt:
        """Create a reactive Integer (RxInt)"""

        self._check_not_disposed()
        rx_int = RxInt(initial_value)
        self.add_cleanup(rx_int.dispose)
        return rx_int
    
    def create_rx_str(self, initial_value: str = "") -> RxStr:
        """Create a reactive str (RxStr)"""

        self._check_not_disposed()
        rx_str = RxStr(initial_value)
        self.add_cleanup(rx_str.dispose)
        return rx_str
    
    def create_rx_bool(self, initial_value: bool = False) -> RxBool:
        """Create a reactive boolean (RxBool)"""

        self._check_not_disposed()
        rx_bool = RxBool(initial_value)
        self.add_cleanup(rx_bool.dispose)
        return rx_bool
    
    def create_rx_list(self, initial_value: List[T] = None) -> RxList[T]:
        """Create a reactive list (RxList)"""

        self._check_not_disposed()
        rx_list = RxList(initial_value)
        self.add_cleanup(rx_list.dispose)
        return rx_list
    
    def create_rx_dict(
        self, 
        initial_value: Dict[str, T] = None
    ) -> RxDict[T]:
        """Create a reactive Dict (RxDict)"""

        self._check_not_disposed()
        rx_dict = RxDict(initial_value)
        self.add_cleanup(rx_dict.dispose)
        return rx_dict
    
    def create_computed(
        self, 
        compute_fn: Callable[[], T]
    ) -> Computed[T]:
        """Create a reactive property"""

        self._check_not_disposed()
        computed = Computed(compute_fn)
        self.add_cleanup(computed.dispose)
        return computed
    
    def add_cleanup(self, cleanup_fn: Callable):
        """Add a cleanup task"""

        self._check_not_disposed()
        self._cleanup_tasks.append(cleanup_fn)
        return self
    
    def set_loading(self, loading: bool):
        """Updates loading state"""

        self._check_not_disposed()
        self._is_loading.value = loading
        return self
    
    def set_error(self, error: str):
        """Update controller's error message"""

        self._check_not_disposed()
        self._error_message.value = error
        return self
    
    def clear_error(self):
        """clear controller's error message"""

        self._check_not_disposed()
        self._error_message.value = ""
        return self
    
    def chain(self, *methods):
        """Allow methods execution in chain"""

        for method in methods:
            if callable(method):
                method(self)
        return self
    
    @classmethod
    def get_all_instances(cls) -> List['FletXController']:
        """Get all active controllers"""
        return list(cls._instances)
    
    @classmethod
    def find_by_type(cls, controller_type: type) -> List['FletXController']:
        """Retrieve a controller instance by type"""

        return [
            instance for instance in cls._instances 
            if isinstance(instance, controller_type)
        ]
    
    def __repr__(self):
        return (
            f"<{self.__class__.__name__}"
            f"(state={self._state.value.value}, id={self._id})>"
        )
    
    def __enter__(self):
        """Support for context manager"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Auto dispose when exiting"""
        self.dispose()