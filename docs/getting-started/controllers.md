# Controllers

> **TL;DR**: A `FletXController` is where your business logic lives. It manages reactive state (`create_rx_int()`, `create_rx_str()`, etc.), handles events (local and global), manages side effects (`use_effect()`), and communicates with your UI through reactive variables and callbacks. Controllers keep your code organized and testable.

---

## What is a FletXController?

A `FletXController` is the **business logic layer** of your FletX application. It:

- **Manages state** - Reactive variables that automatically update the UI
- **Handles events** - Local communication between parts of the app, global communication across controllers
- **Manages side effects** - Code that runs when state changes
- **Provides context** - Shared data accessible across your application
- **Organizes logic** - Keeps messy business logic out of your UI code

Think of it as the **brain** of a feature, while your page is the **interface**.

---

## Why Controllers?

**Without Controllers - Logic Mixed with UI:**

```python
import flet as ft

class CounterPage(FletXPage):
    def __init__(self):
        super().__init__()
        self.count = 0
    
    def build(self):
        def on_increment(e):
            self.count += 1
            # Manual UI updates needed everywhere
            count_text.value = str(self.count)
            self.page_instance.update()
        
        def on_decrement(e):
            self.count -= 1
            # More manual updates
            count_text.value = str(self.count)
            self.page_instance.update()
        
        count_text = ft.Text(str(self.count))
        return ft.Column([
            count_text,
            ft.ElevatedButton("+", on_click=on_increment),
            ft.ElevatedButton("-", on_click=on_decrement)
        ])
```

**Problems:**

- Logic scattered in the page
- No reusability
- Hard to test
- Manual UI updates
- Difficult to modify

**With Controllers - Clean Separation:**

```python
from fletx.core import FletXController, FletXPage
from fletx.decorators import obx
import flet as ft

class CounterController(FletXController):
    def __init__(self):
        super().__init__()
        self.count = self.create_rx_int(0)
    
    def increment(self):
        self.count.increment()
        self.emit_local("counter_changed", self.count.value)
    
    def decrement(self):
        self.count.decrement()
        self.emit_local("counter_changed", self.count.value)

class CounterPage(FletXPage):
    def __init__(self):
        super().__init__()
        self.controller = CounterController()
    
    @obx
    def build(self):
        return ft.Column([
            ft.Text(str(self.controller.count)),
            ft.ElevatedButton("+", on_click=lambda _: self.controller.increment()),
            ft.ElevatedButton("-", on_click=lambda _: self.controller.decrement())
        ])
```

**Benefits:**

- ✅ Clean separation of concerns
- ✅ Reusable logic
- ✅ Easy to test
- ✅ Automatic UI updates with reactive variables
- ✅ Event-driven communication

---

## Your First Controller

### Step 1: Create a Basic Controller

```python
from fletx.core import FletXController

class GreetingController(FletXController):
    def __init__(self):
        super().__init__()
        self.name = self.create_rx_str("")
    
    def greet(self):
        return f"Hello, {self.name.value}!"
```

### Step 2: Use in a Page

```python
from fletx.core import FletXPage
from fletx.decorators import obx
import flet as ft

class GreetingPage(FletXPage):
    def __init__(self):
        super().__init__()
        self.controller = GreetingController()
    
    @obx
    def build(self):
        return ft.Column([
            ft.TextField(
                label="Your name",
                value=self.controller.name.value,
                on_change=lambda e: self.controller.name.set(e.control.value)
            ),
            ft.Text(self.controller.greet(), size=18)
        ])
```

Done! 🎉

---

## Reactive Variables

At the heart of controllers are **reactive variables** - they automatically notify the UI when they change.

### Creating Reactive Variables

```python
class MyController(FletXController):
    def __init__(self):
        super().__init__()
        
        # Integer
        self.count = self.create_rx_int(0)
        
        # String
        self.username = self.create_rx_str("")
        
        # Boolean
        self.is_enabled = self.create_rx_bool(False)
        
        # List
        self.items = self.create_rx_list([])
        
        # Dictionary
        self.config = self.create_rx_dict({"theme": "dark"})
        
        # Generic reactive value
        self.data = self.create_reactive({"key": "value"})
```

