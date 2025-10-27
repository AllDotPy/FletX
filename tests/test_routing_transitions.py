"""
Unit tests for FletX Route Transitions
"""

import pytest
import flet as ft
from unittest.mock import Mock, AsyncMock, patch
from math import pi

from fletx.core.routing.transitions import (
    RouteTransition,
    TransitionType,
    TransitionDirection,
    EasingFunction,
    create_slide_transition,
    create_fade_transition,
    create_zoom_transition,
    create_slide_fade_transition,
    create_fade_through_transition,
    create_scale_fade_transition
)


class MockPage(Mock):
    """Mock Flet Page for testing."""
    
    def __init__(self):
        super().__init__(spec=ft.Page)
        self.controls = []
        self.views = []
    
    def update(self):
        pass
    
    def clean(self):
        self.controls = []
    
    def add(self, *controls):
        self.controls.extend(controls)


class TestTransitionEnums:
    """Test transition enum classes."""

    def test_transition_type_values(self):
        """Test TransitionType enum values."""
        assert TransitionType.NONE.value == "none"
        assert TransitionType.FADE.value == "fade"
        assert TransitionType.SLIDE_LEFT.value == "slide_left"
        assert TransitionType.ZOOM_IN.value == "zoom_in"
        assert TransitionType.CUSTOM.value == "custom"

    def test_transition_direction_values(self):
        """Test TransitionDirection enum values."""
        assert TransitionDirection.LEFT.value == "left"
        assert TransitionDirection.RIGHT.value == "right"
        assert TransitionDirection.UP.value == "up"
        assert TransitionDirection.DOWN.value == "down"

    def test_easing_function_values(self):
        """Test EasingFunction enum values."""
        assert EasingFunction.LINEAR.value == "linear"
        assert EasingFunction.EASE_IN.value == "easeIn"
        assert EasingFunction.EASE_OUT.value == "easeOut"
        assert EasingFunction.BOUNCE_IN.value == "bounceIn"


class TestRouteTransitionInitialization:
    """Test RouteTransition initialization."""

    def test_creation_with_defaults(self):
        """Test basic creation with defaults."""
        transition = RouteTransition()
        
        assert transition.type == TransitionType.FADE
        assert transition.duration == 300
        assert transition.easing == EasingFunction.EASE_IN_OUT
        assert transition.direction is None
        assert transition.reverse_on_back is True

    def test_creation_with_all_params(self):
        """Test creation with all parameters."""
        custom_fn = Mock()
        transition = RouteTransition(
            transition_type=TransitionType.SLIDE_LEFT,
            duration=500,
            easing=EasingFunction.BOUNCE_OUT,
            direction=TransitionDirection.LEFT,
            custom_transition=custom_fn,
            reverse_on_back=False
        )
        
        assert transition.type == TransitionType.SLIDE_LEFT
        assert transition.duration == 500
        assert transition.easing == EasingFunction.BOUNCE_OUT
        assert transition.direction == TransitionDirection.LEFT
        assert transition.custom == custom_fn
        assert transition.reverse_on_back is False

    def test_animation_curve_conversion(self):
        """Test easing function to animation curve conversion."""
        transition = RouteTransition(easing=EasingFunction.EASE_IN)
        
        curve = transition._get_animation_curve()
        assert curve == "easeIn"

    def test_animation_creation(self):
        """Test animation object creation."""
        transition = RouteTransition(duration=400)
        animation = transition._create_animation()
        
        assert isinstance(animation, ft.Animation)
        assert animation.duration == 400


class TestTransitionReversal:
    """Test transition reversal for back navigation."""

    def test_reverse_slide_left(self):
        """Test SLIDE_LEFT reverses to SLIDE_RIGHT."""
        transition = RouteTransition(TransitionType.SLIDE_LEFT)
        
        actual = transition._get_actual_transition_type(is_back_navigation=True)
        assert actual == TransitionType.SLIDE_RIGHT

    def test_reverse_zoom_in(self):
        """Test ZOOM_IN reverses to ZOOM_OUT."""
        transition = RouteTransition(TransitionType.ZOOM_IN)
        
        actual = transition._get_actual_transition_type(is_back_navigation=True)
        assert actual == TransitionType.ZOOM_OUT

    def test_no_reverse_when_disabled(self):
        """Test no reversal when reverse_on_back is False."""
        transition = RouteTransition(
            TransitionType.SLIDE_LEFT,
            reverse_on_back=False
        )
        
        actual = transition._get_actual_transition_type(is_back_navigation=True)
        assert actual == TransitionType.SLIDE_LEFT

    def test_no_reverse_on_forward_nav(self):
        """Test no reversal on forward navigation."""
        transition = RouteTransition(TransitionType.SLIDE_LEFT)
        
        actual = transition._get_actual_transition_type(is_back_navigation=False)
        assert actual == TransitionType.SLIDE_LEFT


