<!-- # 📘 **FletX Controllers** – Complete and Thorough Guide -->

## Introduction

**Controllers** in `FletX` serve as the core coordinating component of your application. They function as an intelligent coordinator that sits between what users see — the UI — and what the application actually does — the business logic. **Controllers**  are where the thinking happens in your FletX application.


The `FletXController` differs fundamentally from a traditional UI component. While pages and widgets handle display and user interaction, the controller manages:

* **Reactive UI components**: Flet widgets that automatically update as the state changes.
* **Business logic**: The rules and operations that define app behaviour.
* **External services**: Communication with APIs, databases, and services.
* **Inter component communication**: How different parts of the app communicate with one another.

## Why Controllers?

When you build modern applications, you quickly encounter a fundamental challenge: how to organise code so that it remains manageable as the application grows. Consider a real world scenario in which you develop an application with multiple interconnected features:
* A login screen that handles user authentication,
* A user dashboard that displays personalised information, and
* A shared to do system that enables multiple users to collaborate.

Without proper organisation, these features become entangled in a web of dependencies, making the code difficult to understand, test, and modify.

`FletXController` addresses this complexity by applying the separation of concerns principle. Instead of mixing UI logic with business logic, controllers create clear boundaries between different types of functionality:

### Without Controllers – Everything Mixed Together

```python
class MyPage(ft.View):
    def __init__(self):
        super().__init__()
        self.username = ""
        self.is_loading = False
        self.error_message = ""

    def build(self):
        username_field = ft.TextField(value=self.username)
        error_text = ft.Text(self.error_message, color="red")
        loading_indicator = ft.ProgressBar(visible=self.is_loading)

        def on_username_change(e):
            self.username = e.control.value
            print(f"Username changed to: {self.username}")
            if len(self.username) < 3:
                self.error_message = "Username too short"
            else:
                self.error_message = ""
            self.page.update()

        username_field.on_change = on_username_change
        return ft.Column([
            username_field,
            error_text,
            loading_indicator,
        ])
```
* State and validation live inside the UI class.
* Event handlers mix UI updates, business logic, and state management.
* Manual calls to `self.page.update()` scattered throughout.

### With Controllers – Clean Separation

```python
class MyController(FletXController):
    def __init__(self):
        super().__init__()

        # Reactive states
        self.username = self.create_rx_str("")
        self.is_loading = self.create_rx_bool(False)
        self.error_message = self.create_rx_str("")

        # Reactive effect
        self.use_effect(self.handle_username_change, deps=[self.username])

    def handle_username_change(self):
        print(f"Username changed to: {self.username.value}")

    def on_ready(self):
        print("Controller is ready!")
```
* All state (`username`, `is_loading`, `error_message`) resides in the Controller.
* Reactive effect enforces logic when `username` changes.
* UI components bind directly to these reactive variables, with no manual updates.

## How Controllers acts as the Bridge Between UI and Business Logic

A `FletXController` sits between your UI (FletXPage) and the application’s business logic and state. It receives user actions, applies business rules, updates reactive state, and enables the UI to update automatically.

### 1. Define the Controller
```python
class CounterController(FletXController):
    def __init__(self):
        super().__init__()
        # Application state
        self.count = self.create_rx_int(0)
        self.is_loading = self.create_rx_bool(False)

    def increment(self):
        # Business logic
        self.is_loading.value = True
        self.count.value += 1
        self.is_loading.value = False
```

* `count`: reactive integer for UI display.
* `increment`: encapsulates business logic and loading state.

### 2. Build the UI
```python
class CounterPage(FletXPage):
    def __init__(self):
        super().__init__()
        self.ctrl = CounterController()

    def build(self):
        return ft.Column([
            # Display reactive state
            ft.Text(f"Count: {self.ctrl.count.value}"),
            # Loading indicator bound to controller
            ft.ProgressBar(visible=self.ctrl.is_loading.value),
            # User action invokes controller method
            ft.ElevatedButton(
                "Increment",
                on_click=lambda e: self.ctrl.increment()
            )
        ])
```

* UI reads `self.ctrl.count.value` and `self.ctrl.is_loading.value`.
* UI writes by calling `self.ctrl.increment()`.

### 3. Reactive Updates

User clicks “Increment” → UI calls `ctrl.increment()`.

Controller logic runs → updates count and `is_loading`.

