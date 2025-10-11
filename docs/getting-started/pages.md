#### Introduction

Pages are the heart of every FletX application — each one represents a screen or view that users can interact with.

In this guide, you’ll learn how to create, structure, and manage pages effectively using the FletXPage class.

We’ll start simple, then progressively explore lifecycle hooks, controllers, navigation, and best practices to help you build smooth, dynamic apps.

#### 1. Using Pages in 

#### What Are `Pages in FletX` ?

In a FletX application, a page represents a screen or view — similar to ft.Page in Flet, but with extra powers.

#### What is a `FletXPage`?
A FletX page is built with the `FletXPage` class, which extends `ft.Container` and adds advanced features such as:

Page lifecycle hooks (on_init, on_destroy)

Access to context and routing

Reactive updates from controllers

Page-level utilities (snackbars, loaders, dialogs, etc.)

Keyboard shortcuts and effects management

In short, a FletXPage lets you define what appears on screen and how it behaves within your app.FletX

#### A Simple “Hello Page” Example

Let’s start small!
Here’s a minimal page you can create with FletX:
``` python
import flet as ft
from fletx import FletXPage

class HelloPage(FletXPage):
    def build(self):
        return ft.Column([
            ft.Text("👋 Hello from FletX!"),
            ft.ElevatedButton("Click Me", on_click=self.say_hello)
        ])
    
    def say_hello(self, _):
        self.show_snackbar("Welcome to your first FletX page!")
```

This simple example shows:

How build() defines what’s visible on the page.

How a button triggers a page utility method (show_snackbar()).

#### Understanding the Page Lifecycle

Each FletXPage goes through several stages from creation to destruction.
Knowing these helps you manage setup, cleanup, and reactivity properly.

### | State          | What It Means                                       |
    | -------------- | --------------------------------------------------- |
    | `INITIALIZING` | The page is being set up (not visible yet).         |
    | `MOUNTED`      | The page is now part of the UI tree.                |
    | `ACTIVE`       | The page is visible and ready for user interaction. |
    | `INACTIVE`     | The page is still mounted but not currently active. |
    | `UNMOUNTING`   | The page is being removed.                          |
    | `DISPOSED`     | The page has been destroyed and cleaned up.         |

You can use lifecycle hooks to react to these stages.

#### Lifecycle Hook Methods
`on_init(self)`

Runs before the page becomes visible.
You typically use this to:

Fetch or prepare data

Subscribe to controller signals

Set up event listeners or effects

`on_destroy(self)`

Runs right before the page is destroyed.
Use it to:

Unsubscribe from listeners

Stop background tasks

Release resources

#### Example:
``` python
def on_init(self):
    print("Page initialized!")

def on_destroy(self):
    print("Cleaning up resources...")
```

#### Defining the Page UI with build()

Every page must define a build() method that returns the layout.

``` python
def build(self):
    return ft.Column([
        ft.Text("My First Page", size=24),
        ft.ElevatedButton("Show Dialog", on_click=self.show_welcome)
    ])
```
This method should be pure and fast — it’s called automatically whenever the page updates or rerenders.

#### Adding Interactivity and Side Effects

FletX pages often listen to controller state or reactive values.
You can subscribe to them easily:
``` python
self.controller.is_loading.listen(self.show_loader)
self.controller.error_message.listen(self.show_snackbar)
```
These subscriptions are automatically cleaned up when the page is destroyed, so you don’t need to unsubscribe manually.

#### Adding Keyboard Shortcuts

FletX allows you to register page-specific keyboard shortcuts to make navigation and actions faster.

``` python
self.add_keyboard_shortcut("ctrl+r", self.refresh, "Reload data")
self.add_keyboard_shortcut("ctrl+h", self.go_home, "Go to home")
```
Shortcuts are active only when the page is mounted or active.

#### Working with Controllers

Controllers manage logic and data, while pages focus on UI.
A page can easily connect to a controller and react to its state.

#### Example:

``` python
from fletx import FletX, FletXPage
from controllers.home_controller import HomeController

class HomePage(FletXPage):
    def __init__(self):
        super().__init__(enable_keyboard_shortcuts=True)
        self.controller = FletX.put(HomeController(), 'home_controller')

    def on_init(self):
        self.controller.load_data()
        self.controller.is_loading.listen(self.show_loader)
        self.controller.error_message.listen(self.show_snackbar)

    def build(self):
        return ft.Column([
            ft.Text("🏠 Home Page", size=22),
            ft.ElevatedButton("Refresh", on_click=self.refresh),
        ])

    def refresh(self, _):
        self.controller.load_data()
```
Here:

