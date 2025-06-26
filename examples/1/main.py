import asyncio
import flet as ft
from fletx.app import FletXApp
from routes import MyAppRouter

def main():

    # Lifecycle Hooks 
    async def on_startup(page: ft.Page):
        print("App is running!")
        page.padding = 0
    
    def on_shutdown(page: ft.Page):
        print("App is closed!")
    
    # Initialisation de l'application FletX
    app = FletXApp(
        initial_route = "/login",
        debug = True,
        theme_mode = ft.ThemeMode.DARK,
        theme = ft.Theme(
            color_scheme_seed = ft.Colors.GREEN
        ),
        dark_theme = ft.Theme(
            color_scheme_seed = ft.Colors.BLUE_800,
            scaffold_bgcolor = ft.Colors.BLACK,
            font_family = 'Bebas Neue, sans-serif',
        ),
        on_startup = on_startup,
        on_shutdown = on_shutdown,
    ).with_window_size(400,810)
    
    # Cette méthode initialise le router avec la page Flet
    # app._main(page) 

    app.run_async()

if __name__ == "__main__":
    main()
    # ft.app(target=main)