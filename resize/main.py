"""
Resize App
None

A FletX application.
Author: einswilli
Version: 0.1.0
"""

import flet as ft
from fletx.app import FletXApp
from app.routes import ResizeRouter

def main():
    """Main entry point for the Resize application."""

    # Lifecycle Hooks 
    async def on_startup(page: ft.Page):
        print("App is running!")
    
    def on_shutdown(page: ft.Page):
        print("App is closed!")
    
    # App Configuration
    app = FletXApp(
        title="Resize",
        initial_route = "/",
        debug = True,
        theme = ft.Theme(color_scheme_seed = ft.Colors.GREEN),
        dark_theme = ft.Theme(
            color_scheme_seed = ft.Colors.BLUE_800,
            scaffold_bgcolor = ft.Colors.BLACK
        ),
        window_config = {
            "width": 400,
            "height": 810,
            "resizable": True,
            "maximizable": True
        },
        on_startup = on_startup,
        on_shutdown = on_shutdown
    )

    # Run App
    app.run()     # you can use also `app.run()` method. see documetation for more

if __name__ == "__main__":
    main()