### Using Reactive Variables

```python
# Getting values
count_value = self.count.value

# Setting values
self.count.value = 5 
self.username.value = "Alice"
self.is_enabled.value = True
# Or with set() method
self.count.set(6)
self.username.set("Bob")

# Working with lists
self.items.append("new item")
self.items.extend(["item2", "item3"])
self.items.remove("new item")
self.items.pop()
self.items.clear()

# Working with dicts
self.config["theme"] = "light"
self.config.update({"lang": "fr"})
self.config.get("theme")

# Special methods for specific types
self.count.increment()  # count += 1
self.count.decrement()  # count -= 1
self.is_enabled.toggle()  # is_enabled = not is_enabled
self.username.append(" Smith")  # append to string
self.username.clear()  # clear string
```

### Listening to Changes

```python
class UserController(FletXController):
    def __init__(self):
        super().__init__()
        self.email = self.create_rx_str("")
    
    def on_ready(self):
        # Listen to email changes
        self.email.listen(self._on_email_change)
    
    def _on_email_change(self):
        print(f"Email changed to: {self.email.value}")
        # Validate email, send events, etc.
```

---

## Computed Properties

Computed properties are **derived reactive values** that automatically update when their dependencies change:

```python
class UserController(FletXController):
    def __init__(self):
        super().__init__()
        self.first_name = self.create_rx_str("John")
        self.last_name = self.create_rx_str("Doe")
        
        # Create computed full name
        self.full_name = self.create_computed(
            lambda: f"{self.first_name.value} {self.last_name.value}"
        )
    
    def on_ready(self):
        # Listen to computed value changes
        self.full_name.listen(lambda: print(f"Full name: {self.full_name.value}"))

# In page
@obx
def build(self):
    return ft.Text(self.controller.full_name.value)
    # Updates automatically when first_name or last_name changes
```

---

## Effects and Side Effects

Effects run code in response to state changes:

```python
class DataController(FletXController):
    def __init__(self):
        super().__init__()
        self.search_query = self.create_rx_str("")
        self.results = self.create_rx_list([])
    
    def on_ready(self):
        # Effect runs whenever search_query changes
        self.use_effect(
            self._perform_search,
            deps=[self.search_query]
        )
    
    def _perform_search(self):
        """Effect function that runs on every search_query change"""
        query = self.search_query.value
        if query:
            # Simulate API call
            self.results.value = self._search_database(query)
        else:
            self.results.value = []
    
    def _search_database(self, query):
        return [f"Result {i}" for i in range(3)]
```

### Effects with Cleanup

```python
class WebsocketController(FletXController):
    def __init__(self):
        super().__init__()
        self.is_connected = self.create_rx_bool(False)
        self.ws = None
    
    def on_ready(self):
        self.add_effect(self._setup_websocket)
    
    def _setup_websocket(self):
        """Effect with cleanup function"""
        print("Connecting websocket...")
        self.ws = self._create_connection()
        self.is_connected.value = True
        
        # Return cleanup function
        def cleanup():
            print("Closing websocket...")
            if self.ws:
                self.ws.close()
            self.is_connected.value = False
        
        return cleanup
    
    def _create_connection(self):
        # Simulate websocket connection
        return {"connected": True}
```

---

## Local Event Bus

Local events allow communication within a controller or between related controllers:

```python
class CartController(FletXController):
    def __init__(self):
        super().__init__()
        self.items = self.create_rx_list([])
        self.total = self.create_rx_int(0)
    
    def add_item(self, item, price):
        self.items.append(item)
        self.total.value += price
        # Emit event
        self.emit_local("item_added", {"item": item, "price": price})
    
    def remove_item(self, item):
        self.items.remove(item)
        # Emit event
        self.emit_local("item_removed", {"item": item})

class CartPage(FletXPage):
    def __init__(self):
        super().__init__()
        self.controller = CartController()
    
    def on_init(self):
        # Listen to controller events
        self.controller.on_local("item_added", self._on_item_added)
        self.controller.on_local("item_removed", self._on_item_removed)
    
    def _on_item_added(self, event):
        print(f"Item added: {event.data['item']}")
    
    def _on_item_removed(self, event):
        print(f"Item removed: {event.data['item']}")
```

