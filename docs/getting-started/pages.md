# Pages

> **TL;DR**: A `FletXPage` is a complete screen component with structured lifecycle (`on_init()`, `on_destroy()`), a `build()` method for UI, automatic controller management, event handling (keyboard, gestures, window events), and built-in support for app bars, drawers, floating action buttons, and keyboard shortcuts.

---

## What is a FletXPage?

A `FletXPage` represents a **single screen or view** in your FletX application. It's much more than Flet's basic page - it's a fully-featured component system that includes:

- **Lifecycle management** - Structured stages from initialization to disposal
- **Built-in event handling** - Keyboard, gestures, window resize, media changes
- **Navigation elements** - App bars, drawers, FABs, bottom sheets
- **Controller integration** - Seamless connection to business logic
- **Reactive updates** - Automatic UI refresh on state changes
- **Keyboard shortcuts** - Power-user features
- **Performance monitoring** - Track render times and statistics
- **Resource cleanup** - Automatic disposal of effects and subscriptions

---

## Why FletXPage?

**Plain Flet - Manual and Scattered:**

```python
import flet as ft

def main(page: ft.Page):
    page.title = "Todo"
    todos = []  # State scattered
    
    def add_todo(e):
        todos.append(input_field.value)
        # Manual UI update
        list_view.controls.clear()
        for todo in todos:
            list_view.controls.append(ft.Text(todo))
        page.update()
    
    input_field = ft.TextField()
    list_view = ft.Column()
    page.add(input_field, ft.ElevatedButton("Add", on_click=add_todo), list_view)
    # No cleanup, no structure

ft.app(target=main)
```

**FletX - Organized and Reactive:**

```python
from fletx.core import FletXPage, FletXController
from fletx.decorators import obx
import flet as ft

class TodoController(FletXController):
    def __init__(self):
        super().__init__()
        self.todos = self.create_rx_list([])
    
    def add_todo(self, title: str):
        self.todos.append(title)
        self.emit_local("todo_added", title)

class TodoPage(FletXPage):
    def __init__(self):
        super().__init__()
        self.controller = TodoController()
    
    def on_init(self):
        # Called when page appears
        self.controller.on_local("todo_added", self._on_todo_added)
    
    def _on_todo_added(self, event):
        self.refresh()

    def build(self):
        return ft.Column([
            ft.TextField(label="Add todo"),
            ft.Column([
                ft.Text(todo) for todo in self.controller.todos
            ])
        ])
```

**Benefits:**

- ✅ Clear structure and organization
- ✅ Automatic state and UI synchronization
- ✅ Proper lifecycle and resource cleanup
- ✅ Event-driven architecture

---

## Page Lifecycle

FletX pages go through distinct stages:

```
INITIALIZING → MOUNTED → ACTIVE → UNMOUNTING → DISPOSED
```

### Lifecycle States

| State | When | What You Can Do |
|-------|------|-----------------|
| `INITIALIZING` | Page created in `__init__()` | Initialize controller, setup state |
| `MOUNTED` | Page attached to view | `on_init()` called - load data |
| `ACTIVE` | Page fully visible | Respond to user input |
| `UNMOUNTING` | Before removal | `on_destroy()` called - cleanup |
| `DISPOSED` | After removal | Resources freed |

### Lifecycle Hooks

```python
class MyPage(FletXPage):
    def on_init(self):
        """Called when page becomes visible"""
        print("Page appeared!")
        # Load data
        self.controller.load_data()
        # Setup listeners
        self.controller.on_local("data_loaded", self._on_data_ready)
    
    def on_destroy(self):
        """Called when page will be removed"""
        print("Page will disappear!")
        # Cancel requests
        self.controller.cancel_pending()
        # Close connections
        if hasattr(self, 'websocket'):
            self.websocket.close()
```

---

## Your First FletXPage

### Step 1: Create a Simple Page

```python
import flet as ft
from fletx.core import FletXPage

class HelloPage(FletXPage):
    def build(self):
        return ft.Column([
            ft.Text("Hello FletX!", size=32),
            ft.ElevatedButton("Click Me")
        ])
```

### Step 2: Register and Run

