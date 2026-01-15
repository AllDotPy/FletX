"""
Decorators for reactivity.

These decorators enable reactive programming patterns by automatically 
tracking dependencies and updating components when underlying data changes,
facilitating seamless UI updates.
"""

import asyncio
import time
from typing import (
    Callable, Any, TypeVar, Dict, Union,
    List, Optional, Tuple, Set
)
from functools import wraps

from fletx.core.state import (
    Reactive, ReactiveDependencyTracker, Computed,
    Observer
)
from fletx.utils import get_logger, get_event_loop


T = TypeVar('T')
F = TypeVar('F', bound = Callable[..., Any])

logger = get_logger('FletX.Decorators.Reactive')


####
##      REACTIVE BATCH DECORATOR
#####
class BatchManager:
    """Manages batched reactive updates"""
    
    def __init__(self):
        self.pending_updates: Set[Callable] = set()
        self.batch_scheduled = False
    
    def add_update(self, update_fn: Callable):
        self.pending_updates.add(update_fn)
        if not self.batch_scheduled:
            self.batch_scheduled = True
            asyncio.create_task(self._flush_batch())
    
    async def _flush_batch(self):
        await asyncio.sleep(0)  # Next tick
        updates = list(self.pending_updates)
        self.pending_updates.clear()
        self.batch_scheduled = False
        
        logger.debug(f"Flushing batch of {len(updates)} updates")
        for update in updates:
            try:
                update()
            except Exception as e:
                logger.error(f"Error in batched update: {e}")

_batch_manager = BatchManager()


####
##      BATCH DECORATOR
#####
def reactive_batch():
    """
    Batches reactive updates to execute on the next tick.
    
    Usage:
    ```python
    @reactive_batch()
    def batch_update(items: RxList):
        # Multiple rapid changes will be batched
        update_list_display(items.value)
    ```
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            update_fn = lambda: func(*args, **kwargs)  # noqa: E731
            _batch_manager.add_update(update_fn)
            logger.debug(f"Batched {func.__name__} for next tick")
        
        return wrapper
    
    return decorator


####
##      REACTIVE MEMO DECORATOR
#####
class ReactiveMemoryCache:
    """Cache for memoized reactive computations"""
    
    def __init__(self, maxsize: int = 128):
        self.maxsize = maxsize
        self.cache: Dict[str, Tuple[Any, Set[Reactive]]] = {}
        self.access_order: List[str] = []
    
    def get(self, key: str) -> Optional[Tuple[Any, Set[Reactive]]]:
        if key in self.cache:
            # Move to end (most recently used)
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
    
    def set(self, key: str, value: Any, dependencies: Set[Reactive]):
        if len(self.cache) >= self.maxsize and key not in self.cache:
            # Remove least recently used
            oldest_key = self.access_order.pop(0)
            del self.cache[oldest_key]
        
        self.cache[key] = (value, dependencies)
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
    
    def invalidate(self, key: str):
        if key in self.cache:
            del self.cache[key]
            self.access_order.remove(key)


####
##      REACTIVE MEMO DECORATOR
#####
def reactive_memo(
    maxsize: int = 128,
    key_fn: Optional[Callable[..., str]] = None
):
    """
    Memoizes reactive computations with dependency tracking.
    
    Args:
        maxsize: Maximum number of cached results
        key_fn: Custom function to generate cache keys
    
    Usage:
    ```python
    @reactive_memo(maxsize=64)
    def expensive_computation(rx_a: RxInt, rx_b: RxInt):
        return rx_a.value * rx_b.value + complex_calculation()
    ```
    """
    cache = ReactiveMemoryCache(maxsize)
    
    def decorator(func: F) -> F:
        dependency_observers: Dict[str, List[Observer]] = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_fn:
                cache_key = key_fn(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}_{hash((args, tuple(kwargs.items())))}"
            
            # Check cache
            cached = cache.get(cache_key)
            if cached:
                result, deps = cached
                logger.debug(f"Cache hit for {cache_key}")
                return result
            
            # Track dependencies during computation
            result, dependencies = ReactiveDependencyTracker.track(
                lambda: func(*args, **kwargs)
            )
            
            # Cache result
            cache.set(cache_key, result, dependencies)
            
            # Set up invalidation observers
            observers = []
            for dep in dependencies:
                observer = dep.listen(
                    lambda k=cache_key: cache.invalidate(k),
                    auto_dispose=False
                )
                observers.append(observer)
            
            dependency_observers[cache_key] = observers
            logger.debug(f"Cached {cache_key} with {len(dependencies)} dependencies")
            
            return result
        
        wrapper.cache = cache
        wrapper.clear_cache = lambda: cache.cache.clear()
        return wrapper
    
    return decorator


####
##      DEBOUNCE DECORATOR
#####
def reactive_debounce(delay: float):
    """
    Debounces reactive updates with a specified delay.
    
    Args:
        delay: Delay in seconds before executing the function
    
    Usage:
    ```python
    @reactive_debounce(0.5)
    def search_handler(query: RxStr):
        # This will only execute 0.5s after the last change
        perform_search(query.value)
    ```
    """
    def decorator(func: F) -> F:
        pending_calls: Dict[str, asyncio.Task] = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            call_id = f"{id(func)}_{hash((args, tuple(kwargs.items())))}"
            
            # Cancel previous call if exists
            if call_id in pending_calls and not pending_calls[call_id].done():
                pending_calls[call_id].cancel()
            
            async def delayed_call():
                await asyncio.sleep(delay)
                try:
                    if asyncio.iscoroutinefunction(func):
                        await func(*args, **kwargs)
                    else:
                        func(*args, **kwargs)

                except asyncio.CancelledError:
                    logger.debug(f"Debounced call {call_id} was cancelled")

                except Exception as e:
                    logger.exception(f"Error in debounced function: {e}")

                finally:
                    if call_id in pending_calls:
                        del pending_calls[call_id]

            # loop = get_event_loop()
            # Schedule new call
            task = get_event_loop().create_task(delayed_call())
            pending_calls[call_id] = task
            
            logger.debug(f"Debounced {func.__name__} with delay {delay}s")
        
        return wrapper
    
    return decorator

####
##      THROTTLE DECORATOR
#####
def reactive_throttle(interval: float):
    """
    Throttles reactive updates to execute at most once per interval.
    
    Args:
        interval: Minimum time between executions in seconds
    
    Usage:
    ```python
    @reactive_throttle(1.0)
    def update_ui(data: RxList):
        # This will execute at most once per second
        refresh_display(data.value)
    ```
    """
    def decorator(func: F) -> F:
        last_called: Dict[str, float] = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            call_id = f"{id(func)}_{hash((args, tuple(kwargs.items())))}"
            now = time.time()
            
            if call_id not in last_called or now - last_called[call_id] >= interval:
                last_called[call_id] = now
                logger.debug(f"Throttled execution of {func.__name__}")
                return func(*args, **kwargs)
            else:
                logger.debug(f"Throttled {func.__name__} - too soon")
        
        return wrapper
    
    return decorator

####
##      CONDITIONAL REACTIVE DECORATOR
#####
def reactive_when(condition: Union[Callable[[], bool], Reactive[bool]]):
    """
    Executes reactive function only when condition is True.
    
    Args:
        condition: Boolean condition or reactive boolean
    
    Usage:
    ```python
    is_enabled = RxBool(True)
    
    @reactive_when(is_enabled)
    def conditional_update(data: RxStr):
        # Only executes when is_enabled.value is True
        update_display(data.value)
    ```
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if isinstance(condition, Reactive):
                should_execute = condition.value
            else:
                should_execute = condition()
            
            if should_execute:
                logger.debug(f"Conditional execution of {func.__name__} - condition met")
                return func(*args, **kwargs)
            else:
                logger.debug(f"Conditional execution of {func.__name__} - condition not met")
        
        return wrapper
    
    return decorator

