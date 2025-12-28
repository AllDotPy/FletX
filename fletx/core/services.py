from abc import ABC
from typing import Any, Dict, Optional
from enum import Enum
from datetime import datetime

from fletx.core.state import (
    Reactive
)
from fletx.core.http import HTTPClient
from fletx.utils import get_logger


####
##      SERVICE STATE
#####
class ServiceState(Enum):
    """Possible state of a FleX Service"""

    IDLE = "idle"
    LOADING = "loading"
    READY = "ready"
    ERROR = "error"
    DISPOSED = "disposed"


####
##      FLETX SERVICE CLASS
#####
class FletXService(ABC):
    """
    Base Class for all FletX based Services.
    Offers a common structure with state, lifecycle management.
    """
    
    def __init__(
        self, 
        name: Optional[str] = None,
        auto_start: bool = True,
        http_client: Optional[HTTPClient] = None,
    ):
        """
        Initializes the FletX service
        
        Args:
            name: Name of the service (default: class name)
            auto_start: Automatically starts the service
            http_client: Instance of the FletX HTTPClient
            logger: Custom logger
        """

        self._name : str = name or self.__class__.__name__
        self._state: Reactive[ServiceState] = Reactive(ServiceState.IDLE)
        self._http_client: Optional[HTTPClient] = http_client
        self._logger = get_logger('FletX')
        self._error: Optional[Exception] = None
        self._disposed = False
        # self._listeners: Dict[str, list] = {
        #     'state_changed': [],
        #     'error': [],
        #     'ready': []
        # }
        
        # Service data
        self._data: Dict[str, Any] = {}
        
        # Metadata
        self._created_at: datetime = datetime.now()
        self._last_updated: Optional[datetime] = None

        # Setup state change listeners
        self.setup_state_listeners()
        
        if auto_start:
            self.start()

    @property
    def name(self) -> str:
        """Service name"""

        return self._name
    
    @property
    def state(self) -> ServiceState:
        """Current state of the service"""

        return self._state
    
    @property
    def is_ready(self) -> bool:
        """Check if service is ready"""

        return self._state == ServiceState.READY
    
    @property
    def is_loading(self) -> bool:
        """check if service is loading"""

        return self._state == ServiceState.LOADING
    
    @property
    def has_error(self) -> bool:
        """check if service has an error"""

        return self._state == ServiceState.ERROR
    
    @property
    def error(self) -> Optional[Exception]:
        """The last error of the service"""

        return self._error
    
    @property
    def http_client(self) -> HTTPClient:
        """Service http client instance"""

        return self._http_client
    
    @property
    def data(self) -> Dict[str, Any]:
        """Service data (read only)"""

        return self._data.copy()

    def set_error(self, error: Exception):
        """Set the service error"""

        if self._disposed:
            raise RuntimeError(f"Service {self._name} is disposed")
        
        self._error = error
        self._logger.error(f"Service error: {error}")
        self._change_state(ServiceState.ERROR)
    
    def set_data(self, key: str, value: Any):
        """Add a key value data to the service's data"""

        if self._disposed:
            raise RuntimeError(f"Service {self._name} is disposed")
        
        self._data[key] = value
        self._last_updated = datetime.now()
        self._logger.debug(f"Data updated: {key}")
    
    def get_data(self, key: str, default: Any = None) -> Any:
        """Get a given key value from service data"""

        return self._data.get(key, default)
    
    def clear_data(self):
        """Clear all service data"""

        self._data.clear()
        self._last_updated = datetime.now()
    
    def setup_state_listeners(self):
        """Setup a service state changes listeners"""

        self._state.listen(
            self.on_state_changed,
            auto_dispose = False
        )

    def start(self):
        """Starts the service"""

        # Service is disposed ?
        if self._disposed:
            raise RuntimeError(
                f"Cannot start disposed service {self._name}"
            )
        
        if self._state != ServiceState.IDLE:
            self._logger.warning(
                f"Service already started (current state: {self._state.value})"
            )
            return
        
        try:
            self._change_state(ServiceState.LOADING)
            self._logger.info(f"Starting service...")
            
            self.on_start()
            
            self._change_state(ServiceState.READY)
            self._logger.info(f"Service started successfully")
            
        except Exception as e:
            self._logger.error(f"Failed to start service: {e}")
            self._change_state(ServiceState.ERROR, e)
            raise

    async def start_async(self):
        """Async version of start method"""

        if self._disposed:
            raise RuntimeError(
                f"Cannot start disposed service {self._name}"
            )
        
        if self._state != ServiceState.IDLE:
            self._logger.warning(
                f"Service already started (current state: {self._state.value})"
            )
            return
        
        try:
            self._change_state(ServiceState.LOADING)
            self._logger.info(f"Starting service (async)...")
            
            await self.on_start_async()
            
            self._change_state(ServiceState.READY)
            self._logger.info(f"Service started successfully (async)")
            
        except Exception as e:
            self._logger.error(f"Failed to start service (async): {e}")
            self._change_state(ServiceState.ERROR, e)
            raise

    def restart(self):
        """Restart the service"""

        self._logger.info("Restarting service...")
        self.stop()
        self.start()
    
    async def restart_async(self):
        """Async version of restart method"""

        self._logger.info("Restarting service (async)...")
        await self.stop_async()
        await self.start_async()
    
    def stop(self):
        """Stop the service"""

        if self._state == ServiceState.IDLE:
            return
        
        try:
            self._logger.info("Stopping service...")

            # Call on_stop hook
            self.on_stop()

            # Change service state
            self._change_state(ServiceState.IDLE)
            self._logger.info("Service stopped")

        except Exception as e:
            self._logger.error(f"Error while stopping service: {e}")
    
    async def stop_async(self):
        """Async version of stop method"""

        if self._state == ServiceState.IDLE:
            return
        
        try:
            self._logger.info("Stopping service (async)...")

            # call on_stop hook
            await self.on_stop_async()

            self._change_state(ServiceState.IDLE)
            self._logger.info("Service stopped (async)")

        except Exception as e:
            self._logger.error(f"Error while stopping service (async): {e}")

    def dispose(self):
        """Dispose the service"""

        if self._disposed:
            return 
        
        try:
            self._logger.info("Disposing service...")
            self.stop()
            self.on_dispose()
            
            # Dispose state change listeners
            self._state.dispose()
            self._data.clear()
            
            self._disposed = True
            self._change_state(ServiceState.DISPOSED)
            self._logger.info("Service disposed")
            
        except Exception as e:
            self._logger.error(f"Error while disposing service: {e}")

    def _change_state(self,state: ServiceState):
        """Changes the service state"""

        self._state.value = state
        self._last_updated = datetime.now()

    def on_start(self):
        """Hook called when service starts"""

        pass

    async def on_start_async(self):
        """Async version of on_start hook (optional)"""

        self.on_start()

    def on_stop(self):
        """Hook called when a service is about to stop (optional)"""

        pass
    
    async def on_stop_async(self):
        """Async version of on_stop hook (optional)"""

        self.on_stop()


    def on_ready(self):
        """Hook called when the service is ready"""

        pass

    def on_state_changed(self, state: ServiceState):
        """Hook called when the service state changes"""

        pass

    def on_error(self):
        """Hook called when the service has an error"""

        pass

    def on_dispose(self):
        """Hook called when a service is disposing (optional)"""

        pass

    def __str__(self) -> str:
        return f"FletXService(name={self._name}, state={self._state.value})"
    
    def __repr__(self) -> str:
        return (f"FletXService(name='{self._name}', state={self._state.value}, "
                f"created_at={self._created_at.isoformat()})")