### Event Bus Methods

```python
# Emit events
controller.emit_local("user_logged_in", {"username": "john"})

# Listen to events
controller.on_local("user_logged_in", callback)

# Listen only once
controller.once_local("user_logged_in", callback)

# Stop listening
controller.off_local("user_logged_in", callback)

# Get reactive list of all events
events = controller.listen_reactive_local("user_logged_in")
events.listen(lambda: print(f"Total events: {len(events.value)}"))

# Access event history
last_event = controller.event_bus.last_event.value
all_events = controller.event_bus.event_history.value
```

---

## Global Event Bus

Global events allow communication across the entire app:

```python
class NotificationController(FletXController):
    def on_ready(self):
        # Listen to global events
        self.on_global("user_logged_out", self._on_user_logged_out)
    
    def _on_user_logged_out(self, event):
        print("User logged out globally!")

class AuthController(FletXController):
    def logout(self):
        # Emit global event
        self.emit_global("user_logged_out", {})
        
        # All controllers with listeners will be notified
```

### Global Event Methods

```python
# Same as local but global scope
controller.emit_global("event_name", data)
controller.on_global("event_name", callback)
controller.once_global("event_name", callback)
controller.off_global("event_name", callback)
controller.listen_reactive_global("event_name")
```

---

## Context System

Context provides a way to store and share data:

### Local Context

```python
class UserProfileController(FletXController):
    def __init__(self):
        super().__init__()
    
    def on_ready(self):
        # Store in local context
        self.set_context("user_id", 123)
        self.set_context("user_role", "admin")
        
        # Get from context
        user_id = self.get_context("user_id")
        
        # Get reactive version
        rx_role = self.get_context_reactive("user_role")
        rx_role.listen(lambda: print(f"Role changed: {rx_role.value}"))
        
        # Check if exists
        has_user = self.has_context("user_id")
        
        # Update multiple
        self.update_context(
            user_id=124,
            user_role="user"
        )
        
        # Remove
        self.remove_context("user_role")
```

### Global Context

```python
class ThemeController(FletXController):
    def set_theme(self, theme):
        # Store globally - accessible from all controllers
        self.set_global_context("current_theme", theme)

class AnyOtherController(FletXController):
    def on_ready(self):
        # Access global context
        theme = self.get_global_context("current_theme")
        
        # Get reactive version
        rx_theme = self.get_global_context_reactive("current_theme")
        rx_theme.listen(lambda: print(f"Theme changed: {rx_theme.value}"))
```

---

## Lifecycle Hooks

Controllers go through lifecycle stages:

```
CREATED → INITIALIZED → READY → DISPOSED
```

### Lifecycle Methods

```python
class FullLifecycleController(FletXController):
    def __init__(self):
        super().__init__()
        self.data = self.create_rx_str("initial")
    
    def on_initialized(self):
        """Called when controller is created and initialized"""
        print("Controller initialized")
    
    def on_ready(self):
        """Called when controller is ready (page is showing)"""
        print("Controller ready")
        # Setup listeners, load data
        self.load_data()
    
    def on_disposed(self):
        """Called when controller is destroyed"""
        print("Controller disposed")
        # Cleanup, cancel requests, close connections
    
    def load_data(self):
        # Load initial data
        self.data.value = "loaded"
```

---

## Built-in State

Controllers include common reactive state:

