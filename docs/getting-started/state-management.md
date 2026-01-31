# State Management

> **TL;DR**: FletX provides reactive variables (`RxInt`, `RxStr`, `RxBool`, `RxList`, `RxDict`) that automatically notify observers when they change. Watch them with `.listen()`, compute derived values with `create_computed()`, and use `@obx` decorator to rebuild UI components automatically. No manual `update()` calls needed.

---

## What is State Management?

**State** is the data your app depends on at any moment - a user's profile, the list of todos, whether a modal is open, API loading status, etc.

**State Management** means organizing, storing, and updating that data in a way that:

- Keeps it consistent and predictable
- Makes it easy to update
- Automatically syncs related UI and logic
- Prevents bugs from scattered, manual updates

FletX makes state management **reactive** - when state changes, everything depending on it automatically updates.

---

## Why Reactive State?

**Manual State - Scattered Updates:**

```python
class TodoPage(FletXPage):
    def __init__(self):
        super().__init__()
        self.todos = []  # Plain Python list
    
    def add_todo(self, title):
        self.todos.append({"title": title, "done": False})
        # Manual update needed everywhere
        self._refresh_todo_list()
        self._update_count()
        self._save_to_db()
        self.page_instance.update()
    
    def _refresh_todo_list(self):
        # Manually rebuild UI
        pass
    
    def _update_count(self):
        # Manually update count
        pass
    
    def _save_to_db(self):
        # Manually persist
        pass
    
    def build(self):
        # State is mixed with UI
        return ft.Column([
            ft.Text(f"Todos: {len(self.todos)}"),
            ft.Column([ft.Text(t["title"]) for t in self.todos])
        ])
```

**Problems:**

- State updates scattered everywhere
- Easy to miss an update
- Manual refresh calls
- Bugs from inconsistent state

**Reactive State - Automatic Sync:**

```python
class TodoController(FletXController):
    def __init__(self):
        super().__init__()
        self.todos = self.create_rx_list([])
        
        # Computed: auto-updates when todos change
        self.count = self.create_computed(lambda: len(self.todos))
    
    def add_todo(self, title):
        self.todos.append({"title": title, "done": False})
        # Everything updates automatically!

class TodoPage(FletXPage):
    def __init__(self):
        super().__init__()
        self.controller = TodoController()
    
    @obx
    def build(self):
        # UI rebuilds automatically when todos changes
        return ft.Column([
            ft.Text(f"Todos: {self.controller.count}"),  # Auto-updates
            ft.Column([ft.Text(t["title"]) for t in self.controller.todos])
        ])
```

**Benefits:**

- ✅ Single source of truth
- ✅ Automatic UI updates
- ✅ No manual refresh calls
- ✅ Fewer bugs
- ✅ Easy to test

---

## Your First Reactive Variable

### Step 1: Create a Reactive Variable

```python
from fletx.core import FletXController

class CounterController(FletXController):
    def __init__(self):
        super().__init__()
        # Create a reactive integer
        self.count = self.create_rx_int(0)
```

### Step 2: Use and Update It

```python
# Get the value
current_count = self.count.value

# Set a new value
self.count.value = 5
# Or self.count.set(5)

# Use type-specific methods
self.count.increment()  # count += 1
self.count.decrement()  # count -= 1
```

### Step 3: Watch for Changes

```python
def on_ready(self):
    # Call function when count changes
    self.count.listen(self._on_count_change)

def _on_count_change(self):
    print(f"Count is now: {self.count.value}")
```

### Step 4: Use in UI with `@obx`

```python
class CounterPage(FletXPage):
    @obx
    def build(self):
        return ft.Column([
            ft.Text(self.controller.count),  # Auto-updates
            ft.ElevatedButton("+", on_click=lambda _: self.controller.count.increment())
        ])
```

Done! 🎉

---

## Reactive Types

### RxInt - Reactive Integer

```python
class MyController(FletXController):
    def __init__(self):
        super().__init__()
        self.age = self.create_rx_int(30)
    
    def have_birthday(self):
        self.age.increment()
    
    def set_age(self, new_age):
        self.age.value = new_age
```

**Methods:**

- `increment(step=1)` - Add to value
- `decrement(step=1)` - Subtract from value
- `value` - Get/set the current value
- `set(new_value)` - Set a new value
- `listen(callback)` - Watch for changes

### RxStr - Reactive String

```python
class UserController(FletXController):
    def __init__(self):
        super().__init__()
        self.username = self.create_rx_str("")
        self.email = self.create_rx_str("")
    
    def update_username(self, new_username):
        self.username.value = new_username
```

**Methods:**

- `append(text)` - Add text to the string
- `clear()` - Empty the string
- `value` - Get/set the current value
- `listen(callback)` - Watch for changes