```python
from fletx import FletXApp
from fletx.navigation import router_config

router_config.add_route("/", HelloPage)
app = FletXApp()
app.run()
```

Done! 🎉

---

## Building UI with `build()`

The `build()` method returns your page's UI. Key principles:

- **Pure** - No side effects
- **Fast** - Should render quickly
- **Declarative** - Describe what UI to show

### Basic Layout

```python
def build(self):
    return ft.Column([
        ft.Text("Title"),
        ft.TextField(label="Input"),
        ft.ElevatedButton("Submit")
    ])
```

### Reactive UI with `@obx`

```python
from fletx.decorators import obx

class CounterPage(FletXPage):
    def __init__(self):
        super().__init__()
        self.controller = CounterController()
    
    @obx
    def counter_display(self):
        """Rebuilds automatically when count changes"""
        return ft.Text(
            f"Count: {self.controller.count}",
            size=24,
            weight="bold"
        )
    
    def build(self):
        return ft.Column([
            self.counter_display(),
            ft.Row([
                ft.ElevatedButton(
                    "Increment",
                    on_click=lambda _: self.controller.count.increment()
                ),
                ft.ElevatedButton(
                    "Decrement",
                    on_click=lambda _: self.controller.count.decrement()
                )
            ])
        ])
```

### Complex Layouts

```python
def build(self):
    return ft.Column([
        # Header
        ft.Container(
            content=ft.Text("Dashboard", size=28, weight="bold"),
            padding=20,
            bgcolor=ft.colors.BLUE
        ),
        # Content
        ft.Container(
            content=ft.Row([
                # Sidebar
                ft.Container(
                    content=ft.Column([
                        ft.Text("Menu"),
                        ft.TextButton("Home"),
                        ft.TextButton("Settings")
                    ]),
                    width=200,
                    bgcolor=ft.colors.SURFACE
                ),
                # Main content
                ft.Container(
                    content=ft.Text("Main content here"),
                    expand=True
                )
            ]),
            expand=True
        )
    ])
```

---

## Working with Controllers

Controllers contain your business logic. Here's how to use them correctly:

### Create a Controller

```python
from fletx.core import FletXController

class UserController(FletXController):
    def __init__(self):
        super().__init__()
        # Create reactive variables using create_rx_* methods
        self.username = self.create_rx_str("")
        self.email = self.create_rx_str("")
        self.is_loading = self.create_rx_bool(False)
        self.users = self.create_rx_list([])
        self.error = self.create_rx_str("")
    
    def load_users(self):
        """Load users from API"""
        self.set_loading(True)
        self.clear_error()
        
        try:
            # Fetch data
            users_data = self._fetch_users()
            self.users.value = users_data
            
            # Emit event
            self.emit_local("users_loaded", len(users_data))
        except Exception as e:
            self.set_error(str(e))
            self.emit_local("error", str(e))
        finally:
            self.set_loading(False)
    
    def add_user(self, username: str, email: str):
        """Add a new user"""
        user = {"name": username, "email": email}
        self.users.append(user)
        self.emit_local("user_added", user)
    
    def _fetch_users(self):
        # Simulate API call
        return [
            {"name": "Alice", "email": "alice@example.com"},
            {"name": "Bob", "email": "bob@example.com"}
        ]
```

### Use Controller in Page

```python
class UsersPage(FletXPage):
    def __init__(self):
        super().__init__()
        # Create controller
        self.controller = UserController()
    
    def on_init(self):
        """When page appears"""
        # Load data
        self.controller.load_users()
        
        # Listen to events
        self.controller.on_local("users_loaded", self._on_users_loaded)
        self.controller.on_local("user_added", self._on_user_added)
        self.controller.on_local("error", self._on_error)
    
    def _on_users_loaded(self, event):
        print(f"Loaded {event.data} users")
        self.refresh()
    
    def _on_user_added(self, event):
        print(f"Added user: {event.data}")
        self.refresh()
    
    def _on_error(self, event):
        print(f"Error: {event.data}")
        self.refresh()
    
    @obx
    def build(self):
        # Show loader while loading
        if self.controller.is_loading:
            return ft.Center(
                content=ft.Column([
                    ft.ProgressRing(),
                    ft.Text("Loading...")
                ])
            )
        
        # Show error if present
        if self.controller.error:
            return ft.Center(
                content=ft.Column([
                    ft.Icon(ft.icons.ERROR, color=ft.colors.RED),
                    ft.Text(f"Error: {self.controller.error}")
                ])
            )
        
        # Show users
        return ft.Column([
            ft.Text(f"Users ({len(self.controller.users)})", size=24),
            ft.Column([
                ft.ListTile(
                    title=ft.Text(user["name"]),
                    subtitle=ft.Text(user["email"])
                )
                for user in self.controller.users
            ])
        ])
```

