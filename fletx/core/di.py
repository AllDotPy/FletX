"""
Dependency Injection System.
fletx.core.di module that provides a dependency injection 
system to manage dependencies between application components, 
allowing to create modular, flexible, and maintainable applications.
"""

import logging
from threading import Lock
from typing import Dict, Any, Type, Optional, TypeVar, ClassVar
from fletx.utils import get_logger
from fletx.utils.exceptions import DependencyNotFoundError

T = TypeVar('T')


####
##      DEPENDENCY INJECTOR CLASS
#####
class DI:
    """
    Dependency Injection Container.
    A container that manages instances of dependencies and provides them 
    to application components, allowing to decouple dependencies and manage 
    them in a centralized way.
    """
    
    _instances: Dict[str, Any] = {}
    logger: ClassVar[logging.Logger] = get_logger("FletX.DI")
    
    @classmethod
    def put(cls, instance: T, tag: Optional[str] = None) -> T:
        """Registers an instance in the container"""

        key = cls._get_key(type(instance), tag)
        cls._instances[key] = instance
        cls.logger.debug(f"Instance registered: {key}")
        return instance
    
    @classmethod
    def find(cls, cls_type: Type[T], tag: Optional[str] = None) -> Optional[T]:
        """Gets an instance from the container"""

        key = cls._get_key(cls_type, tag)
        instance = cls._instances.get(key)
        
        if instance:
            cls.logger.debug(f"Instance found: {key}")
            return instance
        
        # Search withou tag if not found with tag.
        if tag:
            no_tag_key = cls._get_key(cls_type, None)
            instance = cls._instances.get(no_tag_key)
            if instance:
                cls.logger.debug(f"Instance with no tag: {no_tag_key}")
                return instance
        
        return None
    
    @classmethod
    def get(cls, cls_type: Type[T], tag: Optional[str] = None) -> T:
        """Gets an instance from the container (throws an exception if not found)"""

        instance = cls.find(cls_type, tag)
        if instance is None:
            key = cls._get_key(cls_type, tag)
            raise DependencyNotFoundError(f"Dependencey not found: {key}")
        return instance
    
    @classmethod
    def delete(cls, cls_type: Type, tag: Optional[str] = None) -> bool:
        """Removes an instance from the container"""

        key = cls._get_key(cls_type, tag)
        if key in cls._instances:
            # Call dispose if available
            instance = cls._instances[key]
            if hasattr(instance, 'dispose'):
                instance.dispose()
            
            del cls._instances[key]
            cls.logger.debug(f"Instance removed: {key}")
            return True
        return False
    
    @classmethod
    def reset(cls):
        """Resets the container"""

        # Dispose all instances
        for instance in cls._instances.values():
            if hasattr(instance, 'dispose'):
                try:
                    instance.dispose()
                except Exception as e:
                    cls.logger.error(f"Error when disposing instance: {e}")
        
        cls._instances.clear()
        cls.logger.debug("DI container reset was successful")
    
    @classmethod
    def _get_key(cls, cls_type: Type, tag: Optional[str]) -> str:
        """Generates a unique key for the container"""

        base_key = f"{cls_type.__module__}.{cls_type.__name__}"
        return f"{base_key}#{tag}" if tag else base_key
    
    @classmethod
    def list_instances(cls) -> Dict[str, Any]:
        """Lists all registered instances (for debug)"""
        
        return cls._instances.copy()