```python
class ApiController(FletXController):
    def __init__(self):
        super().__init__()
        self.api_data = self.create_rx_list([])
    
    def fetch_data(self):
        # Use built-in state
        self.set_loading(True)
        self.clear_error()
        
        try:
            # Simulate API call
            data = self._call_api()
            self.api_data.value = data
        except Exception as e:
            self.set_error(str(e))
        finally:
            self.set_loading(False)
    
    def _call_api(self):
        return [{"id": 1, "name": "Item"}]

# In page
class DataPage(FletXPage):
    def __init__(self):
        super().__init__()
        self.controller = ApiController()
    
    @obx
    def build(self):
        if self.controller.is_loading:
            return ft.ProgressRing()
        
        if self.controller.error_message:
            return ft.Text(f"Error: {self.controller.error_message}")
        
        return ft.Column([
            ft.Text(f"Items: {len(self.controller.api_data)}")
        ])
```

| Built-in State | Type | Purpose |
|---|---|---|
| `is_loading` | RxBool | Shows if operation is ongoing |
| `error_message` | RxStr | Holds error messages |
| `state` | RxDict | General purpose state storage |

---

## Parent-Child Controllers

Organize complex features with nested controllers:

```python
class ParentController(FletXController):
    def __init__(self):
        super().__init__()
        self.child1 = ChildController()
        self.child2 = ChildController()
        
        # Register children
        self.add_child(self.child1)
        self.add_child(self.child2)
    
    def dispose(self):
        # Children are automatically disposed
        super().dispose()

class ChildController(FletXController):
    def __init__(self):
        super().__init__()
        self.name = self.create_rx_str("")
```

---

## Complete Real-World Example

```python
from fletx.core import FletXController, FletXPage
from fletx.decorators import obx
import flet as ft

class TodoController(FletXController):
    def __init__(self):
        super().__init__()
        self.todos = self.create_rx_list([])
        self.filter_type = self.create_rx_str("all")  # all, completed, pending
        
        # Computed filtered todos
        self.filtered_todos = self.create_computed(
            self._compute_filtered
        )
        
        # Computed stats
        self.completed_count = self.create_computed(
            lambda: len([t for t in self.todos if t["done"]])
        )
        self.total_count = self.create_computed(
            lambda: len(self.todos)
        )
    
    def _compute_filtered(self):
        if self.filter_type.value == "completed":
            return [t for t in self.todos if t["done"]]
        elif self.filter_type.value == "pending":
            return [t for t in self.todos if not t["done"]]
        return list(self.todos.value)
    
    def on_ready(self):
        # Load initial todos
        self.load_todos()
        
        # Listen for changes
        self.on_local("todo_added", lambda e: self.emit_global("todos_changed", None))
    
    def load_todos(self):
        self.set_loading(True)
        try:
            self.todos.value = [
                {"id": 1, "title": "Learn FletX", "done": False},
                {"id": 2, "title": "Build app", "done": False},
                {"id": 3, "title": "Deploy", "done": False}
            ]
        finally:
            self.set_loading(False)
    
    def add_todo(self, title):
        new_todo = {
            "id": len(self.todos) + 1,
            "title": title,
            "done": False
        }
        self.todos.append(new_todo)
        self.emit_local("todo_added", new_todo)
    
    def toggle_todo(self, todo_id):
        for todo in self.todos.value:
            if todo["id"] == todo_id:
                todo["done"] = not todo["done"]
                self.todos.value = list(self.todos.value)  # Trigger update
                break
    
    def delete_todo(self, todo_id):
        self.todos.value = [t for t in self.todos if t["id"] != todo_id]
    
    def set_filter(self, filter_type):
        self.filter_type.value = filter_type

class TodoPage(FletXPage):
    def __init__(self):
        super().__init__(padding=20)
        self.controller = TodoController()
        self.input_field = ft.TextField(label="Add new todo")
    
    def on_init(self):
        self.controller.on_local("todo_added", self._on_todo_added)
    
    def _on_todo_added(self, event):
        self.input_field.value = ""
        self.refresh()
    
    @obx
    def build(self):
        if self.controller.is_loading:
            return ft.Center(content=ft.ProgressRing())
        
        return ft.Column([
            # Header
            ft.Text(
                f"My Todos ({self.controller.completed_count}/{self.controller.total_count})",
                size=24,
                weight="bold"
            ),
            
            # Input
            ft.Row([
                ft.TextField(
                    ref=self.input_field,
                    label="Add new todo",
                    expand=True,
                ),
                ft.IconButton(
                    ft.icons.ADD,
                    on_click=lambda _: self.controller.add_todo(self.input_field.value)
                )
            ]),
            
            # Filter buttons
            ft.Row([
                ft.TextButton(
                    "All",
                    on_click=lambda _: self.controller.set_filter("all")
                ),
                ft.TextButton(
                    "Pending",
                    on_click=lambda _: self.controller.set_filter("pending")
                ),
                ft.TextButton(
                    "Completed",
                    on_click=lambda _: self.controller.set_filter("completed")
                )
            ]),
            
            # Todo list
            ft.ListView([
                ft.ListTile(
                    title=ft.Text(todo["title"]),
                    leading=ft.Checkbox(
                        value=todo["done"],
                        on_change=lambda _: self.controller.toggle_todo(todo["id"])
                    ),
                    trailing=ft.IconButton(
                        ft.icons.DELETE,
                        on_click=lambda _: self.controller.delete_todo(todo["id"])
                    )
                )
                for todo in self.controller.filtered_todos
            ])
        ], scroll=ft.ScrollMode.AUTO)
```

