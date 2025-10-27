"""
Page configuration decorators.

Provides helpers to declaratively configure navigation components on
``FletXPage`` subclasses.
"""

from typing import Any
from fletx.core.page import FletXPage


def page_config(**components: Any):
    """Configure navigation components for a ``FletXPage`` subclass.

    Supported keyword arguments match ``FletXPage.NAVIGATION_COMPONENT_KEYS``.
    Values can be Flet controls, callables returning controls, or classes that
    can be instantiated without arguments.
    """

    invalid = set(components.keys()) - FletXPage.NAVIGATION_COMPONENT_KEYS
    if invalid:
        formatted = ", ".join(sorted(invalid))
        raise ValueError(f"Unsupported page_config keys: {formatted}")

    def decorator(cls):
        if not issubclass(cls, FletXPage):
            raise TypeError(
                "page_config decorator can only be applied to FletXPage subclasses"
            )

        existing = dict(getattr(cls, "__navigation_config__", {}))
        existing.update(FletXPage._filter_navigation_config(components))
        setattr(cls, "__navigation_config__", existing)
        return cls

    return decorator
