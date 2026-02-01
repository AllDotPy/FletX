# Architecture

**TL;DR** — FletX apps separate concerns into Pages (UI), Controllers (logic + state), and Services (reusable utilities). Data flows in one direction: user action → controller → state update → UI re-render.

## Problem

Without clear architecture, your Flet app quickly becomes a mess:

- UI code and business logic are tangled together
- State lives in random places (widget properties, global variables, controller fields)
- Reusing logic across pages is hard
- Testing is painful because everything is interdependent

## Solution

FletX provides a **modular, reactive architecture** inspired by separation of concerns and dependency injection. It gives you a clear place for everything:

- **Pages** = declarative UI
- **Controllers** = business logic + reactive state
- **Services** = shared utilities (API, database, caching)

## Progression: understanding the flow

We'll go from the simplest case (no logic) → single controller → multiple controllers → services. All examples are real code you can run.

---

## 1. A page with no logic (UI only)

**When:** Simple display-only pages, like a splash screen or about page.

```python
from fletx.core import FletXPage
import flet as ft

class AboutPage(FletXPage):
    def build(self):
        return ft.Column([
            ft.Text("About FletX", size=30, weight="bold"),
            ft.Text("FletX is a framework for building structured Flet apps."),
        ])
```

**That's it.** No state, no logic. Just UI.

---

## 2. A page with a simple controller

**When:** The page needs state (counters, form fields, toggles).

```python
from fletx.core import FletXController, RxInt
from fletx.decorators.widgets import obx
import flet as ft

class CounterController(FletXController):
    def __init__(self):
        self.count = RxInt(0)
        super().__init__()
    
    def increment(self):
        self.count.value += 1
    
    def decrement(self):
        self.count.value -= 1
```

**Explanation:** The controller holds reactive state (`self.count`). Methods like `increment()` modify it. FletX tracks reads of `self.count`, so any widget that depends on it will rebuild automatically.

```python
from fletx.core import FletXPage

class CounterPage(FletXPage):
    ctrl = CounterController()
    
    def build(self):
        return ft.Column([
            self._counter_text(),
            ft.Row([
                ft.ElevatedButton("-", on_click=lambda _: self.ctrl.decrement()),
                ft.ElevatedButton("+", on_click=lambda _: self.ctrl.increment()),
            ])
        ])
    
    @obx
    def _counter_text(self):
        # Rebuilds when self.ctrl.count changes
        return ft.Text(
            value=f"Count: {self.ctrl.count.value}",
            size=40,
            weight="bold"
        )
```

**Key insight:** The `@obx` decorator wraps a builder function. When you read `self.ctrl.count` inside it, FletX remembers that dependency. When `count` changes, the builder runs again and the widget updates.

---

## 3. Controller with business logic

**When:** Page needs to compute values, fetch data, or handle complex logic.

```python
from fletx.core import FletXController, RxStr, RxList
from fletx.decorators.reactive import reactive_debounce, reactive_memo
from fletx.core.state import Computed

class SearchController(FletXController):
    def __init__(self):
        self.query = RxStr("")
        self.all_items = ["Apple", "Apricot", "Avocado", "Banana", "Blueberry"]
        self.results = RxList([])
        super().__init__()
    
    @reactive_memo(maxsize=32)
    def _filter_items(self, q: str):
        # Pure computation: filter items matching q
        # FletX caches this automatically
        if not q:
            return self.all_items
        return [item for item in self.all_items if q.lower() in item.lower()]
    
    @reactive_debounce(0.3)
    def search(self, q: RxStr):
        # Executes 300ms after user stops typing
        self.results.value = self._filter_items(q.value)
    
    def clear_search(self):
        self.query.value = ""
        self.results.value = []
```

**Explanation:**

- `@reactive_memo` caches expensive computations.
- `@reactive_debounce` waits for the user to pause before searching.
- The controller encapsulates all the logic; the page is just UI.

```python
from fletx.core import FletXPage
from fletx.decorators.widgets import obx
import flet as ft

class SearchPage(FletXPage):
    ctrl = SearchController()
    
    def build(self):
        return ft.Column([
            ft.TextField(
                label="Search",
                on_change=lambda e: (
                    self.ctrl.query.value = e.control.value,
                    self.ctrl.search(self.ctrl.query)
                )[0]
            ),
            self._results_list(),
        ])
    
    @obx
    def _results_list(self):
        # Rebuilds when self.ctrl.results changes
        items = self.ctrl.results.value
        if not items:
            return ft.Text("No results")
        return ft.Column([
            ft.Text(item) for item in items
        ])
```

