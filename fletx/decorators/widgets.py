"""
Advanced Reactive Widget Decorators for FletX

This module provides advanced decorators for creating reactive widgets
with custom bindings, transformations, and lifecycle callbacks.
"""

import flet as ft
from functools import wraps
from typing import (
    Tuple, get_type_hints, Dict, Callable, Any,
    Optional, Union, List, TypeVar  # noqa: F401
)
from dataclasses import dataclass  # noqa: F401
from enum import Enum

from fletx.core import (
    Reactive, RxInt, RxStr, RxBool, RxList, RxDict,
    FletXWidget
)
from fletx.core import (
    BindingType, BindingConfig, ComputedBindingConfig,
    FormFieldValidationRule
)
from fletx.widgets import Obx
from fletx.utils import get_logger #, get_page

logger = get_logger("FletX.WidgetDecorators")


####
##      REACTIVE BUILDER DECORATOR
#####
def obx(
        builder_fn: Callable[...,Union[ft.Control,List[ft.Control]]]
    ) -> Callable[[], ft.Control]:
    """
    Decorator that creates a reactive widget from a builder function.
    Returns the actual widget, not an Obx wrapper.

    Args:
        builder_fn: Function that return a flet control

    Returns:
        Function that returns the actual Control (preserves widget identity)

    Usage:
    ```python
    @obx
    def counter_text(self):
        return ft.Text(
            value = f'Count: {self.ctrl.count}',
            size = 50, 
            weight = "bold",
            color = 'red' if self.ctrl.count.value % 2 == 0 else 'white'
        )
    ```
    """

    @wraps(builder_fn)
    def wrapper(*args, **kwargs):

        # Create a new builder function that calls the original with args
        def internal_builder():
            return builder_fn(*args, **kwargs)
        
        # Create Obx wrapper and return the actual widget
        obx_wrapper = Obx(internal_builder)
        return obx_wrapper 
    
    return wrapper


