import pytest
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from fletx.core.page import FletXPage, PageState
from fletx.core.controller import FletXController
from fletx.core.routing.models import RouteInfo
from fletx.decorators.page import page_config
import flet as ft


# Concrete implementation for testing
class SamplePage(FletXPage):
    """Concrete implementation of FletXPage for testing."""
    
    def build(self):
        return ft.Text("Test Page Content")


@page_config(app_bar=lambda page: ft.AppBar(title=ft.Text("Decorated")))
class DecoratedPage(SamplePage):
    """Sample page with declarative navigation config for testing."""
    pass


class SampleController(FletXController):
    """Test controller for testing."""
    pass


@pytest.fixture
def mock_dependencies():
    """Mock all external dependencies."""
    with patch('fletx.core.page.get_page') as mock_get_page, \
         patch('fletx.core.page.get_logger') as mock_get_logger, \
         patch('fletx.core.page.DI') as mock_di, \
         patch('fletx.core.page.EffectManager') as mock_effect_manager:
        
        # Setup mock page
        mock_page = Mock()
        mock_page.width = 800
        mock_page.views = [Mock()]
        mock_page.update = Mock()
        mock_get_page.return_value = mock_page
        
        # Setup mock logger
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        # Setup mock DI
        mock_di.put = Mock()
        mock_di.find = Mock(return_value=None)
        mock_di.delete = Mock()
        
        # Setup mock effect manager
        mock_effects = Mock()
        mock_effects.runEffects = Mock()
        mock_effects.dispose = Mock()
        mock_effect_manager.return_value = mock_effects
        
        yield {
            'page': mock_page,
            'logger': mock_logger,
            'di': mock_di,
            'effects': mock_effects
        }


def test_fletxpage_initialization_defaults(mock_dependencies):
    """Test FletXPage initialization with default values."""
    page = SamplePage()
    
    assert page.state == PageState.INITIALIZING
    assert page._auto_dispose_controllers
    assert page._enable_keyboard_shortcuts
    assert page._enable_gestures
    assert page._safe_area
    assert page.route_info is None
    assert len(page._controllers) == 0
    assert page._mount_time is None
    assert page._update_count == 0


def test_fletxpage_initialization_custom(mock_dependencies):
    """Test FletXPage initialization with custom values."""
    page = SamplePage(
        padding=20,
        bgcolor="blue",
        auto_dispose_controllers=False,
        enable_keyboard_shortcuts=False,
        enable_gestures=False,
        safe_area=False
    )
    
    assert not page._auto_dispose_controllers
    assert not page._enable_keyboard_shortcuts
    assert not page._enable_gestures
    assert not page._safe_area
    assert page.padding == 20
    assert page.bgcolor == "blue"


def test_fletxpage_state_property(mock_dependencies):
    """Test FletXPage state property."""
    page = SamplePage()
    
    assert page.state == PageState.INITIALIZING
    
    page._state = PageState.MOUNTED
    assert page.state == PageState.MOUNTED


def test_fletxpage_is_mounted_property(mock_dependencies):
    """Test FletXPage is_mounted property."""
    page = SamplePage()
    
    assert not page.is_mounted
    
    page._state = PageState.MOUNTED
    assert page.is_mounted
    
    page._state = PageState.ACTIVE
    assert page.is_mounted
    
    page._state = PageState.DISPOSED
    assert not page.is_mounted


def test_fletxpage_is_active_property(mock_dependencies):
    """Test FletXPage is_active property."""
    page = SamplePage()
    
    assert not page.is_active
    
    page._state = PageState.ACTIVE
    assert page.is_active
    
    page._state = PageState.INACTIVE
    assert not page.is_active


def test_fletxpage_refresh(mock_dependencies):
    """Test FletXPage refresh method."""
    page = SamplePage()
    initial_count = page._update_count
    
    page.refresh()
    
    assert page._update_count == initial_count + 1
    assert page._last_update_time is not None
    assert mock_dependencies['page'].update.called


def test_fletxpage_set_title(mock_dependencies):
    """Test FletXPage set_title method."""
    mock_dependencies['page'].title = ""
    page = SamplePage()
    
    page.set_title("New Title")
    
    assert mock_dependencies['page'].title == "New Title"
    assert mock_dependencies['page'].update.called


def test_fletxpage_set_theme_mode(mock_dependencies):
    """Test FletXPage set_theme_mode method."""
    mock_dependencies['page'].theme_mode = ft.ThemeMode.SYSTEM
    page = SamplePage()
    
    page.set_theme_mode(ft.ThemeMode.DARK)
    
    assert mock_dependencies['page'].theme_mode == ft.ThemeMode.DARK
    assert mock_dependencies['page'].update.called


def test_fletxpage_keyboard_shortcuts(mock_dependencies):
    """Test FletXPage keyboard shortcut management."""
    page = SamplePage()
    shortcut_callback = Mock()
    
    # Test add_keyboard_shortcut
    page.add_keyboard_shortcut("ctrl+s", shortcut_callback, "Save")
    assert "ctrl+s" in page._keyboard_shortcuts
    assert page._keyboard_shortcuts["ctrl+s"]["callback"] == shortcut_callback
    
    # Test remove_keyboard_shortcut
    removed = page.remove_keyboard_shortcut("ctrl+s")
    assert removed
    assert "ctrl+s" not in page._keyboard_shortcuts


def test_page_config_applies_navigation(mock_dependencies):
    """Ensure page_config decorator populates navigation components."""
    page = DecoratedPage()
    page.route_info = RouteInfo(path="/decorated")

    page._build_page()

    appbar = mock_dependencies['page'].views[-1].appbar
    assert isinstance(appbar, ft.AppBar)
    assert isinstance(appbar.title, ft.Text)
    assert appbar.title.value == "Decorated"


def test_route_navigation_overrides_class_config(mock_dependencies):
    """Route-level config should override decorator defaults."""
    page = DecoratedPage()
    page.route_info = RouteInfo(path="/decorated")
    page.set_route_navigation_config({
        'app_bar': lambda page, info: ft.AppBar(
            title=ft.Text(f"Route {info.path if info else ''}")
        )
    })

    page._build_page()

    appbar = mock_dependencies['page'].views[-1].appbar
    assert isinstance(appbar, ft.AppBar)
    assert appbar.title.value == "Route /decorated"