class TestBasicTransitions:
    """Test basic transition applications."""

    def setup_method(self):
        """Set up test fixtures."""
        self.page = MockPage()
        self.new_controls = [ft.Text("New Content")]
        self.old_controls = [ft.Text("Old Content")]

    @pytest.mark.asyncio
    async def test_none_transition(self):
        """Test NONE transition returns controls unchanged."""
        transition = RouteTransition(TransitionType.NONE)
        
        result = await transition.apply(self.page, self.new_controls)
        
        assert result == self.new_controls

    @pytest.mark.asyncio
    async def test_fade_transition(self):
        """Test FADE transition."""
        transition = RouteTransition(TransitionType.FADE, duration=100)
        
        result = await transition.apply(
            self.page, 
            self.new_controls,
            self.old_controls
        )
        
        assert result == self.new_controls
        assert len(self.page.controls) == 1

    @pytest.mark.asyncio
    async def test_slide_left_transition(self):
        """Test SLIDE_LEFT transition."""
        transition = RouteTransition(TransitionType.SLIDE_LEFT, duration=100)
        
        result = await transition.apply(
            self.page,
            self.new_controls,
            self.old_controls
        )
        
        assert result == self.new_controls

    @pytest.mark.asyncio
    async def test_zoom_in_transition(self):
        """Test ZOOM_IN transition."""
        transition = RouteTransition(TransitionType.ZOOM_IN, duration=100)
        
        result = await transition.apply(
            self.page,
            self.new_controls,
            self.old_controls
        )
        
        assert result == self.new_controls


class TestCompositeTransitions:
    """Test composite transitions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.page = MockPage()
        self.new_controls = [ft.Text("New")]
        self.old_controls = [ft.Text("Old")]

    @pytest.mark.asyncio
    async def test_slide_fade_transition(self):
        """Test SLIDE_FADE composite transition."""
        transition = RouteTransition(TransitionType.SLIDE_FADE_LEFT, duration=100)
        
        result = await transition.apply(
            self.page,
            self.new_controls,
            self.old_controls
        )
        
        assert result == self.new_controls

    @pytest.mark.asyncio
    async def test_fade_through_transition(self):
        """Test FADE_THROUGH transition."""
        transition = RouteTransition(TransitionType.FADE_THROUGH, duration=100)
        
        result = await transition.apply(
            self.page,
            self.new_controls,
            self.old_controls
        )
        
        assert result == self.new_controls

    @pytest.mark.asyncio
    async def test_scale_fade_transition(self):
        """Test SCALE_FADE transition."""
        transition = RouteTransition(TransitionType.SCALE_FADE, duration=100)
        
        result = await transition.apply(
            self.page,
            self.new_controls,
            self.old_controls
        )
        
        assert result == self.new_controls


class TestAdvancedTransitions:
    """Test advanced transition types."""

    def setup_method(self):
        """Set up test fixtures."""
        self.page = MockPage()
        self.new_controls = [ft.Text("New")]
        self.old_controls = [ft.Text("Old")]

    @pytest.mark.asyncio
    async def test_flip_horizontal_transition(self):
        """Test FLIP_HORIZONTAL transition."""
        transition = RouteTransition(TransitionType.FLIP_HORIZONTAL, duration=100)
        
        result = await transition.apply(
            self.page,
            self.new_controls,
            self.old_controls
        )
        
        assert result == self.new_controls

    @pytest.mark.asyncio
    async def test_rotate_transition(self):
        """Test ROTATE transition."""
        transition = RouteTransition(TransitionType.ROTATE, duration=100)
        
        result = await transition.apply(
            self.page,
            self.new_controls,
            self.old_controls
        )
        
        assert result == self.new_controls

    @pytest.mark.asyncio
    async def test_scale_transition(self):
        """Test SCALE transition."""
        transition = RouteTransition(TransitionType.SCALE, duration=100)
        
        result = await transition.apply(
            self.page,
            self.new_controls,
            self.old_controls
        )
        
        assert result == self.new_controls


class TestCustomTransition:
    """Test custom transition functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.page = MockPage()
        self.new_controls = [ft.Text("New")]
        self.old_controls = [ft.Text("Old")]

    @pytest.mark.asyncio
    async def test_custom_transition_execution(self):
        """Test custom transition function is called."""
        async def custom_fn(page, new, old, duration):
            page.clean()
            page.add(*new)
            return new
        
        transition = RouteTransition(
            TransitionType.CUSTOM,
            custom_transition=custom_fn
        )
        
        result = await transition.apply(
            self.page,
            self.new_controls,
            self.old_controls
        )
        
        assert result == self.new_controls

    @pytest.mark.asyncio
    async def test_custom_transition_fallback_on_error(self):
        """Test fallback to fade when custom fails."""
        async def failing_fn(page, new, old, duration):
            raise ValueError("Custom failed")
        
        transition = RouteTransition(
            TransitionType.CUSTOM,
            custom_transition=failing_fn,
            duration=100
        )
        
        result = await transition.apply(
            self.page,
            self.new_controls,
            self.old_controls
        )
        
        # Should fallback to fade and still return controls
        assert result == self.new_controls