Reactive state changes → UI automatically re-renders without manual updates.

`FletX` automatically tracks dependencies between reactive variables and UI elements, so you never need to manually call `update()`.

This pattern ensures:
* **Separation of concerns**: UI code remains simple, focusing on layout.
* **Centralized logic**: Controller contains all state changes and business rules.
* **Automatic UI synchronization**: Reactive variables drive UI updates seamlessly.

## Controller Examples in FletX

### 1. Simple CounterController

This example shows a Controller with a single reactive variable that tracks a count.
```python
class CounterController(FletXController):
    def __init__(self):
        super().__init__()
        # Reactive state: the current count
        self.count = self.create_rx_int(0)

    def increment(self):
        # Business logic: increase count by one
        self.count.value += 1
```
```python
class CounterPage(FletXPage):
    def __init__(self):
        super().__init__()
        self.ctrl = CounterController()

    def build(self):
        return ft.Column([
            ft.Text(f"Count: {self.ctrl.count.value}"),
            ft.ElevatedButton(
                "Increment",
                on_click=lambda e: self.ctrl.increment()
            )
        ])
```
* The Controller holds `count` and an `increment` method.
* The UI displays `count.value` and calls `increment()` on button click.
* Reactive binding ensures the displayed count updates automatically.

### 2. Advanced Controller with Multiple States and Async Logic
This Controller manages username, loading state, and login errors, and performs an asynchronous login operation.
```python
class AuthController(FletXController):
    def __init__(self):
        super().__init__()
        self.username = self.create_rx_str("")
        self.password = self.create_rx_str("")
        self.is_loading = self.create_rx_bool(False)
        self.login_error = self.create_rx_str("")

    async def login(self):
        # Validate input
        if not self.username.value or not self.password.value:
            self.login_error.value = "Username and password required"
            return

        # Show loading indicator
        self.is_loading.value = True
        self.login_error.value = ""

        try:
            # Async business logic
            result = await auth_service.authenticate(
                self.username.value, self.password.value
            )
            if not result.success:
                self.login_error.value = result.message
        except Exception as e:
            self.login_error.value = str(e)
        finally:
            # Hide loading indicator
            self.is_loading.value = False
```

```python
class LoginPage(FletXPage):
    def __init__(self):
        super().__init__()
        self.ctrl = AuthController()

    def build(self):
        return ft.Column([
            ft.TextField(
                label="Username",
                value=self.ctrl.username.value,
                on_change=lambda e: setattr(self.ctrl.username, "value", e.control.value)
            ),
            ft.TextField(
                label="Password",
                password=True,
                value=self.ctrl.password.value,
                on_change=lambda e: setattr(self.ctrl.password, "value", e.control.value)
            ),
            ft.ElevatedButton(
                "Login",
                on_click=lambda e: self.ctrl.login()
            ),
            ft.ProgressBar(visible=self.ctrl.is_loading.value),
            ft.Text(self.ctrl.login_error.value, color="red")
        ])
```

* Reactive variables track user input, loading, and errors.
* The `login` method runs asynchronously, updates state, and handles errors.
* The UI binds to these states, showing loading and error messages automatically.

### 3. Communication Between Controllers
Here, an AuthController notifies a UserController when login succeeds. The UserController then loads user details.
```python
class AuthController(FletXController):
    def __init__(self):
        super().__init__()
        self.is_authenticated = self.create_rx_bool(False)
        self.user_id = self.create_rx_int(None)

    async def login(self, username, password):
        result = await auth_service.authenticate(username, password)
        if result.success:
            self.is_authenticated.value = True
            self.user_id.value = result.user_id
            # Emit a global event for other controllers
            self.emit_global("user_logged_in", {"user_id": self.user_id.value})

class UserController(FletXController):
    def __init__(self):
        super().__init__()
        self.profile = self.create_rx_dict({})
        # Listen for the login event
        self.listen_reactive_global("user_logged_in").listen(self.load_profile)

    async def load_profile(self, event):
        user_id = event.data["user_id"]
        profile_data = await user_service.fetch_profile(user_id)
        self.profile.value = profile_data
```
```python
class AppPage(FletXPage):
    def __init__(self):
        super().__init__()
        self.auth = AuthController()
        self.user = UserController()

    def build(self):
        if not self.auth.is_authenticated.value:
            return LoginPage()
        else:
            return UserProfilePage(profile=self.user.profile.value)
```
* `AuthController.login()` sets authentication state and emits `"user_logged_in"`.
* `UserController` listens to that event and runs `load_profile`, updating `profile`.
* The main page switches between login and profile views based on `is_authenticated`.