### RxBool - Reactive Boolean

```python
class ThemeController(FletXController):
    def __init__(self):
        super().__init__()
        self.is_dark_mode = self.create_rx_bool(False)
    
    def toggle_theme(self):
        self.is_dark_mode.toggle()
```

**Methods:**

- `toggle()` - Flip between true/false
- `value` - Get/set the current value
- `listen(callback)` - Watch for changes

### RxList - Reactive List

```python
class ShoppingController(FletXController):
    def __init__(self):
        super().__init__()
        self.items = self.create_rx_list([])
    
    def add_item(self, item):
        self.items.append(item)
    
    def remove_item(self, item):
        self.items.remove(item)
    
    def clear_cart(self):
        self.items.clear()
    
    def get_item(self, index):
        return self.items[index]
```

**Methods:**

- `append(item)` - Add item
- `remove(item)` - Remove item
- `clear()` - Remove all items
- `pop(index=-1)` - Remove and return item
- `extend(list)` - Add multiple items
- `__len__()` - Get length
- `__getitem__(index)` - Access by index
- `__setitem__(index, value)` - Update by index
- `listen(callback)` - Watch for changes

### RxDict - Reactive Dictionary

```python
class ConfigController(FletXController):
    def __init__(self):
        super().__init__()
        self.settings = self.create_rx_dict({
            "theme": "light",
            "language": "en"
        })
    
    def update_theme(self, theme):
        self.settings["theme"] = theme
    
    def get_language(self):
        return self.settings.get("language", "en")
```

**Methods:**

- `__setitem__(key, value)` - Set value
- `__getitem__(key)` - Get value
- `__delitem__(key)` - Delete key
- `get(key, default)` - Get with default
- `update(dict)` - Merge with dict
- `clear()` - Remove all items
- `listen(callback)` - Watch for changes

### Reactive[T] - Generic Reactive

```python
from fletx.core import Reactive

class UserModel:
    def __init__(self, name, email):
        self.name = name
        self.email = email

class UserController(FletXController):
    def __init__(self):
        super().__init__()
        # Generic reactive for any object
        self.user = self.create_reactive(UserModel("John", "john@example.com"))
    
    def update_user(self, user):
        self.user.value = user
```

---

## Listening to Changes

### Basic Listener

```python
class DataController(FletXController):
    def __init__(self):
        super().__init__()
        self.data = self.create_rx_str("")
    
    def on_ready(self):
        # Call function whenever data changes
        self.data.listen(self._on_data_change)
    
    def _on_data_change(self):
        print(f"Data changed: {self.data.value}")
```

### Stopping Listeners

```python
def on_ready(self):
    # listen() returns an Observer
    observer = self.data.listen(self._on_data_change)
    
    # Later, dispose to stop listening
    observer.dispose()
```

### Multiple Listeners

```python
def on_ready(self):
    self.count.listen(self._log_count)
    self.count.listen(self._update_ui)
    self.count.listen(self._save_to_db)
    
    # All three are called when count changes
```

---

## Computed Properties

Computed properties are **derived values** that automatically update when their dependencies change:

```python
class PriceController(FletXController):
    def __init__(self):
        super().__init__()
        self.price = self.create_rx_int(100)
        self.quantity = self.create_rx_int(2)
        self.tax_rate = self.create_rx_int(10)
        
        # Computed: subtotal = price * quantity
        self.subtotal = self.create_computed(
            lambda: self.price.value * self.quantity.value
        )
        
        # Computed: tax = subtotal * tax_rate / 100
        self.tax = self.create_computed(
            lambda: self.subtotal.value * self.tax_rate.value / 100
        )
        
        # Computed: total = subtotal + tax
        self.total = self.create_computed(
            lambda: self.subtotal.value + self.tax.value
        )
    
    def on_ready(self):
        # Listen to computed values
        self.total.listen(self._on_total_change)
    
    def _on_total_change(self):
        print(f"Total: {self.total.value}")
```

**How it works:**

1. Computed automatically detects dependencies (price, quantity, tax_rate)
2. When any dependency changes, computed is recalculated
3. Listeners are notified of the new value
4. UI components with `@obx` automatically rebuild

**Benefits:**

- No manual recalculation
- No stale values
- Efficient - only recalculates when needed
- Composable - computed can depend on other computed values

---

## Observers and Cleanup

Each listener is an **Observer** with a lifecycle:

