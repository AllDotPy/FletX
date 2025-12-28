import flet as ft
from fletx.core import (
    FletXPage
)
from fletx.navigation import go_back

class NotFoundPage(FletXPage):
    """Default 404 template"""

    def __init__(self):
        super().__init__()
    
    def build(self):
        return ft.Column(
            spacing = 10,
            expand = True,
            alignment = ft.MainAxisAlignment.CENTER,
            horizontal_alignment = ft.CrossAxisAlignment.CENTER,
            controls = [
                ft.Container(
                    expand = True
                ),
                ft.Row(
                    spacing = 0,
                    alignment = ft.MainAxisAlignment.CENTER,
                    controls = [
                        ft.Text(
                            value = f'4',
                            size = 100, 
                            weight = ft.FontWeight.BOLD
                        ),
                        # LOGO USED AS 0
                        ft.Image(
                            src = 'logo.png',
                            fit = ft.ImageFit.CONTAIN,
                            width = 120,
                            height = 120
                        ),
                        ft.Text(
                            value = f'4',
                            size = 100, 
                            weight = ft.FontWeight.BOLD
                        ),
                    ]
                ),

                ft.Text(
                    'PAGE NOT FOUND',
                    size = 30,
                ),
                ft.Text(
                    'The page you were looking for could not be found.',
                    size = 14,
                    text_align = ft.TextAlign.CENTER
                ),

                ft.Container(       # SPACER
                    height = 20
                ),

                # GOBACK BUTTON
                ft.ElevatedButton(
                    "Go back",
                    icon = ft.Icons.ARROW_BACK_IOS,
                    on_click=lambda e: go_back()
                ),

                ft.Container(       # SPACER
                    expand = True
                ),

                ft.Text('🚀 powered by FletX 0.1.4.b1',color = ft.Colors.GREY_600),
                ft.Text('Python version 3.12', color = ft.Colors.GREY_600),
                
                ft.Container(       # SPACER
                    height = 50,
                ),
            ]
        )