## Controller Features

### Reactive Variables

#### Definition
Reactive variables are special values that automatically update every element that depends on them.  
When a reactive variable changes, all UI components that reference it are refreshed instantly.

#### When to Use
Use reactive variables when an application’s display must update immediately in response to:
- User input  
- Clicks or actions  
- Background data changes  

#### Examples
- Displaying the current score in a game as it changes  
- Updating the shopping cart total as items are added  
- Reflecting a user’s input in a live preview


```python
# Create reactive values
username = controller.create_rx_str("John")
age = controller.create_rx_int(30)
is_logged_in = controller.create_rx_bool(False)
tasks = controller.create_rx_list([])
profile = controller.create_rx_dict({"email": "john@example.com"})
```

### Computed Values

#### Definition
A computed value is a value that the system derives from other values. The value is refreshed whenever any of the source values change.

#### When to Use
Apply a computed value when a result must reflect changes in underlying information without requiring manual recalculation or reconstruction.

### Examples
 - Combine a name and age to display “John (25 years old)”.
 - Calculate the total bill in a food order from item prices and quantities.
 - Show the number of remaining tasks by counting items with an unfinished status.

```python
full_info = controller.create_computed(
    lambda: f"{username.value} ({age.value} years old)"
)
```

### Reactive Effects

#### Definition
Reactive Effects are instructions that run automatically whenever a specific value changes — for example, setting an automatic reminder each time something in the app is updated. They let the app respond to state changes instantly without requiring manual triggers.

#### When to Use
Apply Reactive Effects when the app must do an action automatically as soon as a particular piece of state changes, such as:
- Show a message
- Start a process
- Save or sync data

#### Examples
- Fetching additional data when a user selects a different tab
- Displaying a warning if the input becomes too long
- Syncing changes to a server when a user edits a form

```python
controller.use_effect(
    lambda: print(f"Username is now: {username.value}"),
    deps=[username]
)
```

### Local and Global Event Bus

#### Definition
An event bus is a built‑in messaging system that lets components communicate with each other—either within a page (local) or across the entire application (global). It provides a shared channel where components can send events and listen for events without a direct connection.

#### When to Use
Use the event bus when one component must signal another that something has occurred, for example:
- Announcing that a user has logged in or logged out
- Broadcasting that new data has been added
- Notifying other components of state or action changes

#### Examples
- Notifying all sections of the app when a user logs out  
- Showing a notification popup when data is saved elsewhere  
- Refreshing a dashboard when a new message arrives

#### Emit Events

```python
controller.emit_local("user_updated", {"name": "Alice"})
controller.emit_global("theme_changed", {"dark_mode": True})
```
#### Listen to Events

```python
events = controller.listen_reactive_local("user_updated")
events.listen(lambda: print(f"User events: {len(events.value)}"))

# You can access:
print(controller.event_bus.event_history.value)
print(controller.event_bus.last_event.value)

```
### Local and Global Context

#### Definition
The Context system is a way to store and manage shared information so that any part of the app can access or react to it — like a set of shared notes that every component can read from or update. It provides a single source of truth for commonly used data across different parts of the application.

#### When to Use
Use the Context system whenever you need to share data (for example, user information, app settings, or preferences) between multiple screens or features — so you do not have to pass it manually through each component.

#### Examples
- Keeping track of who’s logged in throughout the app  
- Sharing the current app theme (light or dark) between all pages  
- Passing language preferences to every screen

#### Set Context

```python
controller.set_context("current_user", {"id": 1, "name": "John"})

```
#### Get Context (reactively or not)

```python
# Reactive version
rx_user = controller.get_context_reactive("current_user")
rx_user.listen(lambda: print(f"User updated: {rx_user.value}"))

# Reactive check
has_user = controller.has_context_reactive("current_user")
has_user.listen(lambda: print("User exists" if has_user.value else "No user"))

# Non-reactive version
user = controller.get_context("current_user")

```

## Controller Lifecycle Methods in FletX

FletX Controllers provide built-in hooks that let you run code at specific points in a Controller’s lifecycle.  
Understanding these hooks helps you initialize resources, bind listeners, and clean up gracefully.