---

## Navigation Elements

### App Bar

```python
class SettingsPage(FletXPage):
    def build_app_bar(self):
        """Override to create app bar"""
        return ft.AppBar(
            title=ft.Text("Settings"),
            center_title=True,
            actions=[
                ft.IconButton(ft.icons.HELP_OUTLINE),
                ft.PopupMenuButton([
                    ft.PopupMenuItem(text="Option 1"),
                    ft.PopupMenuItem(text="Option 2")
                ])
            ]
        )
    
    def build(self):
        return ft.Column([
            ft.Text("Settings content")
        ])
```

### Navigation Drawer

```python
class HomePage(FletXPage):
    def build_drawer(self):
        """Override to create drawer"""
        return ft.NavigationDrawer(
            controls=[
                ft.NavigationDrawerDestination(
                    label="Home",
                    icon=ft.icons.HOME
                ),
                ft.NavigationDrawerDestination(
                    label="Products",
                    icon=ft.icons.SHOPPING_BAG
                ),
                ft.NavigationDrawerDestination(
                    label="Settings",
                    icon=ft.icons.SETTINGS
                )
            ]
        )
    
    def build(self):
        return ft.Column([
            ft.ElevatedButton(
                "Open Drawer",
                on_click=lambda _: self.open_drawer()
            )
        ])
```

### Floating Action Button

```python
class TasksPage(FletXPage):
    def __init__(self):
        super().__init__()
        self.controller = TaskController()
    
    def build_floating_action_button(self):
        return ft.FloatingActionButton(
            icon=ft.icons.ADD,
            on_click=self._show_add_dialog
        )
    
    def _show_add_dialog(self, e):
        dialog = ft.AlertDialog(
            title=ft.Text("Add Task"),
            content=ft.TextField(label="Task name"),
            actions=[
                ft.TextButton("Cancel"),
                ft.TextButton("Add")
            ]
        )
        self.page_instance.dialog = dialog
        dialog.open = True
        self.page_instance.update()
    
    def build(self):
        return ft.Column([ft.Text("Your Tasks")])
```

### Bottom Sheet

```python
def open_filters(self, e):
    """Show filter options in bottom sheet"""
    sheet_content = ft.Column([
        ft.Text("Filters", size=20, weight="bold"),
        ft.Checkbox(label="Active only"),
        ft.Checkbox(label="Recent"),
        ft.ElevatedButton("Apply")
    ], spacing=15)
    
    self.open_bottom_sheet(sheet_content)
```

---

## Event Handling

### Window Events

```python
class ResponsivePage(FletXPage):
    def __init__(self):
        super().__init__()
        self.window_width = 0
        self.window_height = 0
    
    def on_init(self):
        # Listen to window resize
        self.on_resize(self._on_window_resize)
        
        # Listen to media changes (orientation)
        self.on_media_change(self._on_media_change)
        
        # Listen to brightness changes
        self.on_brigthness_change(self._on_brightness_change)
    
    def _on_window_resize(self, e):
        """When window is resized"""
        self.window_width = e.width
        self.window_height = e.height
        print(f"Window: {self.window_width}x{self.window_height}")
        self.refresh()
    
    def _on_media_change(self, e):
        """When orientation changes"""
        print(f"Media changed: {e.data}")
        self.refresh()
    
    def _on_brightness_change(self, e):
        """When system brightness changes"""
        print(f"Brightness changed")
    
    @obx
    def build(self):
        return ft.Text(f"{self.window_width}x{self.window_height}")
```