####
##      REACTIVE CONTROL DECORATOR
#####
def reactive_control(
    bindings: Union[Dict[str, Union[str, BindingConfig]], Dict[str, str]] = None,
    computed_bindings: Dict[str, ComputedBindingConfig] = None,
    lifecycle_callbacks: Dict[str, Callable] = None,
    auto_dispose: bool = True
):
    """
    Advanced decorator that creates reactive controls with sophisticated binding options.
    
    Args:
        bindings: Mapping of widget properties to reactive bindings
        computed_bindings: Computed properties derived from multiple reactives
        lifecycle_callbacks: Callbacks for widget lifecycle events
        auto_dispose: Whether to automatically dispose reactives on unmount
    
    Usage:
    ```python
    @reactive_control(
        bindings={
            'value': BindingConfig(
                reactive_attr='rx_value',
                binding_type=BindingType.TWO_WAY,
                transform_to_widget=lambda x: str(x),
                validation=lambda x: x >= 0,
                on_change=lambda old, new: print(f"Changed: {old} -> {new}"),
                debounce_ms=300
            ),
            'visible': 'rx_visible'  # Simple binding
        },
        computed_bindings={
            'text': ComputedBindingConfig(
                compute_fn=lambda: f"Value: {self.rx_value.value}",
                dependencies=['rx_value']
            )
        },
        lifecycle_callbacks={
            'did_mount': lambda self: print("Widget mounted"),
            'will_unmount': lambda self: print("Widget unmounting")
        }
    )
    class MyReactiveInput(ft.TextField):
        def __init__(self, *args, **kwargs):
            self.rx_value = RxStr("")
            self.rx_visible = RxBool(True)
            super().__init__(*args, **kwargs)
    ```
    """

    if bindings is None:
        bindings = {}

    if computed_bindings is None:
        computed_bindings = {}

    if lifecycle_callbacks is None:
        lifecycle_callbacks = {}


    def decorator(ControlClass):

        # Store original methods
        original_init = ControlClass.__init__
        original_did_mount = getattr(ControlClass, 'did_mount', None)
        original_will_unmount = getattr(ControlClass, 'will_unmount', None)

        # Add FletXWidget as a parent while preserving existing parents
        ControlClass.__bases__ = (*ControlClass.__bases__, FletXWidget)

        @wraps(original_init)
        def __init__(self, *args, **kwargs):

            # Call original initialization
            original_init(self, *args, **kwargs)

            # ControlClass._Control__uid = None
            # Initialize FletXWidget
            FletXWidget.__init__(self)

            # Storage for binding observers and timers
            self._binding_observers = {}
            self._binding_timers = {}
            self._computed_reactives = {}

            # Validate reactive attributes
            self._validate_reactive_attributes()

            # Setup bindings
            self._setup_bindings()
            self._setup_computed_bindings()

            logger.debug(f"Initialized reactive control {ControlClass.__name__}")

        def _validate_reactive_attributes(self):
            """Validate that required reactive attributes exist"""

            type_hints = get_type_hints(ControlClass)  # noqa: F841
            
            for widget_prop, binding in bindings.items():
                if isinstance(binding, str):
                    rx_name = binding
                else:
                    rx_name = binding.reactive_attr
                
                if not hasattr(self, rx_name):
                    raise AttributeError(
                        f"Reactive attribute '{rx_name}' not found in {ControlClass.__name__}"
                    )
                
                reactive_obj = getattr(self, rx_name)
                if not isinstance(reactive_obj, (Reactive, RxInt, RxStr, RxBool, RxList, RxDict)):
                    raise TypeError(
                        f"Attribute '{rx_name}' must be a reactive type, got {type(reactive_obj)}"
                    )
                
        def _setup_bindings(self):
            """Setup reactive bindings with advanced features"""

            for widget_prop, binding in bindings.items():
                if isinstance(binding, str):
                    # Simple binding
                    binding_config = BindingConfig(reactive_attr=binding)
                else:
                    binding_config = binding
                
                self._setup_single_binding(widget_prop, binding_config)

        def _setup_single_binding(
            self, 
            widget_prop: str, 
            config: BindingConfig
        ):
            """Setup a single reactive binding"""

            reactive_obj = getattr(self, config.reactive_attr)
            
            if config.binding_type == BindingType.ONE_TIME:
                # One-time binding
                self._apply_one_time_binding(widget_prop, reactive_obj, config)
            else:
                # Reactive binding
                callback = self._create_binding_callback(widget_prop, config)
                
                # Apply debouncing/throttling if specified
                if config.debounce_ms:
                    callback = self._debounce(callback, config.debounce_ms)

                elif config.throttle_ms:
                    callback = self._throttle(callback, config.throttle_ms)
                
                observer = reactive_obj.listen(callback, auto_dispose=False)
                self._binding_observers[widget_prop] = observer
                
                # Setup two-way binding if needed
                if config.binding_type == BindingType.TWO_WAY:
                    self._setup_two_way_binding(widget_prop, config, reactive_obj)
                
                # Initial value
                callback()
        
        def _create_binding_callback(
            self, 
            widget_prop: str, 
            config: BindingConfig
        ):
            """Create a callback for reactive binding"""

            def callback():
                if not self._is_mounted:
                    return
                
                reactive_obj = getattr(self, config.reactive_attr)
                new_value = reactive_obj.value
                
                # Apply condition check
                if config.condition and not config.condition():
                    return
                
                # Apply validation
                if config.validation and not config.validation(new_value):
                    logger.warning(
                        f"Validation failed for {widget_prop}: {new_value}"
                    )
                    return
                
                # Transform value for widget
                if config.transform_to_widget:
                    new_value = config.transform_to_widget(new_value)
                
                # Get old value for change callback
                old_value = getattr(self, widget_prop, None)
                
                # Update widget property
                setattr(self, widget_prop, new_value)
                
                # Call change callback
                if config.on_change:
                    config.on_change(old_value, new_value)

                # self.content = self.build()
                
                # Update the widget
                self.update()

                logger.debug(
                    f"Updated {widget_prop} from reactive "
                    f"{config.reactive_attr}: {new_value}"
                )
            
            return callback
        
        def _apply_one_time_binding(
            self, 
            widget_prop: str, 
            reactive_obj: Reactive, 
            config: BindingConfig
        ):
            """Apply one-time binding"""

            value = reactive_obj.value
            
            if config.transform_to_widget:
                value = config.transform_to_widget(value)
            
            setattr(self, widget_prop, value)
            logger.debug(f"Applied one-time binding {widget_prop}: {value}")

        def _setup_two_way_binding(
            self, 
            widget_prop: str, 
            config: BindingConfig, 
            reactive_obj: Reactive
        ):
            """Setup two-way binding for supported widgets"""

            # This is a simplified implementation 
            # we'd need to handle specific widget events Later :-)
            if hasattr(self, 'on_change'):
                original_on_change = self.on_change
                
                def on_change_handler(e):
                    widget_value = getattr(self, widget_prop)
                    
                    # Transform value from widget
                    if config.transform_from_widget:
                        widget_value = config.transform_from_widget(widget_value)
                    
                    # Update reactive
                    reactive_obj.value = widget_value
                    
                    # Call original handler
                    if original_on_change:
                        original_on_change(e)
                
                self.on_change = on_change_handler

        def _setup_computed_bindings(self):
            """Setup computed reactive bindings"""
            for widget_prop, config in computed_bindings.items():
                # Create dependencies list
                deps = [getattr(self, dep_name) for dep_name in config.dependencies]
                
                # Create computed reactive
                from fletx.core.state import Computed
                computed = Computed(
                    lambda: config.compute_fn(),
                    dependencies=deps
                )
                
                self._computed_reactives[widget_prop] = computed
                
                # Setup binding for computed value
                def computed_callback():
                    if not self._is_mounted:
                        return
                    
                    value = computed.value
                    
                    if config.transform:
                        value = config.transform(value)
                    
                    old_value = getattr(self, widget_prop, None)
                    setattr(self, widget_prop, value)
                    
                    if config.on_change:
                        config.on_change(old_value, value)
                    
                    self.update()
                
                observer = computed.listen(computed_callback, auto_dispose=False)
                self._binding_observers[f"computed_{widget_prop}"] = observer
                
                # Initial value
                computed_callback()

        def _debounce(self, func: Callable, delay_ms: int):
            """Create debounced version of function"""
            import asyncio
            
            def debounced():
                if hasattr(self, '_debounce_tasks'):
                    if func in self._debounce_tasks:
                        self._debounce_tasks[func].cancel()
                else:
                    self._debounce_tasks = {}
                
                async def delayed_call():
                    await asyncio.sleep(delay_ms / 1000)
                    func()
                
                task = asyncio.create_task(delayed_call())
                self._debounce_tasks[func] = task
            
            return debounced
        
        def _throttle(self, func: Callable, interval_ms: int):
            """Create throttled version of function"""
            import time
            
            def throttled():
                now = time.time()
                if not hasattr(self, '_throttle_last_calls'):
                    self._throttle_last_calls = {}
                
                if (func not in self._throttle_last_calls or 
                    now - self._throttle_last_calls[func] >= interval_ms / 1000):
                    self._throttle_last_calls[func] = now
                    func()
            
            return throttled
        
        def did_mount(self):
            """Enhanced did_mount with lifecycle callbacks"""

            if original_did_mount:
                original_did_mount(self)
            
            if 'did_mount' in lifecycle_callbacks:
                lifecycle_callbacks['did_mount'](self)
            
            FletXWidget.did_mount(self)
            
            logger.debug(f"Mounted reactive control {ControlClass.__name__}")

        def will_unmount(self):
            """Enhanced will_unmount with cleanup"""
            if 'will_unmount' in lifecycle_callbacks:
                lifecycle_callbacks['will_unmount'](self)
            
            # Cleanup binding observers
            for observer in self._binding_observers.values():
                observer.dispose()
            self._binding_observers.clear()
            
            # Cleanup computed reactives
            for computed in self._computed_reactives.values():
                computed.dispose()
            self._computed_reactives.clear()
            
            # Cleanup debounce tasks
            if hasattr(self, '_debounce_tasks'):
                for task in self._debounce_tasks.values():
                    task.cancel()
            
            if original_will_unmount:
                original_will_unmount(self)
            
            logger.debug(f"Unmounted reactive control {ControlClass.__name__}")
        
        # Inject new methods
        ControlClass.__init__ = __init__
        ControlClass._validate_reactive_attributes = _validate_reactive_attributes
        ControlClass._setup_bindings = _setup_bindings
        ControlClass._setup_single_binding = _setup_single_binding
        ControlClass._create_binding_callback = _create_binding_callback
        ControlClass._apply_one_time_binding = _apply_one_time_binding
        ControlClass._setup_two_way_binding = _setup_two_way_binding
        ControlClass._setup_computed_bindings = _setup_computed_bindings
        ControlClass._debounce = _debounce
        ControlClass._throttle = _throttle
        ControlClass.did_mount = did_mount
        ControlClass.will_unmount = will_unmount

        return ControlClass
    
    return decorator


