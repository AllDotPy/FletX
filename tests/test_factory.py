import os
import sys
import types
import importlib.util


def _load_factory_and_deps():
    # Stub minimal 'fletx.utils.context' and 'flet'
    if "fletx" not in sys.modules:
        sys.modules["fletx"] = types.ModuleType("fletx")

    # Stub flet
    flet_mod = types.ModuleType("flet")

    class Control:
        pass

    class Page:
        def __init__(self):
            self._registered_controls = {}

        def register_control(self, name, widget_class):
            self._registered_controls[name] = widget_class

    flet_mod.Control = Control
    flet_mod.Page = Page

    # Stub fletx.utils.context
    context_mod = types.ModuleType("fletx.utils.context")

    class AppContext:
        _data = {}

        @classmethod
        def get_data(cls, key):
            return cls._data.get(key)

        @classmethod
        def set_data(cls, key, value):
            cls._data[key] = value

    context_mod.AppContext = AppContext

    sys.modules["flet"] = flet_mod
    sys.modules["fletx.utils.context"] = context_mod

    # Load fletx/core/factory.py directly
    factory_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "fletx", "core", "factory.py"
    )
    spec = importlib.util.spec_from_file_location(
        "fletx_core_factory_standalone", factory_path
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.FletXWidgetRegistry


FletXWidgetRegistry = _load_factory_and_deps()
# Now import the stubbed flet so we can use it in tests
import flet


def test_widget_registration_success():
    # Reset the registry
    FletXWidgetRegistry._widgets.clear()
    FletXWidgetRegistry._registered = False

    # Create a mock widget class with required methods
    class MockWidget(flet.Control):
        def _get_control_name(self):
            return "MockWidget"

        def build(self):
            pass

        def did_mount(self):
            pass

        def will_unmount(self):
            pass

        def bind(self):
            pass

    # Register the widget
    registered_cls = FletXWidgetRegistry.register(MockWidget)
    assert registered_cls is MockWidget
    assert "MockWidget" in FletXWidgetRegistry._widgets
    assert FletXWidgetRegistry._widgets["MockWidget"] is MockWidget


def test_widget_registration_duplicate():
    FletXWidgetRegistry._widgets.clear()
    FletXWidgetRegistry._registered = False

    class MockWidget(flet.Control):
        def _get_control_name(self):
            return "MockWidget"

        def build(self):
            pass

        def did_mount(self):
            pass

        def will_unmount(self):
            pass

        def bind(self):
            pass

    FletXWidgetRegistry.register(MockWidget)
    try:
        FletXWidgetRegistry.register(MockWidget)
        assert False, "Expected ValueError"
    except ValueError as e:
        assert "already registered" in str(e)


def test_widget_registration_missing_methods():
    FletXWidgetRegistry._widgets.clear()
    FletXWidgetRegistry._registered = False

    # Missing _get_control_name
    class MockWidget1(flet.Control):
        def build(self):
            pass

        def did_mount(self):
            pass

        def will_unmount(self):
            pass

        def bind(self):
            pass

    try:
        FletXWidgetRegistry.register(MockWidget1)
        assert False, "Expected AttributeError"
    except AttributeError as e:
        assert "_get_control_name" in str(e)

    # Missing build
    class MockWidget2(flet.Control):
        def _get_control_name(self):
            return "MockWidget2"

        def did_mount(self):
            pass

        def will_unmount(self):
            pass

        def bind(self):
            pass

    try:
        FletXWidgetRegistry.register(MockWidget2)
        assert False, "Expected AttributeError"
    except AttributeError as e:
        assert "build" in str(e)

    # Missing did_mount
    class MockWidget3(flet.Control):
        def _get_control_name(self):
            return "MockWidget3"

        def build(self):
            pass

        def will_unmount(self):
            pass

        def bind(self):
            pass

    try:
        FletXWidgetRegistry.register(MockWidget3)
        assert False, "Expected AttributeError"
    except AttributeError as e:
        assert "did_mount" in str(e)

    # Missing will_unmount
    class MockWidget4(flet.Control):
        def _get_control_name(self):
            return "MockWidget4"

        def build(self):
            pass

        def did_mount(self):
            pass

        def bind(self):
            pass

    try:
        FletXWidgetRegistry.register(MockWidget4)
        assert False, "Expected AttributeError"
    except AttributeError as e:
        assert "will_unmount" in str(e)

    # Missing bind
    class MockWidget5(flet.Control):
        def _get_control_name(self):
            return "MockWidget5"

        def build(self):
            pass

        def did_mount(self):
            pass

        def will_unmount(self):
            pass

    try:
        FletXWidgetRegistry.register(MockWidget5)
        assert False, "Expected AttributeError"
    except AttributeError as e:
        assert "bind" in str(e)


def test_widget_registration_after_page_registered():
    FletXWidgetRegistry._widgets.clear()
    FletXWidgetRegistry._registered = (
        True  # Simulate that the page is already registered
    )

    class MockWidget(flet.Control):
        def _get_control_name(self):
            return "MockWidget"

        def build(self):
            pass

        def did_mount(self):
            pass

        def will_unmount(self):
            pass

        def bind(self):
            pass

    try:
        FletXWidgetRegistry.register(MockWidget)
        assert False, "Expected RuntimeError"
    except RuntimeError as e:
        assert "after the page is registered" in str(e)


def test_register_all():
    FletXWidgetRegistry._widgets.clear()
    FletXWidgetRegistry._registered = False

    # Create a mock page
    page = flet.Page()  # Using the stubbed Page

    # Create a mock widget class
    class MockWidget(flet.Control):
        def _get_control_name(self):
            return "MockWidget"

        def build(self):
            pass

        def did_mount(self):
            pass

        def will_unmount(self):
            pass

        def bind(self):
            pass

    # Register the widget
    FletXWidgetRegistry.register(MockWidget)

    # Call register_all
    FletXWidgetRegistry.register_all(page)

    # Check that the widget was registered with the page
    assert hasattr(page, "_registered_controls")
    assert "MockWidget" in page._registered_controls
    assert page._registered_controls["MockWidget"] is MockWidget
    # Check that the registry is marked as registered
    assert FletXWidgetRegistry._registered is True

    # Call register_all again (should do nothing)
    FletXWidgetRegistry.register_all(page)
    # The registered controls should still be the same (no duplicate)
    assert len(page._registered_controls) == 1


if __name__ == "__main__":
    test_widget_registration_success()
    test_widget_registration_duplicate()
    test_widget_registration_missing_methods()
    test_widget_registration_after_page_registered()
    test_register_all()
    print("All factory tests passed!")