### Keyboard Events

```python
class SearchPage(FletXPage):
    def __init__(self):
        super().__init__(enable_keyboard_shortcuts=True)
        self.search_input = ft.TextField()
    
    def on_init(self):
        # Listen to all keyboard events
        self.on_keyboard(self._on_keyboard)
        
        # Or register specific shortcuts
        self.add_keyboard_shortcut("ctrl+f", self._focus_search, "Focus search")
        self.add_keyboard_shortcut("escape", self._clear_search, "Clear search")
    
    def _on_keyboard(self, e):
        """Handle any keyboard event"""
        if e.key == "Enter":
            self._do_search()
    
    def _focus_search(self):
        self.search_input.focus()
    
    def _clear_search(self):
        self.search_input.value = ""
        self.search_input.update()
    
    def _do_search(self):
        print(f"Searching for: {self.search_input.value}")
    
    def build(self):
        return ft.Column([
            self.search_input,
            ft.Text("Shortcuts: Ctrl+F to focus, Escape to clear")
        ])
```

### Scroll Events

```python
class InfiniteScrollPage(FletXPage):
    def __init__(self):
        super().__init__()
        self.list_view = ft.ListView()
    
    def on_init(self):
        self.on_scroll(self._on_scroll)
    
    def _on_scroll(self, e):
        """When user scrolls"""
        print(f"Scroll offset: {e.offset}")
        # Load more items when near bottom
        if e.offset > 0.8:  # 80% scrolled
            self._load_more_items()
    
    def _load_more_items(self):
        print("Loading more items...")
    
    def build(self):
        return ft.Column([
            self.list_view
        ])
```

---

## Keyboard Shortcuts

Make your app more productive with shortcuts:

```python
class EditorPage(FletXPage):
    def __init__(self):
        super().__init__(enable_keyboard_shortcuts=True)
        self.editor = ft.TextField(multiline=True, min_lines=10)
    
    def on_init(self):
        # Register shortcuts
        self.add_keyboard_shortcut("ctrl+s", self._save, "Save")
        self.add_keyboard_shortcut("ctrl+n", self._new, "New")
        self.add_keyboard_shortcut("ctrl+o", self._open, "Open")
        self.add_keyboard_shortcut("ctrl+z", self._undo, "Undo")
        self.add_keyboard_shortcut("ctrl+y", self._redo, "Redo")
    
    def _save(self):
        print("Saving...")
    
    def _new(self):
        self.editor.value = ""
        self.editor.update()
    
    def _open(self):
        print("Opening file...")
    
    def _undo(self):
        print("Undo...")
    
    def _redo(self):
        print("Redo...")
    
    def build(self):
        shortcuts = self.get_keyboard_shortcuts()
        shortcuts_text = "\n".join(
            [f"{k}: {v['description']}" for k, v in shortcuts.items()]
        )
        
        return ft.Column([
            ft.Text("Shortcuts:"),
            ft.Text(shortcuts_text, size=10),
            self.editor
        ])
```

---

## Gestures

Handle touch and mouse gestures:

```python
class GesturesPage(FletXPage):
    def __init__(self):
        super().__init__(enable_gestures=True)
    
    def on_init(self):
        # Handle tap
        self.on_tap(self._on_tap)
        
        # Handle long press
        self.on_long_press(self._on_long_press)
        
        # Handle scale/zoom
        self.on_scale(self._on_scale)
    
    def _on_tap(self, e):
        print(f"Tapped at {e.local_x}, {e.local_y}")
    
    def _on_long_press(self, e):
        print(f"Long pressed at {e.local_x}, {e.local_y}")
    
    def _on_scale(self, e):
        print(f"Scale: {e.scale}")
    
    def build(self):
        return ft.Column([
            ft.Text("Tap, long press, or scale me!")
        ])
```

---

## Dialogs and Alerts