---

## 4. Multiple pages sharing a controller

**When:** Multiple pages need access to the same state (e.g., user profile, app settings).

```python
from fletx import FletX
from fletx.core import FletXController, RxDict, RxBool

class AppController(FletXController):
    """Shared app-wide state"""
    def __init__(self):
        self.user = RxDict({})
        self.is_logged_in = RxBool(False)
        super().__init__()
    
    def login(self, email, password):
        # Validate and set user
        self.user.value = {"email": email, "name": "John"}
        self.is_logged_in.value = True
    
    def logout(self):
        self.user.value = {}
        self.is_logged_in.value = False

# Register a global instance of the controller
FletX.put(AppController, tag='app_ctrl')
```

**Use it from multiple pages:**

```python
from fletx import FletX
from fletx.core import FletXPage

class ProfilePage(FletXPage):
    # Get the global iinstance of AppController 
    app_ctrl = FletX.find(AppController, tag='app_ctrl')
    
    def build(self):
        return ft.Column([
            self._profile_view(),
            ft.ElevatedButton("Logout", on_click=lambda _: self.app_ctrl.logout())
        ])
    
    @obx
    def _profile_view(self):
        if not self.app_ctrl.is_logged_in.value:
            return ft.Text("Not logged in")
        user = self.app_ctrl.user.value
        return ft.Text(f"Welcome, {user.get('name', 'Guest')}")
```

```python
from fletx import FletX
class SettingsPage(FletXPage):
    # Get the global instance of AppController
    app_ctrl = FletX.put(AppController, tag='app_ctrl')
    
    def build(self):
        return ft.Column([
            ft.Text(f"Logged in as: {self.app_ctrl.user.value.get('email', 'N/A')}")
        ])
```

**Key:** Both pages share the same `AppController` instance. When one page changes `is_logged_in`, all pages see the change.

---

## 5. Services for reusable logic

**When:** You need to share utilities across multiple controllers (API calls, database, caching, file I/O).

```python
from fletx.core import FletXService, RxDict, RxBool

class UserService(FletXService):
    """Manages user data"""
    def __init__(self):
        super().__init__()
        self.user = RxDict({})
        self.is_loading = RxBool(False)
    
    def fetch_user(self, user_id: int):
        """Simulate API call"""
        self.is_loading.value = True
        try:
            # In real code: response = requests.get(f"/api/users/{user_id}")
            self.user.value = {
                "id": user_id,
                "name": "John Doe",
                "email": "john@example.com"
            }
        finally:
            self.is_loading.value = False
```

**Use service from a controller:**

```python
from fletx.core import FletXController

class ProfileController(FletXController):
    def __init__(self):
        # Find the service from FletX's dependency injection
        self.user_service = FletX.find(UserService)
        super().__init__()
    
    def load_profile(self, user_id: int):
        self.user_service.fetch_user(user_id)
```

**Use service from a page:**

```python
from fletx.core import FletXPage
from fletx import FletX

class ProfilePage(FletXPage):
    def build(self):
        user_service = FletX.find(UserService)
        
        return ft.Column([
            self._profile_view(user_service),
        ])
    
    @obx
    def _profile_view(self, user_service):
        if user_service.is_loading.value:
            return ft.ProgressRing()
        user = user_service.user.value
        return ft.Column([
            ft.Text(f"Name: {user.get('name', 'N/A')}"),
            ft.Text(f"Email: {user.get('email', 'N/A')}")
        ])
```

---

## 6. The full picture: app with routing

Let's combine pages, controllers, services, and routing.

**Project structure:**

```
app/
  __init__.py
  main.py
  app.py
  pages/
    __init__.py
    home.py
    profile.py
    settings.py
  controllers/
    __init__.py
    home_controller.py
    app_controller.py
  services/
    __init__.py
    user_service.py
    api_service.py
```

**app/app.py — App setup with routing:**

```python
from fletx.app import FletXApp
from fletx.navigation import router_config
from app.services.user_service import UserService
from app.pages.home import HomePage
from app.pages.profile import ProfilePage
from app.pages.settings import SettingsPage

# Register services
FletX.register(UserService)

# Register routes
router_config.add_routes([
    {"path": "/", "component": HomePage},
    {"path": "/profile/:user_id", "component": ProfilePage},
    {"path": "/settings", "component": SettingsPage},
])

app = FletXApp(title="MyApp")
```

**app/main.py — Entry point:**

```python
from app.app import app

if __name__ == "__main__":
    app.run()
```

**app/pages/home.py:**

