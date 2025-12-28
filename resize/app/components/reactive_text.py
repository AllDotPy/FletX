import flet as ft
from fletx.core import (
    RxStr
)
from fletx.decorators import (
    simple_reactive
)

@simple_reactive(
    bindings={
        'value': 'text'
    }
)
class MyReactiveText(ft.Text):
    """My Reactive Text Widget"""
    def __init__(self, rx_text: RxStr, **kwargs):
        self.text: RxStr = rx_text
        super().__init__(**kwargs)