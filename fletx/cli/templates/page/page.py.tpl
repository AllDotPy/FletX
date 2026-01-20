"""
{{ name | pascal_case }} Controller.

This Page class is generated from a template.
"""

from flet import *
from fletx.core import FletXPage

# Import your modules here...


class {{ name | pascal_case }}Page(FletXPage):
    """{{ name | pascal_case }} Page"""

    def __init__(self):
        super().__init__(
            padding = 10,
            bgcolor = Theme.scaffold_bgcolor
        )

        # ...

    def on_init(self):
        """Hook called when {{ name | pascal_case }}Page is initialized"""

        print("{{ name | pascal_case }}Page is initialized")

    def on_destroy(self):
        """Hook called when {{ name | pascal_case }}Page will be unmounted."""

        print("{{ name | pascal_case }}Page is destroyed")

    def build(self)-> Control:
        """Method that build {{ name | pascal_case }}Page content"""

        return SafeArea(
            expand = True,
            minimum_padding = 0,
            maintain_bottom_view_padding = False,
            content = Column(
                expand = True,
                alignment = MainAxisAlignment.CENTER,
                horizontal_alignment = CrossAxisAlignment.CENTER,
                controls = [
                    Text("{{ name | pascal_case }}Page works!", size=24),
                ]
            )
        )