```python
class WebsocketController(FletXController):
    def __init__(self):
        super().__init__()
        self.connected = self.create_rx_bool(False)
        self.observer = None
    
    def on_ready(self):
        # Create observer
        self.observer = self.connected.listen(self._on_connected_change)
    
    def _on_connected_change(self):
        if self.connected.value:
            self._connect_websocket()
        else:
            self._disconnect_websocket()
    
    def _connect_websocket(self):
        print("Connecting...")
    
    def _disconnect_websocket(self):
        print("Disconnecting...")
    
    def on_disposed(self):
        # Cleanup: stop listening
        if self.observer:
            self.observer.dispose()
```

---

## Reactivity in UI

### Using `@obx` Decorator

The `@obx` decorator makes a method reactive - it rebuilds automatically when its reactive dependencies change:

```python
from fletx.decorators import obx

class TodoPage(FletXPage):
    def __init__(self):
        super().__init__()
        self.controller = TodoController()
    
    @obx
    def todo_item_widget(self, todo):
        """This rebuilds when reactive values in the controller change"""
        return ft.Card(
            content=ft.Container(
                content=ft.Text(todo["title"]),
                padding=10
            )
        )
    
    @obx
    def build(self):
        """Main UI rebuilds automatically when todos or count changes"""
        return ft.Column([
            ft.Text(
                f"Count: {self.controller.count}",  # Auto-updates
                size=24,
                weight="bold"
            ),
            ft.ListView([
                self.todo_item_widget(todo)
                for todo in self.controller.todos  # Auto-updates
            ])
        ])
```

**How it works:**

1. `@obx` wraps the method
2. When the method runs, it tracks reactive variables used
3. If any reactive variable changes, the method is called again
4. UI is automatically rebuilt with new values

### Without `@obx` - Manual Updates

```python
# ❌ Without @obx - need manual updates
def build(self):
    def on_count_change():
        count_text.value = str(self.controller.count.value)
        self.page_instance.update()
    
    self.controller.count.listen(on_count_change)
    
    count_text = ft.Text(str(self.controller.count.value))
    return count_text

# ✅ With @obx - automatic!
@obx
def build(self):
    return ft.Text(str(self.controller.count.value))
```

---

## Complete Real-World Example

```python
# controller.py

from fletx.core import FletXController

class ShoppingController(FletXController):
    def __init__(self):
        super().__init__()
        self.items = self.create_rx_list([])
        self.tax_rate = self.create_rx_int(10)
        
        # Computed subtotal
        self.subtotal = self.create_computed(
            lambda: sum([item["price"] * item["quantity"] 
                        for item in self.items.value])
        )
        
        # Computed tax
        self.tax = self.create_computed(
            lambda: self.subtotal.value * self.tax_rate.value / 100
        )
        
        # Computed total
        self.total = self.create_computed(
            lambda: self.subtotal.value + self.tax.value
        )
        
        # Computed item count
        self.item_count = self.create_computed(
            lambda: sum([item["quantity"] for item in self.items.value])
        )
    
    def add_item(self, name, price):
        self.items.append({
            "id": len(self.items) + 1,
            "name": name,
            "price": price,
            "quantity": 1
        })
        self.emit_local("item_added", name)
    
    def update_quantity(self, item_id, quantity):
        for item in self.items.value:
            if item["id"] == item_id:
                item["quantity"] = quantity
                # Trigger update
                self.items.value = list(self.items.value)
                break
    
    def remove_item(self, item_id):
        self.items.value = [item for item in self.items if item["id"] != item_id]
    
    def clear_cart(self):
        self.items.clear()

```