---

## Best Practices

### 1. Use `create_rx_*()` for Initialization

```python
# ✅ Good
class MyController(FletXController):
    def __init__(self):
        super().__init__()
        self.count = self.create_rx_int(0)

# ❌ Avoid - don't import and use directly
from fletx.core.state import RxInt
class MyController(FletXController):
    def __init__(self):
        self.count = RxInt(0)  # Wrong!
```

### 2. Initialize in `on_ready()`, not `__init__()`

```python
# ✅ Good - setup in on_ready
def on_ready(self):
    self.load_data()
    self.email.listen(self._validate_email)

# ❌ Avoid - setup in __init__
def __init__(self):
    self.load_data()  # May not work correctly
```

### 3. Use Computed for Derived Values

```python
# ✅ Good - use computed
self.full_name = self.create_computed(
    lambda: f"{self.first} {self.last}"
)

# ❌ Avoid - manual updates
self.full_name = self.create_rx_str("")
self.first.listen(lambda: self.full_name.value = f"{self.first.value} {self.last.value}")
```

### 4. Clean Up in Lifecycle

```python
def on_disposed(self):
    # Cancel requests
    self.cancel_pending()
    
    # Close connections
    if self.websocket:
        self.websocket.close()
```

### 5. Use Events for Communication

```python
# ✅ Good - use events
self.emit_local("data_changed", new_data)

# ❌ Avoid - tight coupling
page.controller.do_something()  # Page depends on controller structure
```

---

## Summary

| Feature | Purpose |
|---------|---------|
| `create_rx_int()` | Create reactive integer |
| `create_rx_str()` | Create reactive string |
| `create_rx_bool()` | Create reactive boolean |
| `create_rx_list()` | Create reactive list |
| `create_rx_dict()` | Create reactive dictionary |
| `create_computed()` | Create derived reactive value |
| `use_effect()` | Run code on state changes |
| `add_effect()` | Add effect with cleanup |
| `emit_local()` | Emit local event |
| `emit_global()` | Emit global event |
| `on_local()` | Listen to local event |
| `on_global()` | Listen to global event |
| `set_context()` | Store local context value |
| `get_context()` | Get local context value |
| `get_context_reactive()` | Get local context as reactive |
| `set_global_context()` | Store global context value |
| `get_global_context()` | Get global context value |
| `set_loading()` | Set loading state |
| `set_error()` | Set error message |
| `on_initialized()` | Lifecycle hook - initialization |
| `on_ready()` | Lifecycle hook - ready |
| `on_disposed()` | Lifecycle hook - cleanup |

---

## Next Steps

- Learn about [Pages](pages.md) to use controllers in UI
- Explore [Routing](routing.md) to share controllers across pages
- Understand [Dependency Injection](dependency-injection.md) to manage controller lifecycles
- Read about [State Management](state-management.md) for advanced patterns
- Check [Decorators](decorators.md) for reactive UI with `@obx`
