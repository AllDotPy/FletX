"""
Reactive State Management System (inspired by GetX).
A state management system that uses a reactive approach to 
manage data and application states, inspired by the GetX library.
"""

import logging
from typing import (
    Any, Callable, ClassVar, List, Generic, TypeVar, Dict, Optional,
    Set, Union
)
from abc import ABC, abstractmethod
from fletx.utils import get_logger

T = TypeVar('T')
K = TypeVar("K")
V = TypeVar("V")


####
##      REACTIVE DEPENDENCY TACKER
#####
class ReactiveDependencyTracker:
    """
    Reactive Dependency Tracker.
    Tracks and manages dependencies between data and reactive components, 
    allowing for automatic updates to components when a dependency changes.
    """
    
    _current_tracker = None
    
    @classmethod
    def track(cls, computation: Callable):
        """
        Runs a function while tracking its dependencies.
        Runs a function while monitoring and managing the dependencies it uses, 
        allowing for detection and reaction to changes in those dependencies.
        """

        previous_tracker = cls._current_tracker
        cls._current_tracker = set()
        
        try:
            result = computation()
            return result, cls._current_tracker.copy()
        finally:
            cls._current_tracker = previous_tracker


####
##      OBSERVER CLASS
#####
class Observer:
    """
    Enhanced Observer with Lifecycle Management.
    An advanced observer that allows tracking changes in data 
    while managing the observation lifecycle, including creation, 
    update, and disposal of subscriptions.
    """
    
    def __init__(
        self, 
        callback: Callable[[], None], 
        auto_dispose: bool = True
    ):
        self.callback = callback
        self.active = True
        self.auto_dispose = auto_dispose
        self._dependencies = set()

    @property
    def logger(self):
        return get_logger('FletX.Observer')
    
    def add_dependency(self, dependency):
        """
        Adds a reactive dependency.
        Registers a new reactive dependency, 
        allowing to track and react to changes in the associated data.
        """

        self._dependencies.add(dependency)
    
    def notify(self):
        """
        Notifies the observer
        Sends a notification to the observer when the associated data changes, 
        triggering an update or appropriate action.
        """

        if self.active and self.callback:
            try:
                self.callback()
            except Exception as e:
                self.logger.error(f"Observer error: {e}", exc_info=True)
    
    def dispose(self):
        """
        Cleans up resources
        Releases and cleans up associated resources, 
        such as subscriptions, references, or memory, 
        to prevent memory leaks and optimize performance.
        """

        self.active = False
        self.callback = None
        for dep in self._dependencies:
            dep._remove_observer(self)
        self._dependencies.clear()


####
##      REACTIVE CLASS
#####
class Reactive(Generic[T]):
    """
    Reactive Class with Auto Dependency Tracking
    A class that features automatic dependency tracking, 
    allowing for seamless and efficient management of 
    dependencies between data and components.
    """
    
    _logger: ClassVar[logging.Logger] = get_logger("FletX.Reactive")

    def __init__(self, initial_value: T):
        self._value = initial_value
        self._observers: Set[Observer] = set()

    @property
    def logger(cls):
        if not cls._logger:
            cls._logger = get_logger('FletX.Reactive')
        return cls._logger
    
    @property
    def value(self) -> T:
        """
        Dependency-Tracking Getter.
        Tracks the associated dependencies, allowing for automatic 
        updates to components that depend on it.
        """

        if ReactiveDependencyTracker._current_tracker is not None:
            ReactiveDependencyTracker._current_tracker.add(self)
        return self._value
    
    @value.setter
    def value(self, new_value: T):
        """
        Observer-Notifying Setter. 
        Notifies the observers that are subscribed to this property, 
        triggering automatic updates.
        """

        if self._value != new_value:
            old_value = self._value
            self._value = new_value
            self._notify_observers()
            self.logger.debug(f"Value changed: {old_value} → {new_value}")
    
    def listen(
        self, 
        callback: Callable[[], None], 
        auto_dispose: bool = True
    ) -> Observer:
        
        """
        Listens to changes with lifecycle management.
        Listens to changes on a property or object while 
        managing the listening lifecycle, including subscription,
        unsubscription, and error handling.
        """

        observer = Observer(callback, auto_dispose)
        observer.add_dependency(self)
        self._observers.add(observer)
        return observer
    
    def _notify_observers(self):
        """
        Notifies all active observers.
        Sends a notification to all observers that are currently 
        subscribed and listening, allowing them to react to changes or updates.
        """

        for observer in list(self._observers):
            if observer.active:
                observer.notify()
            else:
                self._observers.remove(observer)
    
    def _remove_observer(self, observer: Observer):
        """Removes an observer"""

        if observer in self._observers:
            self._observers.remove(observer)
    
    def dispose(self):
        """Cleans up all dependencies"""

        for observer in list(self._observers):
            observer.dispose()
        self._observers.clear()
    
    def __str__(self):
        return str(self._value)
    
    def __repr__(self):
        return f"Reactive({self.__class__.__name__}, value={self._value})"