```python
# Page.py

from fletx.core import FletXPage
from fletx.decorators import obx
import flet as ft

class ShoppingPage(FletXPage):
    def __init__(self):
        super().__init__(padding=20)
        self.controller = ShoppingController()
    
    def on_init(self):
        self.controller.on_local("item_added", self._on_item_added)
    
    def _on_item_added(self, event):
        print(f"Added: {event.data}")
    
    @obx
    def price_summary(self):
        """Price summary that rebuilds when totals change"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("Subtotal:"),
                        ft.Text(f"${self.controller.subtotal.value:.2f}", weight="bold")
                    ]),
                    ft.Row([
                        ft.Text("Tax (10%):"),
                        ft.Text(f"${self.controller.tax.value:.2f}", weight="bold")
                    ]),
                    ft.Divider(),
                    ft.Row([
                        ft.Text("Total:"),
                        ft.Text(f"${self.controller.total.value:.2f}", size=18, weight="bold")
                    ])
                ], spacing=10),
                padding=15
            )
        )
    
    @obx
    def build(self):
        return ft.Column([
            # Header
            ft.Text(
                f"Shopping Cart ({self.controller.item_count} items)",
                size=24,
                weight="bold"
            ),
            
            # Items list
            ft.ListView([
                ft.Card(
                    content=ft.Container(
                        content=ft.Row([
                            ft.Column([
                                ft.Text(item["name"], weight="bold"),
                                ft.Text(f"${item['price']}", size=12, color=ft.colors.GREY)
                            ], expand=True),
                            ft.Row([
                                ft.IconButton(
                                    ft.icons.REMOVE,
                                    on_click=lambda _, id=item["id"]: 
                                        self.controller.update_quantity(id, max(1, item["quantity"]-1))
                                ),
                                ft.Text(str(item["quantity"])),
                                ft.IconButton(
                                    ft.icons.ADD,
                                    on_click=lambda _, id=item["id"]: 
                                        self.controller.update_quantity(id, item["quantity"]+1)
                                ),
                                ft.IconButton(
                                    ft.icons.DELETE,
                                    on_click=lambda _, id=item["id"]: 
                                        self.controller.remove_item(id)
                                )
                            ])
                        ]),
                        padding=10
                    )
                )
                for item in self.controller.items
            ], spacing=5),
            
            # Price summary
            self.price_summary(),
            
            # Action buttons
            ft.Row([
                ft.ElevatedButton(
                    "Add Item",
                    on_click=lambda _: self.controller.add_item("Product", 99.99)
                ),
                ft.OutlinedButton(
                    "Clear Cart",
                    on_click=lambda _: self.controller.clear_cart()
                )
            ], spacing=10)
        ], scroll=ft.ScrollMode.AUTO)
```

---

## Best Practices

### 1. Use Type-Specific Creators

```python
# ✅ Good - use create_rx_* methods
self.count = self.create_rx_int(0)
self.name = self.create_rx_str("")
self.items = self.create_rx_list([])

# ❌ Avoid - importing types directly
from fletx.core.state import RxInt
self.count = RxInt(0)  # Not tracked by controller lifecycle
```

### 2. Use `@obx` for Reactive Methods

```python
# ✅ Good - method rebuilds when dependencies change
@obx
def user_card(self):
    return ft.Card(content=ft.Text(self.controller.username.value))

# ❌ Avoid - regular method won't react
def user_card(self):
    return ft.Card(content=ft.Text(self.controller.username.value))
```

### 3. Use Computed for Derived Values

```python
# ✅ Good - computed auto-updates
self.full_name = self.create_computed(
    lambda: f"{self.first.value} {self.last.value}"
)

# ❌ Avoid - manual updates
self.full_name = self.create_rx_str("")
self.first.listen(lambda: self.full_name.value = f"{self.first.value} {self.last.value}")
```

### 4. Listen at Right Time

```python
# ✅ Good - setup listeners in on_ready
def on_ready(self):
    self.count.listen(self._on_count_change)

# ❌ Avoid - setup in __init__
def __init__(self):
    self.count.listen(self._on_count_change)  # Might not work
```

### 5. Clean Up Listeners

```python
# ✅ Good - dispose observers
def on_ready(self):
    self.observer = self.data.listen(self._on_data)

def on_disposed(self):
    if self.observer:
        self.observer.dispose()

# ❌ Avoid - leave listeners hanging
def on_ready(self):
    self.data.listen(self._on_data)  # Memory leak potential
```

### 6. Keep UI Methods Pure

```python
# ✅ Good - no side effects in @obx methods
@obx
def build(self):
    return ft.Text(self.controller.value)

# ❌ Avoid - side effects in @obx
@obx
def build(self):
    save_to_db(self.controller.value)  # Don't do this!
    return ft.Text(self.controller.value)
```

---

## Summary

| Concept | Purpose |
|---------|---------|
| **RxInt** | Reactive integer with increment/decrement |
| **RxStr** | Reactive string with append/clear |
| **RxBool** | Reactive boolean with toggle |
| **RxList** | Reactive list with append/remove/pop |
| **RxDict** | Reactive dictionary with get/update |
| **Reactive[T]** | Generic reactive value |
| **Computed** | Derived value that auto-updates |
| **Observer** | Listens to changes, can be disposed |
| **@obx** | Decorator that rebuilds on changes |
| **.listen()** | Watch for changes |
| **.value** | Get/set current value |
| **create_computed()** | Create computed property |
| **create_rx_int()** | Create reactive int |
| **create_rx_str()** | Create reactive string |
| **create_rx_bool()** | Create reactive boolean |
| **create_rx_list()** | Create reactive list |
| **create_rx_dict()** | Create reactive dictionary |

---

## Next Steps

- Learn how to use state in [Controllers](controllers.md)
- Explore [Pages](pages.md) with reactive UI
- Understand [Dependency Injection](dependency-injection.md) for sharing state
- Check [Decorators](decorators.md) for advanced reactivity with `@obx`
- Read about [Routing](routing.md) to manage state across pages