####
##      CONVENIENCE DECORATOR
#####
def simple_reactive(bindings: Dict[str, str]):
    """
    Simplified version of reactive_control for basic bindings.
    
    Usage:
    ```python
    @simple_reactive({'value': 'rx_value', 'visible': 'rx_visible'})
    class MyInput(ft.TextField):
        def __init__(self):
            self.rx_value = RxStr("")
            self.rx_visible = RxBool(True)
            super().__init__()
    ```
    """
    return reactive_control(bindings=bindings)


####
##      TWO WAY REACTIVE DECORATOR
#####
def two_way_reactive(bindings: Dict[str, str]):
    """
    Creates two-way reactive bindings.
    
    Usage:
    ```python
    @two_way_reactive({'value': 'rx_value'})
    class MyInput(ft.TextField):
        def __init__(self):
            self.rx_value = RxStr("")
            super().__init__()
    ```
    """
    binding_configs = {
        prop: BindingConfig(
            reactive_attr = rx_attr,
            binding_type = BindingType.TWO_WAY
        )
        for prop, rx_attr in bindings.items()
    }
    return reactive_control(bindings=binding_configs)


####
##      COMPUTED REACTIVE WIDGET DECORATOR
#####
def computed_reactive(**computed_props):
    """
    Creates reactive controls with computed properties.
    
    Usage:
    ```python
    @computed_reactive(
        text=lambda self: f"Count: {self.rx_count.value}",
        color=lambda self: "red" if self.rx_count.value > 10 else "blue"
    )
    class MyText(ft.Text):
        def __init__(self):
            self.rx_count = RxInt(0)
            super().__init__()
    ```
    """
    computed_bindings = {}
    for prop, compute_fn in computed_props.items():
        computed_bindings[prop] = ComputedBindingConfig(
            compute_fn=lambda self=None, fn=compute_fn: fn(self),
            dependencies=['rx_count']  # You'd need to auto-detect this
        )
    
    return reactive_control(computed_bindings=computed_bindings)