FletX.put() injects and stores the controller.

The page listens to its reactive states.

The page updates automatically when controller data changes.

#### Navigating Between Pages

You can navigate between pages using the router object:

``` python
self.router.go("/about")
```
Routes must be registered in your app configuration so FletX knows which FletXPage to render.

#### Complete Example – A Counter Page

Here’s a small but complete example tying everything together:

``` python
import flet as ft
from fletx import FletXPage, FletX

class CounterController:
    def __init__(self):
        self.count = FletX.signal(0)

    def increment(self):
        self.count.value += 1

class CounterPage(FletXPage):
    def __init__(self):
        super().__init__(padding=20, enable_keyboard_shortcuts=True)
        self.controller = CounterController()
        self.controller.count.listen(self.update_ui)
        self.add_keyboard_shortcut("ctrl+i", self.increment, "Increase count")

    def build(self):
        self.text = ft.Text(f"Count: {self.controller.count.value}", size=24)
        return ft.Column([
            self.text,
            ft.ElevatedButton("Increment", on_click=self.increment)
        ])

    def increment(self, _=None):
        self.controller.increment()
        self.show_snackbar("Count increased!")

    def update_ui(self, _):
        self.text.value = f"Count: {self.controller.count.value}"
        self.update()
```
This example demonstrates:

A simple reactive state (count)

Listening for changes

Updating the UI dynamically

Adding keyboard shortcuts

#### Useful Page Utilities
#### | Method                    | Description                                 |
     | ------------------------- | ------------------------------------------- |
     | `show_snackbar()`         | Displays a temporary message at the bottom. |
     | `show_dialog()`           | Opens a dialog box.                         |
     | `show_loader()`           | Shows or hides a loading indicator.         |
     | `show_bottom_sheet()`     | Displays a bottom sheet.                    |
     | `add_keyboard_shortcut()` | Adds contextual keyboard shortcuts.         |

You can use these utilities anywhere inside your page for smooth UX.

#### Best Practices

✅ Keep your UI lightweight — move logic to controllers.
✅ Use lifecycle hooks for setup and cleanup.
✅ Avoid side effects directly in build().
✅ Reuse components across pages for consistency.
✅ Keep each page focused on one major responsibility.

#### Next Steps

- Learn about [Routing in FletX](routing.md)
- Explore [Dependency Injection in FletX](guides/dependency-injection.md)
- Understand the [Architecture Overview](architecture.md)

<!-- # Using Pages in 
### 🔷 What is a `FletXPage`?

A `FletXPage` represents **a single screen or view** in a FletX application. It is the fundamental building block of the user interface and typically corresponds to a page the user navigates to.

Each page is designed to:

* Define its UI layout using a `build()` method
* Respond to lifecycle events (`on_init`, `on_destroy`)
* React to state changes and side effects
* Add contextual keyboard shortcuts
* Interact with controllers using reactive data listening

---

### 🔁 Page Lifecycle in FletX

FletXPages go through a **structured lifecycle**, with each state representing a phase in the page’s existence. Understanding these states is crucial to managing page behavior correctly.

| State          | Description                                                                     |
| -------------- | ------------------------------------------------------------------------------- |
| `INITIALIZING` | The page is being initialized but not yet visible                               |
| `MOUNTED`      | The page has been mounted in the UI, but might not be active                    |
| `ACTIVE`       | The page is fully visible and has focus (can respond to input)                  |
| `INACTIVE`     | The page is still mounted but currently inactive (e.g., another page is active) |
| `UNMOUNTING`   | The page is about to be removed from the UI                                     |
| `DISPOSED`     | The page has been destroyed and its resources cleaned up                        |

---

### 🧩 Lifecycle Hook Methods

FletXPages provide lifecycle hooks that allow you to define behaviors when the page appears or disappears.

#### `on_init(self)`

This method is called **before the page becomes visible**. You should use it to:

* Initialize or fetch data
* Subscribe to signals from controllers
* Set up any one-time effects or listeners