class TestTransitionWithoutOldControls:
    """Test transitions without old controls."""

    def setup_method(self):
        """Set up test fixtures."""
        self.page = MockPage()
        self.new_controls = [ft.Text("New")]

    @pytest.mark.asyncio
    async def test_fade_without_old_controls(self):
        """Test fade transition without old controls."""
        transition = RouteTransition(TransitionType.FADE, duration=100)
        
        result = await transition.apply(self.page, self.new_controls)
        
        assert result == self.new_controls

    @pytest.mark.asyncio
    async def test_slide_without_old_controls(self):
        """Test slide transition without old controls."""
        transition = RouteTransition(TransitionType.SLIDE_LEFT, duration=100)
        
        result = await transition.apply(self.page, self.new_controls)
        
        assert result == self.new_controls


class TestUtilityFunctions:
    """Test utility functions for creating transitions."""

    def test_create_slide_transition(self):
        """Test create_slide_transition utility."""
        transition = create_slide_transition(TransitionDirection.LEFT, duration=400)
        
        assert transition.type == TransitionType.SLIDE_LEFT
        assert transition.duration == 400

    def test_create_fade_transition(self):
        """Test create_fade_transition utility."""
        transition = create_fade_transition(duration=500)
        
        assert transition.type == TransitionType.FADE
        assert transition.duration == 500

    def test_create_zoom_transition(self):
        """Test create_zoom_transition utility."""
        zoom_in = create_zoom_transition(zoom_in=True)
        zoom_out = create_zoom_transition(zoom_in=False)
        
        assert zoom_in.type == TransitionType.ZOOM_IN
        assert zoom_out.type == TransitionType.ZOOM_OUT

    def test_create_slide_fade_transition(self):
        """Test create_slide_fade_transition utility."""
        transition = create_slide_fade_transition(TransitionDirection.UP)
        
        assert transition.type == TransitionType.SLIDE_FADE_UP

    def test_create_fade_through_transition(self):
        """Test create_fade_through_transition utility."""
        transition = create_fade_through_transition(duration=350)
        
        assert transition.type == TransitionType.FADE_THROUGH
        assert transition.duration == 350

    def test_create_scale_fade_transition(self):
        """Test create_scale_fade_transition utility."""
        transition = create_scale_fade_transition()
        
        assert transition.type == TransitionType.SCALE_FADE


class TestTransitionHelpers:
    """Test transition helper methods."""

    def test_push_to_slide_conversion(self):
        """Test push type to slide type conversion."""
        transition = RouteTransition()
        
        assert transition._push_to_slide_type(TransitionType.PUSH_LEFT) == TransitionType.SLIDE_LEFT
        assert transition._push_to_slide_type(TransitionType.PUSH_RIGHT) == TransitionType.SLIDE_RIGHT
        assert transition._push_to_slide_type(TransitionType.PUSH_UP) == TransitionType.SLIDE_UP
        assert transition._push_to_slide_type(TransitionType.PUSH_DOWN) == TransitionType.SLIDE_DOWN

    @pytest.mark.asyncio
    async def test_wait_for_completion(self):
        """Test wait_for_completion method."""
        transition = RouteTransition(duration=100)
        
        # Should wait for duration
        await transition.wait_for_completion()
        assert transition._animation_complete is True

    def test_set_animation_end_callback(self):
        """Test setting animation end callback."""
        transition = RouteTransition()
        callback = Mock()
        
        transition.set_animation_end_callback(callback)
        
        assert transition._animation_end_callback == callback


class TestErrorHandling:
    """Test error handling in transitions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.page = MockPage()
        self.new_controls = [ft.Text("New")]

    @pytest.mark.asyncio
    async def test_unsupported_transition_returns_controls(self):
        """Test unsupported transition type returns controls."""
        transition = RouteTransition(TransitionType.FADE)
        # Manually set an invalid type
        transition.type = "invalid_type"
        
        result = await transition.apply(self.page, self.new_controls)
        
        assert result == self.new_controls

    @pytest.mark.asyncio
    async def test_transition_error_returns_controls(self):
        """Test that errors during transition still return controls."""
        # Mock page.update to raise an error
        self.page.update = Mock(side_effect=Exception("Update failed"))
        
        transition = RouteTransition(TransitionType.FADE, duration=100)
        
        result = await transition.apply(self.page, self.new_controls)
        
        # Should still return controls despite error
        assert result == self.new_controls