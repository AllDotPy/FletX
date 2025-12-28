"""
FletX - A lightweight dependency injection framework inspired by GetX for Flet applications.
"""

from fletx.core.di import DI


__version__ = "0.1.4.b3"

####
##    FLETX - DEPENDENCY INJECTION INTERFACE
####
class FletX:
    """FletX Dependency Injection Interface
    This class provides a simple interface to interact with the Dependency Injection (DI) container.
    It allows to register, find, delete, and reset instances in the DI container.
    """
    
    @staticmethod
    def put(instance, tag=None):
        """Register an instance in the DI container"""
        return DI.put(instance, tag)
    
    @staticmethod
    def find(cls, tag=None):
        """Retrieve an instance from the DI container"""
        return DI.find(cls, tag)
    
    @staticmethod
    def delete(cls, tag=None):
        """Delete an instance from the DI container"""
        return DI.delete(cls, tag)
    
    @staticmethod
    def reset():
        """Reset the DI container, clearing all registered instances."""
        return DI.reset()

__all__ = [
    'FletX',
    '__version__'
]