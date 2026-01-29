"""
FletX main entry point
"""

import inspect
import atexit
import flet as ft
from typing import (
    Dict, Optional, Callable, Any, Union, List
)

from fletx.core.routing.models import NavigationMode
from fletx.core.routing.router import FletXRouter
# from fletx.core.factory import FletXWidgetRegistry
from fletx.utils.logger import SharedLogger
from fletx.utils.context import AppContext
from fletx.utils import run_async  # noqa: F401
from fletx.core.concurency.event_loop import EventLoopManager


####
##      FLETX APPLICATION
#####
class FletXApp:
    """FletX Application class with async/sync support"""
    
    def __init__(
        self, 
        initial_route: str = "/",
        navigation_mode: NavigationMode = NavigationMode.VIEWS,
        theme_mode: ft.ThemeMode = ft.ThemeMode.SYSTEM,
        debug: bool = False,
        title: str = "FletX App",
        theme: Optional[ft.Theme] = None,
        dark_theme: Optional[ft.Theme] = None,
        window_config: Optional[Dict[str, Any]] = None,
        on_startup: Optional[Union[Callable, List[Callable]]] = None,
        on_shutdown: Optional[Union[Callable, List[Callable]]] = None,
        on_system_exit: Optional[Union[Callable, List[Callable]]] = None,
        **kwargs
    ):
        """
        Initialize the FletX application with enhanced configuration
        
        Args:
            initial_route: Initial route path
            navigation_mode: router navigation mode (NATIVE, HYBRID, VIEWS)
            theme_mode: Theme mode (SYSTEM, LIGHT, DARK)
            debug: Enable debug mode
            title: Application title
            theme: Light theme configuration
            dark_theme: Dark theme configuration
            window_config: Window configuration dict
            on_startup: Startup hook(s)
            on_shutdown: Shutdown hook(s)
            **kwargs: Additional arguments for ft.app()
        """

        self.initial_route = initial_route
        self.navigation_mode = navigation_mode
        self.theme_mode = theme_mode
        self.debug = debug
        self.title = title
        self.theme = theme
        self.dark_theme = dark_theme
        self.window_config = window_config or {}
        self.flet_kwargs = kwargs

        # Normalize hooks to lists
        self.on_startup = self._normalize_hooks(on_startup)
        self.on_shutdown = self._normalize_hooks(on_shutdown)
        self.on_system_exit = self._normalize_hooks(on_system_exit)

        # Internal state
        self._is_initialized = False
        self._page: ft.Page = None

        # Initialize event loop manager
        self._loop_manager = EventLoopManager()

        # Initialization of the shared logger
        SharedLogger._initialize_logger(
            name = 'FletX',
            debug = debug
        )
        self.logger = SharedLogger.get_logger(__name__)

    @property
    def is_initialized(self) -> bool:
        """Check if app is initialized"""

        return self._is_initialized
    
    @property
    def page(self) -> Optional[ft.Page]:
        """Get current page (if available)"""

        return self._page
        
    def _normalize_hooks(
        self, 
        hooks: Optional[Union[Callable, List[Callable]]]
    ) -> List[Callable]:
        """Normalize hooks to a list format"""

        if hooks is None:
            return []
        
        elif callable(hooks):
            return [hooks]
        
        elif isinstance(hooks, list):
            return hooks
        
        else:
            raise ValueError(
                "Hooks must be callable or list of callables"
            )
        
    def add_startup_hook(self, hook: Callable):
        """Add a startup hook"""

        self.on_startup.append(hook)
        return self
    
    def add_shutdown_hook(self, hook: Callable):
        """Add a shutdown hook"""

        self.on_shutdown.append(hook)
        return self
    
    def attach_on_shutdown_hooks(self):
        """Add on Shutdown hooks to the page close event."""

        self.page.on_close = lambda: self._loop_manager.run_until_complete(
            self._execute_hooks(self.on_shutdown, "shutdown")
        )
        atexit.register(self.handle_sysem_exit_signal)

    def handle_sysem_exit_signal(self):
        """handle system exit signals and call handlers"""

        # Just execute on_system_exit_hooks
        self._loop_manager.run_until_complete(
            self._execute_hooks(
                self.on_system_exit,
                'on_system_exit'
            )
        )
    
    def configure_window(self, **config):
        """Configure window properties"""

        self.window_config.update(config)
        return self
    
    def configure_theme(
        self, 
        theme: ft.Theme = None, 
        dark_theme: ft.Theme = None
    ):
        """Configure application themes"""

        # Light Theme
        if theme:
            self.theme = theme

        # Dark Theme
        if dark_theme:
            self.dark_theme = dark_theme
        return self
    
    async def _execute_hooks(
        self, 
        hooks: List[Callable], 
        context: str = ""
    ):
        """Execute hooks with async/sync support"""

        for hook in hooks:
            try:
                # Coroutine function
                if inspect.iscoroutinefunction(hook):
                    await hook(self._page)

                # Non coroutine function
                else:
                    hook(self._page)
                self.logger.debug(
                    f"Executed {context} hook: {hook.__name__}"
                )

            except Exception as e:
                self.logger.error(
                    f"Error in {context} hook {hook.__name__}: {e}"
                )

    def _configure_page(self, page: ft.Page):
        """Configure the Flet page"""

        # Basic configuration
        page.title = self.title
        page.theme_mode = self.theme_mode
        
        # Theme configuration
        if self.theme:
            page.theme = self.theme
        if self.dark_theme:
            page.dark_theme = self.dark_theme
            
        # Window configuration
        for key, value in self.window_config.items():
            if hasattr(page.window, key):
                setattr(page.window, key, value)
            else:
                self.logger.warning(f"Unknown window property: {key}")

    async def _async_main(self, page: ft.Page):
        """Async main entry point"""

        self._page = page
        
        try:
            # Configure page
            self._configure_page(page)
            
            # Execute startup hooks
            await self._execute_hooks(self.on_startup, "startup")
            
            # Register widgets (if needed)
            # FletXWidgetRegistry.register_all(page)
            
            # Initialize App Context
            AppContext.initialize(page, self.debug)
            AppContext.set_data("logger", self.logger)
            AppContext.set_data("app", self)
            AppContext.set_data("event_loop", self._loop_manager.loop)
            
            # Initialize Router
            FletXRouter.initialize(
                page, initial_route = self.initial_route
            ).set_navigation_mode(self.navigation_mode)
            
            self._is_initialized = True
            self.logger.info("FletX Application initialized successfully (async mode)")
            
        except Exception as e:
            self.logger.error(f"Error initializing FletX App: {e}")
            page.add(ft.Text(f"Initialization Error: {e}", color=ft.Colors.RED))

    def _sync_main(self, page: ft.Page):
        """Sync main entry point"""

        try:
            self._loop_manager.run_until_complete(
                self._async_main(page)
            )
            self.attach_on_shutdown_hooks()
        except Exception as e:
            self.logger.error(f'Error when trying to run App: {e}')

        # finally:
            # Execute shutdown hooks
            # if self.on_shutdown:
            #     self._loop_manager.run_until_complete(
            #         self._execute_hooks(self.on_shutdown, "shutdown")
            #     )
            # self._loop_manager.close_loop()

    def _main(self, page: ft.Page):
        """Main entry point (backward compatibility)"""

        self._sync_main(page)
    
    def create_main_handler(self) -> Callable:
        """Create a main handler for ft.app()"""

        return self._sync_main
    
    def create_async_main_handler(self) -> Callable:
        """Create an async main handler"""

        return self._async_main
        
    def run(self, **kwargs):
        """Run the application (sync mode)"""

        merged_kwargs = {**self.flet_kwargs, **kwargs}
        ft.app(target=self._sync_main, **merged_kwargs)

    def run_async(self, **kwargs):  # noqa: F811
        """Run the application (async mode)"""

        def async_wrapper(page):

            try:
                self._loop_manager.run_until_complete(self._async_main(page))
                self.attach_on_shutdown_hooks()
            except Exception as e:
                self.logger.error(f'Error when trying to run App: {e}')
            # finally:
            #     if self.on_shutdown:
            #         self._loop_manager.run_until_complete(
            #             self._execute_hooks(self.on_shutdown, "shutdown")
            #         )
                # self._loop_manager.close_loop()
        
        merged_kwargs = {**self.flet_kwargs, **kwargs}
        ft.app(target = async_wrapper, **merged_kwargs)

    def run_web(
        self, 
        host: str = "localhost", 
        port: int = 8000, **kwargs
    ):
        """Run as web application"""

        merged_kwargs = {**self.flet_kwargs, **kwargs}
        ft.app(
            target = self._sync_main, 
            view = ft.WEB_BROWSER, 
            host = host, 
            port = port, 
            **merged_kwargs
        )
    
    def run_desktop(self, **kwargs):
        """Run as desktop application"""

        merged_kwargs = {**self.flet_kwargs, **kwargs}
        ft.app(
            target = self._sync_main, 
            view = ft.FLET_APP, 
            **merged_kwargs
        )

    def get_context_data(
        self, 
        key: str, 
        default: Any = None
    ) -> Any:
        """Get data from app context"""

        return AppContext.get_data(key, default)
    
    def set_context_data(self, key: str, value: Any):
        """Set data in app context"""

        AppContext.set_data(key, value)
    
    # Fluent interface methods
    def with_title(self, title: str):
        """Set application title (fluent)"""

        self.title = title
        return self
    
    def with_theme(self, theme: ft.Theme):
        """Set light theme (fluent)"""

        self.theme = theme
        return self
    
    def with_dark_theme(self, dark_theme: ft.Theme):
        """Set dark theme (fluent)"""

        self.dark_theme = dark_theme
        return self
    
    def with_window_size(self, width: int, height: int):
        """Set window size (fluent)"""

        self.window_config.update({"width": width, "height": height})
        return self
    
    def with_debug(self, debug: bool = True):
        """Enable/disable debug mode (fluent)"""

        self.debug = debug
        return self