```python
from fletx.core import FletXPage
from app.controllers.home_controller import HomeController
import flet as ft

class HomePage(FletXPage):
    ctrl = HomeController()
    
    def build(self):
        return ft.Column([
            ft.Text("Home", size=30, weight="bold"),
            ft.ElevatedButton("Go to Profile", on_click=lambda _: self.page.go("/profile/123"))
        ])
```

**app/controllers/home_controller.py:**

```python
from fletx.core import FletXController, RxInt

class HomeController(FletXController):
    def __init__(self):
        self.visit_count = RxInt(0)
        super().__init__()
    
    def record_visit(self):
        self.visit_count.value += 1
```

**app/services/user_service.py:**

```python
from fletx.core import FletXService, RxDict

class UserService(FletXService):
    def __init__(self):
        super().__init__()
        self.user = RxDict({})
    
    def fetch_user(self, user_id: int):
        self.user.value = {"id": user_id, "name": f"User {user_id}"}
```

---

## Data flow diagram

```
┌─────────────────────────────────────────────────────────┐
│                   User Interaction                       │
│            (button click, text input, etc)               │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  Page.build()                            │
│          (renders UI from current state)                 │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Event Handler in Page                       │
│         (on_click, on_change, on_focus, etc)            │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│          Controller Method (or Service)                  │
│    (implements business logic, updates state)           │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│          State Update (RxInt, RxStr, etc)               │
│          (triggers dependent watchers)                   │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│      Reactive Watchers (@obx, listeners)                │
│        (detect the state change)                         │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│            UI Rebuilds (only changed parts)             │
│                   Page.build() again                     │
└─────────────────────────────────────────────────────────┘
```

---

## Best practices (summary)

| Principle | What to do |
|-----------|-----------|
| Single responsibility | One controller per page (usually). One service per concern (users, auth, API). |
| Separate logic from UI | Put business logic in controllers/services. Pages just render and call methods. |
| Use reactive state | All mutable state should be `Rx*` (RxInt, RxStr, RxList, RxDict). Never plain Python variables. |
| Inject dependencies | Use `FletX.find()` to get services, not global imports. Makes testing easy. |
| Keep methods small | Controller methods should be focused. If a method is too long, break it into smaller methods. |
| Clean up on dispose | If your service opens a connection (socket, file, etc), close it in `on_dispose()`. |
| Use `@obx` for builders | Wrap reactive builders with `@obx` so FletX tracks dependencies automatically. |
| Avoid `lambda:` in build | Use `@obx` decorated methods instead. Cleaner, easier to understand. |

---

## Common patterns

### Pattern 1: Read-only page (no controller needed)

```python
class AboutPage(FletXPage):
    def build(self):
        return ft.Column([ft.Text("About")])
```

### Pattern 2: Single reactive value

```python
class TogglePage(FletXPage):
    is_dark = RxBool(False)
    
    def build(self):
        return ft.Column([
            self._toggle(),
        ])
    
    @obx
    def _toggle(self):
        return ft.Switch(
            value=self.is_dark.value,
            on_change=lambda e: setattr(self.is_dark, 'value', e.control.value)
        )
```

### Pattern 3: Page + Controller + Service

```python
from fletx import FletX

class UserPage(FletXPage):
    ctrl = UserController()
    
    def build(self):
        return ft.Column([self._user_card()])
    
    @obx
    def _user_card(self):
        user_service = FletX.find(UserService)
        return ft.Text(user_service.user.value.get("name", "Unknown"))
```

---

## Troubleshooting

**Q: My widget doesn't update when state changes.**

A: Make sure you're using `@obx` and reading the reactive variable inside the builder. FletX needs to detect the read to track the dependency.

**Q: I have multiple pages sharing state, but changes don't sync.**

A: Register the controller/service with `FletX.register()` at app startup, and use `FletX.find()` to retrieve it. Don't create new instances.

**Q: My controller is getting too big.**

A: Break it into multiple smaller controllers or move logic into services. Each should have one clear responsibility.

**Q: How do I pass data between pages?**

A: Use route parameters (`/profile/:user_id`) and access them in `self.route_info.params`. Or use a shared service/controller.

---

## References

- [Controllers](controllers.md) — deep dive into FletXController
- [State Management](state-management.md) — understand reactive primitives (RxInt, RxList, Computed)
- [Reactive Decorators](decorators.md) — control when/how code executes (debounce, throttle, memo)
- [Pages](pages.md) — detailed FletXPage reference
- [Routing](routing.md) — navigation and route configuration

---

**Next:** Pick a pattern above that matches your use case. Start with pattern 1 or 2, then graduate to 3 as you need more features.