####
##      REACTIVE COMPUTED PROPERTIES CLASS
#####
class Computed(Reactive[T]):
    """
    Reactive Computed Value.
    A value that is automatically calculated based on 
    other values or properties, and that updates reactively 
    when any of these dependencies change.
    """
    
    def __init__(
        self, 
        compute_fn: Callable[[], T], 
        dependencies: List[Reactive] = None
    ):
        """
        Args:
            compute_fn: Calculation function
            dependencies: List of dependencies (automatically detected if None)
        """
        # Auto detect dependencies
        if dependencies is None:
            _, dependencies = ReactiveDependencyTracker.track(compute_fn)
        
        super().__init__(compute_fn())
        self._compute_fn = compute_fn
        self._dependencies = dependencies or []
        
        # Subscribing to dependencies
        for dep in self._dependencies:
            self.logger.debug(
                f"Subscribing to dependency: {dep.__class__.__name__}"
            )
            dep.listen(self._update_value)
    
    def _update_value(self):
        """
        Updates the computed value
        Recalculates and updates the value based on the current dependencies.
        """

        new_value, new_deps = ReactiveDependencyTracker.track(self._compute_fn)
        
        # Update dependencies if necessary
        if new_deps != set(self._dependencies):
            # Unsubscribe from old dependencies
            for dep in self._dependencies:
                dep._remove_observer(self._observer)
            
            # Subscribe to newer dependencies
            self._dependencies = list(new_deps)
            for dep in self._dependencies:
                dep.listen(self._update_value)
        
        self.value = new_value
        self.logger.debug(
            f"Computed value updated: {self._value} from dependencies {self._dependencies}"
        )


####
##      REACTIVE INTEGER CLASS
#####
class RxInt(Reactive[int]):
    """
    An integer that can be observed and updated reactively, 
    triggering automatic updates when it changes.
    """
    
    def __init__(self, initial_value: int = 0):
        super().__init__(initial_value)
    
    def increment(self, step: int = 1):
        """Increment the object's value"""
        self.value += step
    
    def decrement(self, step: int = 1):
        """Decrement the object's value"""
        self.value -= step


####
##      REACTIVE STR CLASS
#####
class RxStr(Reactive[str]):
    """
    A string that can be observed and updated reactively, 
    triggering automatic updates when it changes.
    """
    
    def __init__(self, initial_value: str = ""):
        super().__init__(initial_value)
    
    def append(self, text: str):
        """Append text to value"""
        self.value += text
    
    def clear(self):
        """Clear the value"""
        self.value = ""


####
##      REACTIVE BOOLEAN CLASS
#####
class RxBool(Reactive[bool]):
    """
    A boolean value that can be observed and updated reactively, 
    triggering automatic updates when it changes.
    """
    
    def __init__(self, initial_value: bool = False):
        super().__init__(initial_value)
    
    def toggle(self):
        """Inverts the value"""
        self.value = not self.value


####
##      REACTIVE LIST CLASS
#####
class RxList(Reactive[List[T]]):
    """
    A list that can be observed and updated reactively, 
    triggering automatic updates when it changes, whether by adding, 
    removing, or modifying elements.
    """
    
    def __init__(self, initial_value: List[T] = None):
        super().__init__(initial_value or [])
    
    def append(self, item: T):
        """Append item to value"""
        self._value.append(item)
        self._notify_observers()
    
    def remove(self, item: T):
        """Remove item from value"""
        if item in self._value:
            self._value.remove(item)
            self._notify_observers()
    
    def clear(self):
        """clear value"""
        self._value.clear()
        self._notify_observers()

    def pop(self,idx: int = -1):
        """pop an element equivalent to list.pop()"""

        item = self._value.pop(idx)
        self._notify_observers()
        return item
    
    def extend(self, other: list):
        """Extends current RxList with the given pthon list."""

        self._value.extend(other)
        self._notify_observers()
    
    def __len__(self):
        return len(self._value)
    
    def __getitem__(self, index):
        return self._value[index]
    
    def __setitem__(self, index, value):
        self._value[index] = value
        self._notify_observers()


####
##      REACTIVE DICT CLASS
#####
class RxDict(Generic[T],Reactive[Dict[str, T]]):
    """
    A dictionary that can be observed and updated reactively, 
    triggering automatic updates when it changes, whether by adding, 
    removing, or modifying keys or values.
    """
    
    def __init__(self, initial_value: Dict[str, T] = None):
        super().__init__(initial_value or {})
    
    def __getitem__(self, key: str):
        return self._value[key]
    
    def __setitem__(self, key: str, value: T):
        self._value[key] = value
        self._notify_observers()
    
    def __delitem__(self, key: str):
        if key in self._value:
            del self._value[key]
            self._notify_observers()
    
    def get(self, key: str, default: T = None):
        """
        Gets a value with default.
        Retrieves a value from a dictionary or other data source, 
        returning a default value if the key or property does not exist.
        """

        return self._value.get(key, default)
    
    def update(self, other: Dict[str, T]):
        """
        Updates with another dictionary.
        Updates the current dictionary with the keys and values
        from another dictionary, overwriting existing values if 
        the keys are the same.
        """

        self._value.update(other)
        self._notify_observers()
    
    def clear(self):
        """
        Clears the dictionary.
        Removes all keys and values from the dictionary, leaving it empty.
        """
        self._value.clear()
        self._notify_observers()
