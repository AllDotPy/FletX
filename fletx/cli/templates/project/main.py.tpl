"""
{{ project_name | pascal_case }} App
{{ description }}

A FletX application.
Author: {{ author }}
Version: {{ version }}
"""

import flet as ft
from fletx.app import FletXApp
from app.routes import {{ project_name | pascal_case }}Router
from app.utils.theme import light_theme, dark_theme

def main():
    """Main entry point for the {{ project_name | pascal_case }} application."""

    # Lifecycle Hooks 
    async def on_startup(page: ft.Page):
        print("App is running!")
    
    def on_shutdown(page: ft.Page):
        print("App is closed!")
    
    # App Configuration
    app = FletXApp(
        title = "{{ project_name | pascal_case }}",
        initial_route = "/",
        debug = True,
        theme = light_theme,
        dark_theme = dark_theme,
        theme_mode= ft.ThemeMode.SYSTEM,
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
    app.run_async()     # you can use also `app.run()` method. see documetation for more

if __name__ == "__main__":
    main()