####
##      REACTIVE SELECTOR DECORATOR
#####
def reactive_select(*reactive_props: Reactive):
    """
    Creates a selector that only triggers when specific reactive properties change.
    
    Args:
        *reactive_props: Reactive properties to watch
    
    Usage:
    ```python
    name = RxStr("John")
    age = RxInt(25)
    
    @reactive_select(name)  # Only triggers when name changes, not age
    def update_name_display():
        return f"Name: {name.value}"
    ```
    """
    def decorator(func: F) -> F:
        observers: List[Observer] = []
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # Set up observers for selected properties
        for prop in reactive_props:
            observer = prop.listen(
                lambda: wrapper(),
                auto_dispose=False
            )
            observers.append(observer)
        
        wrapper.dispose = lambda: [obs.dispose() for obs in observers]
        logger.debug(f"Created reactive selector for {len(reactive_props)} properties")
        
        return wrapper
    
    return decorator

####
##      REACTIVE EFFECT DECORATOR
#####
def reactive_effect(
    dependencies: Optional[List[Reactive]] = None,
    auto_run: bool = True
):
    """
    Creates a reactive effect that runs when dependencies change.
    
    Args:
        dependencies: List of reactive dependencies (auto-detected if None)
        auto_run: Whether to run the effect immediately
    
    Usage:
    ```python
    counter = RxInt(0)
    
    @reactive_effect([counter])
    def log_counter_changes():
        print(f"Counter changed to: {counter.value}")
    ```
    """
    def decorator(func: F) -> F:
        observers: List[Observer] = []

        _self = None
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Auto-detect dependencies if not provided
            if dependencies is None:
                result, deps = ReactiveDependencyTracker.track(
                    lambda: func(*args, **kwargs)
                )
                
                # Set up observers for detected dependencies
                for dep in deps:
                    observer = dep.listen(
                        lambda: func(*args, **kwargs),
                        auto_dispose = False
                    )
                    observers.append(observer)
                
                logger.debug(f"Effect {func.__name__} auto-detected {len(deps)} dependencies")
                return result
            
            # Use provided dependencies else
            else:
                for dep in dependencies:
                    observer = dep.listen(
                        lambda: func(*args, **kwargs),
                        auto_dispose = False
                    )
                    observers.append(observer)
                
                logger.debug(f"Effect {func.__name__} using {len(dependencies)} dependencies")
                return func(*args, **kwargs)
        
        wrapper.dispose = lambda: [obs.dispose() for obs in observers]
        
        # Auto-run if enabled
        if auto_run:
            wrapper(_self)
        
        return wrapper
    
    return decorator

####
##      REACTIVE COMPUTED DECORATOR
#####
def reactive_computed(dependencies: Optional[List[Reactive]] = None):
    """
    Creates a computed reactive value from a function.
    
    Args:
        dependencies: List of reactive dependencies (auto-detected if None)
    
    Usage:
    ```python
    first_name = RxStr("John")
    last_name = RxStr("Doe")
    
    @reactive_computed([first_name, last_name])
    def full_name():
        return f"{first_name.value} {last_name.value}"
    
    # full_name is now a Reactive[str] that updates automatically
    """
    def decorator(func: F) -> Reactive:
        return Computed(func, dependencies)
    
    return decorator