####
##      REACTIVE FORM DECORATOR
#####
def reactive_form(
    form_fields: Dict[str, str],
    validation_rules: Optional[Dict[str,Union[str,List[FormFieldValidationRule]]]] = None,
    on_submit: Optional[Union[Callable,str]] = None,
    on_submit_success: Optional[Union[Callable,str]] = None,
    on_submit_failed: Optional[Union[Callable,str]] = None,
    on_submit_exception: Optional[Union[Callable,str]] = None,
    auto_validate: bool = True
):
    """
    Creates a reactive form with validation and submission handling.
    
    Args:
        form_fields: Mapping of form field names to reactive attributes
        validation_rules: Validation functions for each field
        on_submit: Callback when form is submitted
        auto_validate: Whether to validate fields on change
    
    Usage:
    ```python
    @reactive_form(
        form_fields={
            'username': 'rx_username',
            'email': 'rx_email',
            'password': 'rx_password'
            'confirm_password': 'rx_confirm_password'
        },
        validation_rules={
            'username': lambda x: len(x) >= 3,
            'email': 'validate_email',          # Will call MyForm().validate_email(value)
            'password': lambda x: len(x) >= 8,
            'confirm_password': [
                FormFieldValidationRule(
                    validate_fn = 'validate_one',  # Will call MyFrm().validate_one(value)
                    err_message = '{field} validate one error message'
                ),
                FormFieldValidationRule(
                    validate_fn = lambda value : value != 'azerty',
                    err_message = '{field} value cannot be "azerty".'
                )
            ]
        },
        on_submit = lambda form: print("Form submitted:", form.get_values())
        on_submit_success = lambda values: print("Form values:", values)
        on_submit_failed = lambda errors: print("Errors:", errors)
        on_submit_exception = lambda msg: print("Form submit exception:", msg)
    )
    class MyForm(ft.Column):
        def __init__(self):
            self.rx_username = RxStr("")
            self.rx_email = RxStr("")
            self.rx_password = RxStr("")
            self.rx_confirm_password = RxStr("")
            self.rx_is_valid = RxBool(False)
            super().__init__()

        def validate_email(self,value): -> bool:
            # Validation logic here...
            return True

        # Other handler methods ...
    ```
    """
    
    if validation_rules is None:
        validation_rules = {}
    
    def decorator(FormClass):
        original_init = FormClass.__init__
        
        # Add FletXWidget as parent
        FormClass.__bases__ = (*FormClass.__bases__, FletXWidget)
        
        @wraps(original_init)
        def __init__(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            FletXWidget.__init__(self)
            
            # Form state
            self._form_errors = {}
            self._validation_observers = []
            
            # Setup form bindings
            self._setup_form_bindings()
            
            # Add form methods
            self.get_values = lambda: {
                field: getattr(self, rx_attr).value
                for field, rx_attr in form_fields.items()
            }
            
            self.get_errors = lambda: self._form_errors.copy()
            
            self.is_valid = lambda: len(self._form_errors) == 0
            
            self.submit = lambda: self._handle_submit()
            
            self.validate_field = lambda field: self._validate_field(field)
            
            self.validate_all = lambda: self._validate_all_fields()

        def _setup_form_bindings(self):
            """Setup reactive bindings for form fields"""

            for field, rx_attr in form_fields.items():
                reactive_obj = getattr(self, rx_attr)
                
                if auto_validate and field in validation_rules:
                    # Setup validation on change
                    def create_validator(field_name):
                        def validator():
                            self._validate_field(field_name)
                        return validator
                    
                    observer = reactive_obj.listen(create_validator(field), auto_dispose=False)
                    self._validation_observers.append(observer)

        def _validate_field(self, field: str) -> bool:
            """Validate a single field"""

            if field not in validation_rules:
                return True
            
            rx_attr = form_fields[field]
            value = getattr(self, rx_attr).value

            # Get field validation rules
            rules = validation_rules[field]
            is_valid = False
            errors: List[str] = []

            # 1. rules is Callable
            if callable(rules):
                # Then call it with the value
                is_valid = rules(value)

            # 2. FormClass Callable attribute (function)
            elif isinstance(rules, str): 
                if hasattr(self,rules):
                    is_valid = getattr(self,rules)(value)

                # otherwise ignore the rule
                else:
                    logger.warning(
                        f'Rule {rules} ignored beacause for {field} field'
                        f'{FormClass.__name__} has no attribute {rules}.'
                    )

            # 3. There are multiple rules for the field (FormFieldValidationRules)
            elif isinstance(rules,list):
                checks: List[bool] = []
                for rule in rules:
                    check: bool = True
                    # FormClass Callable attribute (function)
                    if isinstance(rule.validate_fn, str):
                        if hasattr(self,rule.validate_fn):
                            check = getattr(self,rule.validate_fn)(value)

                        # otherwise ignore the rule
                        else:
                            logger.warning(
                                f'Rule {rules} ignored for "{field}" field beacause '
                                f'{FormClass.__name__} has no attribute {rules}.'
                            )
                    # Validation function (callable)
                    elif callable(rule.validate_fn):
                        check = rule.validate_fn(value)

                    # Add rule message if rule fails
                    if not check:
                        errors.append(rule.err_message.format(field = field, value = value)) 

                    # finally append validatio result
                    checks.append(check)
                is_valid = all(checks)
            
            if is_valid:
                self._form_errors.pop(field, None)
            else:
                self._form_errors[field] = errors or f"Invalid {field} value"
                if auto_validate:
                    self._call_handler(on_submit_failed, self.get_errors())
            
            # Update form validity if rx_is_valid exists
            if hasattr(self, 'rx_is_valid'):
                self.rx_is_valid.value = self.is_valid()
            
            logger.debug(f"Validated {field}: {is_valid}")
            return is_valid

        def _validate_all_fields(self) -> bool:
            """Validate all form fields"""

            all_valid = True
            for field in form_fields.keys():
                if not self._validate_field(field):
                    all_valid = False
            return all_valid

        def _handle_submit(self):
            """Handle form submission in a reactive and extensible way."""

            try:
                # Validation des champs
                is_valid = self._validate_all_fields()

                if not is_valid:
                    logger.warning("Form submission failed due to validation errors")
                    if on_submit_failed:
                        self._call_handler(on_submit_failed, self.get_errors())
                    return

                # Soumission réussie
                logger.info("Form validated successfully")

                if on_submit:
                    self._call_handler(on_submit,self)

                if on_submit_success:
                    self._call_handler(on_submit_success,self.get_values())

            except Exception as e:
                logger.exception("Unexpected error during form submission")
                if on_submit_exception:
                    self._call_handler(on_submit_exception,e)
            
        def _call_handler(self, handler: Union[str,Callable[[],None]], *args, **kwargs):
            """Cal the given handler (method name or callable)."""

            if isinstance(handler, str):
                method = getattr(self, handler, None)
                if not callable(method):
                    raise AttributeError(
                        f'{self.__class__.__name__} has no callable method "{handler}"'
                    )
                method(*args, **kwargs)
            
            elif callable(handler):
                handler(*args, **kwargs)
            
            else:
                raise TypeError(
                    f"{handler} must be a string (method name) or a callable"
                )

        def will_unmount(self):
            """Cleanup form observers"""

            for observer in self._validation_observers:
                observer.dispose()
            self._validation_observers.clear()

            for rx_obj in form_fields.values():
                reactive_obj = getattr(self, rx_obj, None)
                if reactive_obj and hasattr(reactive_obj, 'dispose'):
                    reactive_obj.dispose()
            
            super(FormClass, self).will_unmount()
            FletXWidget.will_unmount(self)

        # Inject methods
        FormClass.__init__ = __init__
        FormClass._setup_form_bindings = _setup_form_bindings
        FormClass._validate_field = _validate_field
        FormClass._validate_all_fields = _validate_all_fields
        FormClass._handle_submit = _handle_submit
        FormClass._call_handler = _call_handler
        FormClass.will_unmount = will_unmount

        return FormClass
    
    return decorator


####
##      REACTIVE LIST WIDGET DECORATOR
#####
def reactive_list(
    items_attr: str,
    item_builder: Callable[[Any, int], ft.Control],
    empty_builder: Optional[Callable[[], ft.Control]] = None,
    animate_changes: bool = True
):
    """
    Creates a reactive list widget that automatically updates when items change.
    
    Args:
        items_attr: Name of the RxList attribute
        item_builder: Function to build each item widget
        empty_builder: Function to build empty state widget
        animate_changes: Whether to animate list changes
    
    Usage:
    ```python
    @reactive_list(
        items_attr='rx_items',
        item_builder=lambda item, index: ft.Text(f"{index}: {item}"),
        empty_builder=lambda: ft.Text("No items"),
        animate_changes=True
    )
    class MyList(ft.Column):
        def __init__(self):
            self.rx_items = RxList(["Item 1", "Item 2"])
            super().__init__()
    ```
    """
    
    def decorator(ListClass):
        original_init = ListClass.__init__
        original_did_mount = getattr(ListClass, 'did_mount', None)
        
        # Add FletXWidget as parent
        ListClass.__bases__ = (*ListClass.__bases__, FletXWidget)
        
        @wraps(original_init)
        def __init__(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            FletXWidget.__init__(self)
            
            self._list_observer = None
            self._current_controls = []

            # Setup a basic size animation
            if animate_changes:
                self.animate_size = True

        def _setup_list_binding(self):
            """Setup reactive binding for list items"""
            items_list = getattr(self, items_attr)
            
            if not isinstance(items_list, RxList):
                raise TypeError(f"{items_attr} must be an RxList")
            
            self._list_observer = items_list.listen(self._rebuild_list, auto_dispose=False)
            
            # Initial build
            self._rebuild_list()

        def _rebuild_list(self):
            """Rebuild the list controls"""
            if not self._is_mounted:
                return
            
            items_list = getattr(self, items_attr)
            items = items_list.value
            
            # Clear current controls
            self.controls.clear()
            self._current_controls.clear()
            
            # Build new controls
            if not items and empty_builder:
                empty_control = empty_builder()
                self.controls.append(empty_control)
                self._current_controls.append(empty_control)
            else:
                for index, item in enumerate(items):
                    control = item_builder(item, index)
                    self.controls.append(control)
                    self._current_controls.append(control)
            
            # Update the widget
            self.update()
            
            logger.debug(f"Rebuilt list with {len(items)} items")

        def did_mount(self):
            """Enhanced did_mount with lifecycle callbacks"""

            if original_did_mount:
                original_did_mount(self)

            # Call FletXWidget did mount
            FletXWidget.did_mount(self)

            # Setup list binding, once the widget is mounted
            self._setup_list_binding()
            
            logger.debug(f"Mounted reactive List control {ListClass.__name__}")

        def will_unmount(self):
            """Cleanup list observer"""
            if self._list_observer:
                self._list_observer.dispose()
                self._list_observer = None
            
            # Call Super's will_mount method if any
            super(ListClass,self).will_unmount()
            FletXWidget.will_unmount(self)

        # Inject methods
        ListClass.__init__ = __init__
        ListClass._setup_list_binding = _setup_list_binding
        ListClass._rebuild_list = _rebuild_list
        ListClass.did_mount = did_mount
        ListClass.will_unmount = will_unmount

        return ListClass
    
    return decorator


####
##      REACTIVE STATE MACHINE DECORATOR
####
def reactive_state_machine(
    states: Enum,
    initial_state: Enum,
    transitions: Dict[Tuple[Enum, str], Enum],
    state_attr: str = 'rx_state',
    on_state_change: Optional[Callable[[Enum, Enum], None]] = None
):
    """
    Creates a reactive state machine for widgets.
    
    Args:
        states: Enum defining possible states
        initial_state: Initial state
        transitions: Valid transitions {(from_state, action): to_state}
        state_attr: Name of the reactive state attribute
        on_state_change: Callback when state changes
    
    Usage:
    ```python
    class LoadingState(Enum):
        IDLE = "idle"
        LOADING = "loading"
        SUCCESS = "success"
        ERROR = "error"
    
    @reactive_state_machine(
        states=LoadingState,
        initial_state=LoadingState.IDLE,
        transitions={
            (LoadingState.IDLE, 'start_loading'): LoadingState.LOADING,
            (LoadingState.LOADING, 'success'): LoadingState.SUCCESS,
            (LoadingState.LOADING, 'error'): LoadingState.ERROR,
            (LoadingState.SUCCESS, 'reset'): LoadingState.IDLE,
            (LoadingState.ERROR, 'retry'): LoadingState.LOADING,
        },
        on_state_change=lambda old, new: print(f"State: {old} -> {new}")
    )
    class LoadingWidget(ft.Container):
        def __init__(self):
            super().__init__()
    ```
    """
    
    def decorator(WidgetClass):
        original_init = WidgetClass.__init__
        
        # Add FletXWidget as parent
        WidgetClass.__bases__ = (*WidgetClass.__bases__, FletXWidget)
        
        @wraps(original_init)
        def __init__(self, *args, **kwargs):
            # Initialize state reactive
            state_reactive = RxStr(initial_state.value)
            setattr(self, state_attr, state_reactive)
            
            original_init(self, *args, **kwargs)
            FletXWidget.__init__(self)
            
            self._state_observer = None
            self._setup_state_machine()

        def _setup_state_machine(self):
            """Setup state machine reactive binding"""
            state_reactive = getattr(self, state_attr)
            
            if on_state_change:
                def state_change_handler():
                    current_state_value = state_reactive.value
                    current_state = next(
                        (s for s in states if s.value == current_state_value),
                        None
                    )
                    if current_state:
                        on_state_change(None, current_state)  # TODO: Track previous state
                
                self._state_observer = state_reactive.listen(
                    state_change_handler, 
                    auto_dispose=False
                )

        def transition(self, action: str) -> bool:
            """Attempt to transition to a new state"""
            state_reactive = getattr(self, state_attr)
            current_state_value = state_reactive.value
            current_state = next(
                (s for s in states if s.value == current_state_value),
                None
            )
            
            if not current_state:
                logger.error(f"Invalid current state: {current_state_value}")
                return False
            
            transition_key = (current_state, action)
            if transition_key not in transitions:
                logger.warning(f"Invalid transition: {current_state} + {action}")
                return False
            
            new_state = transitions[transition_key]
            old_state = current_state
            
            state_reactive.value = new_state.value
            
            if on_state_change:
                on_state_change(old_state, new_state)
            
            logger.info(f"State transition: {old_state} -> {new_state} (action: {action})")
            return True

        def get_current_state(self) -> Enum:
            """Get current state as enum"""
            state_reactive = getattr(self, state_attr)
            current_state_value = state_reactive.value
            return next(
                (s for s in states if s.value == current_state_value),
                initial_state
            )

        def can_transition(self, action: str) -> bool:
            """Check if transition is possible"""
            current_state = self.get_current_state()
            return (current_state, action) in transitions

        def will_unmount(self):
            """Cleanup state machine observer"""
            if self._state_observer:
                self._state_observer.dispose()
                self._state_observer = None
            
            if hasattr(super(), 'will_unmount'):
                super().will_unmount()

        # Inject methods
        WidgetClass.__init__ = __init__
        WidgetClass._setup_state_machine = _setup_state_machine
        WidgetClass.transition = transition
        WidgetClass.get_current_state = get_current_state
        WidgetClass.can_transition = can_transition
        WidgetClass.will_unmount = will_unmount

        return WidgetClass
    
    return decorator