#### `on_destroy(self)`

This method is called **just before the page is unmounted and destroyed**. It’s useful to:

* Unsubscribe from observers
* Cancel background tasks
* Clear resources

These methods give you control over the page's initialization and teardown logic.

---

### 🛠️ The `build()` Method – Defining the UI

Every `FletXPage` must define a `build()` method. This method returns the actual content of the page using Flet UI elements.

```python
def build(self):
    return ft.Column([
        ft.Text("Page Title"),
        ft.ElevatedButton("Click Me", on_click=self.handle_click)
    ])
```

This method is automatically called when the page is rendered. It should be fast, pure, and declarative.

---

### 🎯 Handling Side Effects with `EffectManager`

FletX provides a built-in effect manager to help you manage **reactive side effects**. These are actions triggered by changes in observable data or controller state.

You can add effects using listeners:

```python
# React to loading state
self.controller.is_loading.listen(self.show_loader)

# React to controller readiness
self.controller.is_ready.listen(self.load_data)
```

These effects are **automatically cleaned up** when the page is destroyed, making them safe and maintainable.

---

### ⌨️ Adding Keyboard Shortcuts

You can enable contextual **keyboard shortcuts** on a FletXPage by passing `enable_keyboard_shortcuts=True` in the constructor.

```python
self.add_keyboard_shortcut("ctrl+r", self.refresh, "Refresh the page")
self.add_keyboard_shortcut("ctrl+h", self.go_home, "Navigate home")
```

> ⚠️ Shortcuts are only active when the page is in `MOUNTED` or `ACTIVE` state.

This feature improves productivity and accessibility for power users.

---

### 🔗 Interacting with Controllers

A `FletXPage` can work with controllers to handle complex logic or manage data. Pages can:

* Observe reactive properties from the controller
* Listen to loading or error states
* Call controller methods to fetch or mutate data

```python
# Subscribe to reactive controller states
self.controller = HomeController()
self.controller.is_loading.listen(self.show_loader)
self.controller.error_message.listen(self.show_error)
```

This ensures your page stays in sync with the application logic and state.

---

### ✅ Complete Example of a `FletXPage`

```python
class HomePage(FletXPage):
    def __init__(self):
        super().__init__(
            padding=20,
            bgcolor=ft.colors.BLUE_GREY_50,
            border_radius=10,
            enable_keyboard_shortcuts=True
        )

        
        # Register keyboard shortcuts
        self.add_keyboard_shortcut("ctrl+r", self.refresh, "Refresh the page")
        self.add_keyboard_shortcut("ctrl+h", lambda: navigate('/home'), "Go to home page")

        # Inject HomeController
        self.controller = FletX.put(HomeController(),'home_conroller')
        # Connect to controller and listen for state changes
        self.controller.is_loading.listen(self.show_loader)

    def on_init(self):
        # Trigger actions when the page is initialized
        self.controller.load_data()
        self.controller.error_message.listen(self.show_snackbar)

    def on_destroy(self):
        print("HomePage is being destroyed...")

    def build(self):
        return ft.Column([
            ft.Text("Welcome to FletX!", size=24),
            ft.ElevatedButton("Show Dialog", on_click=self.show_sample_dialog),
            ft.ElevatedButton("Show Snackbar", on_click=self.show_snackbar)
        ])

    def refresh(self, _=None):
        self.controller.load_data()

    def go_home(self, _=None):
        self.router.go("/home")

    def show_sample_dialog(self, _=None):
        ...

    def show_snackbar(self, _=None):
        ...

    def show_loader(self, is_loading):
        if is_loading:
            ...
```

---

### 📌 Summary Table

| Feature                   | Purpose                                          |
| ------------------------- | ------------------------------------------------ |
| `on_init` / `on_destroy`  | Handle page initialization and cleanup           |
| `build()`                 | Define the UI layout using Flet widgets          |
| `add_keyboard_shortcut()` | Add contextual keyboard actions                  |
| `controller.listen(...)`  | React to observable changes from controllers     |
| `EffectManager`           | Manage side effects in a structured and safe way |

---

## 🧠 Next Steps

* Explore the [Routing System](routing.md)
* Learn about the [Architecture](architecture.md)
* Dive into [dependency injection](guides/dependency-injection.md) -->
