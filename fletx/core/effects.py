"""
Effect and Hook Management (React-style)

FletX.core.effects module that provides effect and hook management
inspired by React, allowing to create side effects, manage component lifecycles, 
and share data between components in an efficient and reactive way.
"""

import inspect
from typing import Callable, List, Any, Optional, Dict

from fletx.utils import get_logger
# from fletx.core.state import Reactive, ReactiveDependencyTracker


####
##      EFFECT MANAGER CLASS
#####
class EffectManager:
    """
    Centralized Effect Management.
    Effect management mechanism that allows to coordinate and control 
    the application's side effects in a centralized way, to ensure a 
    consistent and predictable execution of effects.
    """
    
    def __init__(self):
        self._effects: Dict[str, 'Effect'] = {}
        self._initialized = False
        
    
    def useEffect(
        self, 
        effect_fn: Callable, 
        dependencies: List[Any] = None,
        key: Optional[str] = None
    ):
        """
        Registers an effect to trigger.
        Registers an effect that will be triggered on certain events or changes, 
        allowing to manage the application's side effects efficiently.

        args:
            effect_fn: Function to execute when the effect is triggered
            dependencies: Re-run the effect only if these dependencies change, to avoid unnecessary executions
            key: Unique key to identify the effect and manage it precisely
        """

        effect_key = key or f"effect_{len(self._effects)}"
        
        # Create or update the effect
        if effect_key not in self._effects:
            self._effects[effect_key] = Effect(effect_fn, dependencies)
        else:
            self._effects[effect_key].update(effect_fn, dependencies)
    
    def runEffects(self):
        """Runs all registered effects"""

        for effect in self._effects.values():
            effect.run()
    
    def dispose(self):
        """Cleans up all effects"""

        for effect in self._effects.values():
            effect.dispose()
        self._effects.clear()


####
##      EFFECT CLASS
#####
class Effect:
    """
    Represents an individual effect
    A single effect that can be executed, 
    with its own dependencies, execution function, 
    and identification key, allowing to manage effects 
    in a precise and isolated way.
    """
    
    def __init__(self, effect_fn: Callable, dependencies: List[Any] = None):
        self.effect_fn = effect_fn
        self.dependencies = dependencies
        self._cleanup_fn = None
        self._last_deps = None
        self._logger = get_logger("FletX.Effect")

    @classmethod
    @property
    def logger(cls):
        if not cls._logger:
            cls._logger = get_logger('FletX.Effect')
        return cls._logger
    
    def run(self):
        """Runs the effect if dependencies have changed"""

        should_run = (
            self.dependencies is None or 
            self._last_deps is None or
            any(dep != last for dep, last in zip(self.dependencies, self._last_deps))
        )
        
        if should_run:
            # Calls the previous cleanup function
            if self._cleanup_fn:
                try:
                    self._cleanup_fn()
                except Exception as e:
                    self.logger.error(f"Cleanup error: {e}", exc_info=True)
            
            # Execute the new effet
            result = self.effect_fn()
            
            # If the effect returns a cleanup function
            if callable(result):
                self._cleanup_fn = result
            else:
                self._cleanup_fn = None
            
            # Remember the last dependencies
            if self.dependencies is not None:
                self._last_deps = self.dependencies.copy()
    
    def update(
        self, 
        effect_fn: Callable, 
        dependencies: List[Any] = None
    ):
        """Updates the effect configuration"""

        self.effect_fn = effect_fn
        self.dependencies = dependencies
    
    def dispose(self):
        """Cleans up the effect"""

        if self._cleanup_fn:
            try:
                self._cleanup_fn()
            except Exception as e:
                self.logger.error(f"Cleanup error on dispose: {e}", exc_info=True)
        self._cleanup_fn = None
