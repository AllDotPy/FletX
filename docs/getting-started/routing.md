# 📍 Routing

FletX features a modern, declarative routing system inspired by Angular and Vue Router. It enables developers to organize their application navigation cleanly—supporting **static and dynamic routes**, **nested paths**, **modular routing**, **page transitions**, **route guards**, and **middleware**.

FletX also provides utility functions for programmatic navigation, such as `navigate()` and `go_back()`.

---

!!! tip "How to read routing diagrams"

    - Boxes represent **router steps** or **components**.
    - Arrows indicate **navigation flow** (URL → match → page → controller → UI).
    - Prefer using the Architecture guide’s diagrams as a quick mental model.

[← Back to Architecture](architecture.md)

## 🧭 Basic Routing

Use the global `router_config` to define your app's navigation structure:

```python
from fletx.navigation import router_config

# Define simple static routes
router_config.add_routes([
    {"path": "/", "component": HomePage},          # Main entry point
    {"path": "/settings", "component": SettingsPage}  # Static settings page
])
```

> 🧠 These are the core pages accessible via `/` and `/settings`. The `component` can be any valid FletX view class.

---

## 🧩 Dynamic Routing with Parameters

FletX allows dynamic segments using `:param` and `*param` (wildcard):

```python
router_config.add_routes([
    {
        "path": "/users/:id",  # :id is dynamic (e.g. /users/42)
        "component": UserDetailPage
    },
    {
        "path": "/products/*category",  # Matches /products/electronics/phones
        "component": ProductsPage
    }
])
```

> 📦 `route.params` gives access to dynamic values extracted from the URL.

---

## 🪜 Nested Routing (Hierarchical)

You can structure your routes with a parent-child hierarchy using `children`:

```python
from fletx.navigation import RouteDefinition

# Admin layout with nested pages
router_config.add_route(
    path="/admin",
    component=AdminLayoutPage,  # Base layout
    children=[
        RouteDefinition(path="/dashboard", component=AdminDashboardPage),
        RouteDefinition(path="/users", component=AdminUsersPage)
    ]
)
```

> 🧱 This allows child components to render inside the parent layout, just like `<router-outlet>` in Angular.

---

## 🧱 Modular Routing with `ModuleRouter`

For large apps, splitting routing logic by modules keeps your code maintainable.

### 🔹 Example 1: Manual `ModuleRouter` registration

```python
admin_module = ModuleRouter()
admin_module.name = "admin"

admin_module.add_routes([
    {"path": "/", "component": AdminHomePage},
    {"path": "/users", "component": AdminUsersPage},
    {"path": "/settings", "component": AdminSettingsPage}
])

# Mount admin module under the /admin path
router_config.add_module_routes("/admin", admin_module)
```

> 🚀 This creates modular routes like `/admin/users`.

---

### 🔹 Example 2: Angular-style with `@register_router`

```python
# Define the routes for the Admin module
admin_routes = [
    {"path": "/", "component": AdminHomePage},
    {"path": "/users", "component": AdminUsersPage},
    {"path": "/settings", "component": AdminSettingsPage}
]

# Register the admin router
@register_router
class AdminRouter(ModuleRouter):
    name = 'Admin'
    base_path = '/admin'
    is_root = False
    routes = admin_routes
    sub_routers = []

# Declare the root router and include AdminRouter
@register_router
class MyAppRouter(ModuleRouter):
    name = 'MyAppRouter'
    base_path = '/'
    is_root = True
    routes = []
    sub_routers = [AdminRouter]
```

> 🧩 This structure is powerful for enterprise-scale applications and module separation.

---

## 🎭 Page Transitions

FletX supports animated transitions between pages using `RouteTransition`:

```python
from fletx.navigation import RouteTransition, TransitionType

routes = [
    {
        "path": "/login",
        "component": LoginPage,
        "meta": {
            "transition": RouteTransition(
                transition_type=TransitionType.ZOOM_IN,  # Zoom animation
                duration=350  # In milliseconds
            )
        }
    },
    {
        "path": "/dashboard",
        "component": DashboardHomePage,
        "meta": {
            "transition": RouteTransition(
                transition_type=TransitionType.FLIP_HORIZONTAL,
                duration=350
            )
        }
    }
]
```

> 🌈 Page transitions help enhance user experience and feedback during navigation.

---

## 🛡️ Route Guards & Middleware

FletX supports **guards** (for route protection) and **middleware** (for navigation hooks).

### 🔐 Auth Guard Example

```python
from fletx.navigation import RouteGuard

class AuthGuard(RouteGuard):
    """Blocks access if the user is not authenticated."""
    
    def __init__(self, auth_service, login_route="/login"):
        self.auth_service = auth_service
        self.login_route = login_route

    def can_activate(self, route_info):
        return self.auth_service()

    def redirect_to(self, route_info):
        return f"{self.login_route}?returnUrl={route_info.path}"
```

> ✅ `can_activate()` checks before entering a route.
> 🔁 `redirect_to()` defines where to redirect if access is denied.

---

### 📊 Middleware Example (e.g., loading state)

```python
from fletx.navigation import RouteMiddleware

class LoadingMiddleware(RouteMiddleware):
    """Shows a loading indicator during navigation."""

    def __init__(self, loading_service):
        self.loading_service = loading_service

    def before_navigation(self, from_route, to_route):
        self.loading_service.show_loading(f"Loading {to_route.path}...")

    def after_navigation(self, route_info):
        self.loading_service.hide_loading()

    def on_navigation_error(self, error, route_info):
        self.loading_service.hide_loading()
```

> 💡 Middleware can be used for analytics, logging, or animations.

---

### 🧪 Using Guards and Middleware in routes

```python
router_config.add_route(
    path="/profile",
    component=ProfilePage,
    guards=[AuthGuard()],                # Check if user is authenticated
    middleware=[LoadingMiddleware()]    # Show loading screen during transition
)
```

---

## 🔁 Programmatic Navigation

Use `navigate()` to switch routes and `go_back()` to return to the previous one.

```python
from fletx.navigation import navigate, go_back

# Navigate to a static or dynamic page
navigate("/home")
navigate("/users/23")

# Pass additional data
navigate("/dashboard", data={"user_id": 23})

# Replace the current page or reset navigation stack
navigate("/dashboard", replace=True, clear_history=True)

# Navigate back (like a browser back button)
go_back()
```

> 🔀 Useful for navigation after login, form submissions, etc.

---

## Summary

| Feature            | Description                          |
| ------------------ | ------------------------------------ |
| `add_routes()`     | Define simple or dynamic routes      |
| `ModuleRouter`     | Organize routes by feature/module    |
| `@register_router` | Angular-style modular declaration    |
| `RouteGuard`       | Protect pages (e.g., login required) |
| `RouteMiddleware`  | Run code before/after navigation     |
| `RouteTransition`  | Add animation to route changes       |
| `navigate()`       | Programmatic navigation              |
| `go_back()`        | Navigate to the previous route       |

---

## 🧠 Next Steps

* Dive into [dependency injection](dependency-injection.md)
* Explore the [services](services.md)
* Learn about the [Architecture](architecture.md)