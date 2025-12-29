import logging
from pathlib import Path
from types import ModuleType
import flet
import asyncio
from typing import Callable, Awaitable, Any, Union
from importlib import import_module

from fletx.utils.context import AppContext
from fletx.utils.logger import SharedLogger

# FletX Logger Utility
def get_logger(name: str) -> logging.Logger:
    """Gets a logger from the global context"""

    base_logger = AppContext.get_data("logger")
    if base_logger is None:

        # Fallback if the context is not initialized
        SharedLogger._initialize_logger(
            name = 'FletX',
        )
        
        logger = SharedLogger.get_logger(__name__) 
        return logger
    return base_logger.getChild(name)


# FletXApp Context Page Getter
def get_page() -> flet.Page: 
    """Gets the current FletX page from the global context"""
    
    page = AppContext.get_page()
    if page is None:
        raise RuntimeError(
            "FletX application context is not initialized."
            " Ensure AppContext.initialize() is called before accessing the page."
        )
    return page

# IMPORT MODULE
def import_module_from(path: Union[str,Path]) ->'ModuleType':
    """Import module using importlib"""
    
    return import_module(path)

# GET EVENT LOOP
def get_event_loop() -> asyncio.AbstractEventLoop:
    """
    Returns the currently running asyncio event loop.
    If no event loop is running, creates a new one and sets it as the current loop.

    Returns:
        An instance of asyncio.AbstractEventLoop
    """
    return AppContext.get_data('event_loop')

# RUN ASYNC
def run_async(callback: Callable[[], Awaitable[Any]]) -> Any:
    """
    Executes an async callback using asyncio.
    - If an event loop is already running, schedules the coroutine.
    - If not, starts a new event loop and runs the coroutine.

    Args:
        callback: An async function (coroutine) to execute.

    Returns:
        The result of the coroutine, or a task if within a running loop.
    """
    
    # If we're inside an existing running loop 
    loop = get_event_loop()

    if loop.is_running():
        task = loop.create_task(callback())

        # Optional: Add callback to handle task completion
        def handle_task_done(fut):
            try:
                fut.result()
            except Exception as e:
                get_logger('FletX.utils.run_async').error(f"task failed: {e}")
        
        task.add_done_callback(handle_task_done)

    # If loop isn't running, run it until complete
    else: 
        loop.run_until_complete(callback())
    
# UI FRIENDLY SLEEP
async def ui_friendly_sleep(duration_ms: int, page: flet.Page):
    """Sleep that allows UI updates to process"""
    if duration_ms <= 0:
        return
    
    # Split into smaller chunks to keep UI responsive
    chunk_size = 16  # ~60fps
    remaining = duration_ms
    
    while remaining > 0:
        current_chunk = min(chunk_size, remaining)
        await asyncio.sleep(current_chunk / 1000)
        page.update()  # Allow UI updates between chunks
        remaining -= current_chunk