```python
class DialogsPage(FletXPage):
    def build(self):
        return ft.Column([
            ft.ElevatedButton("Alert", on_click=self._show_alert),
            ft.ElevatedButton("Confirm", on_click=self._show_confirm),
            ft.ElevatedButton("Loader", on_click=self._show_loader),
            ft.ElevatedButton("Snackbar", on_click=self._show_snackbar)
        ])
    
    def _show_alert(self, e):
        dialog = ft.AlertDialog(
            title=ft.Text("Alert"),
            content=ft.Text("This is an alert message"),
            actions=[ft.TextButton("OK")]
        )
        self.page_instance.dialog = dialog
        dialog.open = True
        self.page_instance.update()
    
    def _show_confirm(self, e):
        dialog = ft.AlertDialog(
            title=ft.Text("Confirm?"),
            content=ft.Text("Are you sure?"),
            actions=[
                ft.TextButton("Cancel"),
                ft.TextButton("Yes", style=ft.ButtonStyle(color=ft.colors.RED))
            ]
        )
        self.page_instance.dialog = dialog
        dialog.open = True
        self.page_instance.update()
    
    def _show_loader(self, e):
        self.show_loader(ft.ProgressRing())
    
    def _show_snackbar(self, e):
        snack = ft.SnackBar(ft.Text("Operation completed!"))
        self.page_instance.snack_bar = snack
        snack.open = True
        self.page_instance.update()
```

---

## Effects and Side Effects

```python
class EffectsPage(FletXPage):
    def __init__(self):
        super().__init__()
        self.controller = MyController()
    
    def on_init(self):
        # Watch for changes
        self.watch(
            self.controller.username,
            self._on_username_change
        )
        
        # Watch multiple
        self.watch_multiple(
            [self.controller.email, self.controller.phone],
            self._on_contact_change
        )
        
        # Add effect with cleanup
        self.add_effect(
            self._setup_listener,
            cleanup_fn=self._cleanup_listener
        )
    
    def _on_username_change(self):
        print(f"Username changed to: {self.controller.username}")
    
    def _on_contact_change(self):
        print("Contact info changed")
    
    def _setup_listener(self):
        print("Setting up listener...")
    
    def _cleanup_listener(self):
        print("Cleaning up listener...")
    
    def build(self):
        return ft.Text("Effects demo")
```

---

## Page Configuration

```python
class StyledPage(FletXPage):
    def __init__(self):
        super().__init__(
            # Layout
            padding=20,
            bgcolor=ft.colors.SURFACE_VARIANT,
            
            # Styling
            border_radius=10,
            
            # Features
            enable_keyboard_shortcuts=True,
            enable_gestures=True,
            safe_area=True,
            
            # Lifecycle
            auto_dispose_controllers=True
        )
    
    def on_init(self):
        # Set page title
        self.set_title("My Page")
        
        # Set theme
        self.set_theme_mode(ft.ThemeMode.LIGHT)
    
    def build(self):
        return ft.Text("Styled page")
```

---

## Performance Monitoring

```python
class AnalyticsPage(FletXPage):
    def on_destroy(self):
        # Get performance stats
        stats = self.get_performance_stats()
        
        print(f"Render time: {stats['average_render_time']:.2f}ms")
        print(f"Updates: {stats['update_count']}")
        print(f"Controllers: {stats['controller_count']}")
    
    def build(self):
        return ft.Text("Performance tracked")
```

---

## Complete Real-World Example