| **Method** | **When It Runs** |
|-------------|------------------|
| **`on_initialized()`** | Immediately after the Controller object is created |
| **`on_ready()`** | After the UI components associated with this Controller are mounted and ready |
| **`on_disposed()`** | When the Controller is being destroyed or unmounted |
| **`on_close()`** <br><sub>(Alias for `on_disposed` in older `FletX` releases)</sub> | Just before the Controller is removed from memory |


#### `on_initialized()`

**Use Cases**
- Set default values  
- Configure dependencies (services, repositories)  
- Initialize non-reactive properties  

**Example**
```python
class MyController(FletXController):
    def on_initialized(self):
        # Called during instantiation, before any UI is mounted
        self.logger = setup_logging()             # Configure logger
        self.default_theme = "light"              # Non-reactive default
        self.load_config_from_disk()
```
#### `on_ready()`

**Use Cases**
- Bind reactive listeners to UI events  
- Trigger initial data loads that require UI context  
- Start animations or focus input fields  

**Example**
```python
class UserController(FletXController):
    def on_ready(self):
        # UI is now visible; safe to fetch and display data
        self.load_user_profile()                  # Populate reactive state
        self.username_input.focus()               # Set initial focus
        self.username.listen(self.validate_name)  # Reactive effect
```
#### `on_disposed()`

**Use Cases**
- Cancel pending network or database requests  
- Dispose of timers, subscriptions, or event listeners  
- Release resources (file handles, sockets)  

**Example**
```python
class StreamingController(FletXController):
    def on_disposed(self):
        # Called during cleanup, before object is garbage-collected
        self.stream_subscription.cancel()         # Stop live updates
        self.timer.stop()                         # Cancel periodic tasks
        self.logger.info("StreamingController disposed")
```
#### `on_close()`
<sub>Alias for `on_disposed` in older `FletX` releases</sub>

**Use Cases**
- Persist unsaved changes  
- Notify other Controllers or services of shutdown  

**Example**
```python
class FormController(FletXController):
    def on_close(self):
        if self.has_unsaved_changes:
            save_to_disk(self.form_data)         # Persist draft data
        self.emit_global("form_closed", {})       # Notify others
```
## Controller Lifecycle

The following steps occur when a FletX controller runs:

#### 1. Creation → `on_initialized()`
The controller starts for the first time. Use this method to set default values or load basic settings.

#### 2. UI Ready → `on_ready()`
The application screen becomes visible. Load data, connect buttons, or set focus to input fields.

#### 3. User Actions → Normal controller methods & reactive effects
Users interact with the app. The controller responds to clicks, inputs, and updates the screen.

#### 4. Closing → `on_disposed()` / `on_close()`
The controller is about to close or be removed. Stop timers, cancel requests, and save any unsaved data.

## FletX Application Architecture Guidelines

#### 1. Keep Logic Out of the UI Layer
- **Separate concerns** so that UI code remains focused on presentation.
- **Bind UI elements** directly to reactive variables; do not embed logic in event handlers.
- **Delegate validation**, data processing, and side effects to controllers.
- **Avoid** calling APIs or performing complex computations inside `FletXPage.build()`.

#### 2. Use Controllers for Testability and Scalability
- **Encapsulate** business rules and state in controllers to enable unit testing.
- **Write tests** that instantiate controllers, manipulate reactive variables, and verify state changes without involving the UI.
- **Mock external services** (e.g., API clients, databases) in controller tests to simulate success and failure scenarios.
- **Extend controllers** or create new ones as the application grows—leave UI code unchanged.

#### 3. Organize Controllers in Large Applications
- **Use a clear, feature-based directory structure**, such as: auth/, user/, dashboard/,todo/
- **Name controllers** to reflect their responsibilities (e.g., `LoginController`, `SettingsController`, `NotificationsController`).
- **Register shared/global controllers** in a root module (like `AppPage`) so that all pages can retrieve them via dependency injection.
- **Keep controllers focused** on a single responsibility; if one grows too large, split it into smaller, cohesive ones.

**Implementing these practices** leads to a clean architecture, robust testing, and a maintainable codebase for FletX applications.


## Next Steps

* Explore [Page (Views)](pages.md)
* Learn about the [Architecture](architecture.md)
* Dive into [dependency injection](guides/dependency-injection.md)