```python
from fletx.core import FletXPage, FletXController
from fletx.decorators import obx
import flet as ft

class BookController(FletXController):
    def __init__(self):
        super().__init__()
        self.books = self.create_rx_list([])
        self.selected_book = self.create_rx_str("")
        self.filter_text = self.create_rx_str("")
    
    def load_books(self):
        self.set_loading(True)
        try:
            self.books.value = [
                {"id": 1, "title": "Python Guide", "author": "John Doe"},
                {"id": 2, "title": "Web Dev", "author": "Jane Smith"},
                {"id": 3, "title": "AI Basics", "author": "Bob Johnson"}
            ]
            self.emit_local("books_loaded", len(self.books))
        finally:
            self.set_loading(False)
    
    def select_book(self, book_id):
        book = next((b for b in self.books if b["id"] == book_id), None)
        if book:
            self.selected_book.value = book["title"]

class BooksPage(FletXPage):
    def __init__(self):
        super().__init__(padding=20)
        self.controller = BookController()
    
    def build_app_bar(self):
        return ft.AppBar(
            title=ft.Text("Books Library"),
            center_title=True
        )
    
    def on_init(self):
        self.controller.load_books()
        self.controller.on_local("books_loaded", self._on_loaded)
    
    def _on_loaded(self, event):
        print(f"Loaded {event.data} books")
    
    @obx
    def build(self):
        if self.controller.is_loading:
            return ft.Center(content=ft.ProgressRing())
        
        return ft.Column([
            ft.Text(f"Books ({len(self.controller.books)})", size=24),
            ft.ListView([
                ft.ListTile(
                    title=ft.Text(book["title"]),
                    subtitle=ft.Text(book["author"]),
                    on_click=lambda _, b=book: self.controller.select_book(b["id"])
                )
                for book in self.controller.books
            ]),
            ft.Divider(),
            ft.Text(
                f"Selected: {self.controller.selected_book if self.controller.selected_book else 'None'}"
            )
        ])
```

---

## Best Practices

### 1. Initialize in `on_init()`, not `__init__()`

```python
# ✅ Good
class MyPage(FletXPage):
    def on_init(self):
        # Page is now visible
        self.controller.load_data()

# ❌ Avoid
class MyPage(FletXPage):
    def __init__(self):
        # Page not visible yet!
        self.controller.load_data()
```

### 2. Clean Up in `on_destroy()`

```python
def on_destroy(self):
    # Cancel requests
    self.controller.cancel_all()
    
    # Close connections
    if hasattr(self, 'ws'):
        self.ws.close()
```

### 3. Use Controller Methods Correctly

```python
# ✅ Good - use create_rx_* for initialization
class MyController(FletXController):
    def __init__(self):
        super().__init__()
        self.count = self.create_rx_int(0)
        self.name = self.create_rx_str("")
        self.items = self.create_rx_list([])

# ✅ Good - use set_* methods for updates
self.controller.set_loading(True)
self.controller.set_error("Error message")

# ❌ Avoid - don't use RxInt/RxStr directly
self.controller.count = RxInt(0)  # Wrong!

# ❌ Avoid - don't set reactive properties directly
self.controller.is_loading = True  # Won't trigger updates
```

### 4. Keep Pages Focused

```python
# ✅ Good - one responsibility
class UserListPage(FletXPage):
    pass

# ❌ Avoid - too many responsibilities  
class AdminPage(FletXPage):
    # Shows users, analytics, settings, logs...
    pass
```

### 5. Use @obx for Reactive Methods

```python
# ✅ Good - method marked with @obx rebuilds automatically
@obx
def user_card(self):
    return ft.Card(content=ft.Text(self.controller.username))

# ❌ Avoid - regular method won't react to changes
def user_card(self):
    return ft.Card(content=ft.Text(self.controller.username))
```

---

## Summary

| Feature | Purpose |
|---------|---------|
| `build()` | Return the page UI |
| `on_init()` | Setup when page appears |
| `on_destroy()` | Cleanup when page disappears |
| `build_app_bar()` | Custom app bar |
| `build_drawer()` | Navigation drawer |
| `build_floating_action_button()` | FAB |
| `add_keyboard_shortcut()` | Register shortcut |
| `on_resize()` | Window resize event |
| `on_keyboard()` | Keyboard event |
| `on_scroll()` | Scroll event |
| `on_tap()` / `on_long_press()` / `on_scale()` | Gesture events |
| `page_instance` | Access Flet page |
| `refresh()` | Force UI update |
| `open_drawer()` / `close_drawer()` | Drawer control |
| `open_bottom_sheet()` | Show bottom sheet |
| `show_loader()` | Show loading dialog |
| `controller` | Business logic |
| `watch()` | React to state changes |
| `get_performance_stats()` | Performance info |

---

## Next Steps

- Learn about [Controllers](controllers.md) for managing state
- Explore [Routing](routing.md) to navigate between pages
- Understand [Dependency Injection](dependency-injection.md)
- Read about [State Management](state-management.md) with reactive variables
- Check [Decorators](decorators.md) for advanced features
