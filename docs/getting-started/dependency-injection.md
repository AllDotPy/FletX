# Dependency Injection

> **TL;DR**: Dependency Injection (DI) is a way to share instances of services across your app without passing them through function parameters. FletX provides a simple container where you register services once and retrieve them anywhere using `FletX.put()` and `FletX.find()`.

---

## What is Dependency Injection?

Dependency Injection is a design pattern that solves a common problem: **How do I share data between different parts of my app without global variables?**

### The Problem Without DI

Imagine you have a service that manages user authentication:

```python
class AuthService:
    def __init__(self):
        self.user = None
    
    def login(self, username):
        self.user = username
    
    def is_logged_in(self):
        return self.user is not None
```

Without DI, you'd have to create this service and pass it everywhere:

```python
# You have to create it once
auth_service = AuthService()

# Then pass it to every page and controller that needs it
class HomePage(FletXPage):
    def __init__(self, auth_service):  # Passed as parameter
        self.auth_service = auth_service
    
    def build(self):
        return ft.Text("Home Page")

class ProfilePage(FletXPage):
    def __init__(self, auth_service):  # Passed as parameter
        self.auth_service = auth_service
    
    def build(self):
        return ft.Text("Profile Page")

# When creating pages, you have to pass it manually
home_page = HomePage(auth_service)
profile_page = ProfilePage(auth_service)
```

This gets tedious quickly, especially with many services and pages.

### The DI Solution

With Dependency Injection, you **register** your service once in a central container, and any part of your app can **retrieve** it:

```python
from fletx import FletX

# Register once at app startup
FletX.put(AuthService())

# Retrieve anywhere you need it
class HomePage(FletXPage):
    def build(self):
        # Just grab it from the container
        auth = FletX.find(AuthService)
        return ft.Text(f"Welcome {auth.user}")

class ProfilePage(FletXPage):
    def build(self):
        # Same service instance, no parameters needed
        auth = FletX.find(AuthService)
        return ft.Text(f"Profile for {auth.user}")
```

**Key benefits:**
- No parameter passing chains
- Services are created once (singleton pattern)
- Any page or controller can access them
- Easier to test and maintain

---

## Your First Service

Let's create a simple service and register it:

### Step 1: Create the Service

```python
class CounterService:
    def __init__(self):
        self.count = 0
    
    def increment(self):
        self.count += 1
    
    def get_count(self):
        return self.count
```

### Step 2: Register at Startup

Register the service when your app starts (usually in `main.py`):

```python
from fletx import FletX, FletXApp
from services.counter_service import CounterService

# Register the service in the DI container
FletX.put(CounterService())

# Now run your app
app = FletXApp()
app.run()
```

### Step 3: Use the Service Anywhere

Now any page or controller can retrieve and use the service:

```python
import flet as ft
from fletx.core import FletXPage
from fletx import FletX
from services.counter_service import CounterService

class CounterPage(FletXPage):
    def build(self):
        # Get the service from the DI container
        counter_service = FletX.find(CounterService)
        
        def on_increment(_):
            counter_service.increment()
            # In a real app, you'd trigger a page rebuild here
            # This is simplified for demonstration
        
        return ft.Column([
            ft.Text(f"Count: {counter_service.get_count()}"),
            ft.ElevatedButton("Increment", on_click=on_increment)
        ])
```

---

## Managing Multiple Services

As your app grows, you'll have many services: authentication, database, settings, notifications, etc.

### Organizing Your Services

Create a separate file to register all your services:

```python
# services/__init__.py
from fletx import FletX
from .auth_service import AuthService
from .counter_service import CounterService
from .settings_service import SettingsService

def register_services():
    """Register all app services in the DI container"""
    FletX.put(AuthService())
    FletX.put(CounterService())
    FletX.put(SettingsService())
```

Then call it from your main app:

```python
# main.py
from fletx import FletXApp
from services import register_services

# Register all services
register_services()

# Run the app
app = FletXApp()
app.run()
```

### Accessing Services in Different Contexts

**In Pages:**

```python
class SettingsPage(FletXPage):
    def build(self):
        settings = FletX.find(SettingsService)
        auth = FletX.find(AuthService)
        
        return ft.Column([
            ft.Text(f"Theme: {settings.theme}"),
            ft.Text(f"User: {auth.user}")
        ])
```

**In Controllers:**

```python
from fletx.core import FletXController
from fletx import FletX

class ProductController(FletXController):
    def __init__(self):
        super().__init__()
        self.auth = FletX.find(AuthService)
        self.db = FletX.find(DatabaseService)
    
    def get_user_products(self):
        return self.db.get_products(self.auth.user)
```

**In Services (Services can depend on other services):**

```python
class OrderService:
    def __init__(self):
        # Get dependencies from the container
        self.auth = FletX.find(AuthService)
        self.db = FletX.find(DatabaseService)
        self.payment = FletX.find(PaymentService)
    
    def create_order(self, product_id, quantity):
        user = self.auth.user
        # Use injected dependencies...
        self.db.save_order(user, product_id, quantity)
```

---

## Advanced: Using Tags for Multiple Instances

Sometimes you need multiple instances of the same service with different configurations. Use tags:

```python
# Register multiple instances with different tags
FletX.put(DatabaseService(host="localhost"), tag="local")
FletX.put(DatabaseService(host="production.com"), tag="production")

# Retrieve the specific one you need
local_db = FletX.find(DatabaseService, tag="local")
prod_db = FletX.find(DatabaseService, tag="production")
```

**Example: Multiple API clients**

```python
# Register different API clients
FletX.put(ApiClient(base_url="https://api.example.com"), tag="main")
FletX.put(ApiClient(base_url="https://backup-api.example.com"), tag="backup")

# Use the main API
main_api = FletX.find(ApiClient, tag="main")
data = main_api.fetch("/users")

# Fall back to backup if main is down
if data is None:
    backup_api = FletX.find(ApiClient, tag="backup")
    data = backup_api.fetch("/users")
```

---

## Service Lifecycle Management

### Creating Fresh Instances Per Request

If you need a new instance each time (not a singleton), create it manually:

```python
# Using singleton from DI
template_service = FletX.find(TemplateService)

# Creating a fresh instance
fresh_template = TemplateService()
```

### Removing a Service

If you need to unregister a service:

```python
FletX.delete(AuthService)

# Try to find it now
auth = FletX.find(AuthService)  # Will raise an error
```

### Clearing Everything

Reset the entire DI container (useful in tests):

```python
FletX.reset()
```

---

## Real-World Example: E-Commerce App

Here's a complete example showing DI in a realistic app:

### Step 1: Define Your Services

```python
# services/auth_service.py
class AuthService:
    def __init__(self):
        self.user = None
    
    def login(self, username, password):
        # In a real app, verify credentials
        self.user = username
    
    def logout(self):
        self.user = None
    
    def is_logged_in(self):
        return self.user is not None

# services/cart_service.py
class CartService:
    def __init__(self):
        self.items = []
    
    def add_item(self, product_id, quantity):
        self.items.append({"id": product_id, "qty": quantity})
    
    def get_total_items(self):
        return sum(item["qty"] for item in self.items)
    
    def clear(self):
        self.items = []

# services/__init__.py
from fletx import FletX
from .auth_service import AuthService
from .cart_service import CartService

def register_services():
    FletX.put(AuthService())
    FletX.put(CartService())
```

### Step 2: Use Services in Pages

```python
import flet as ft
from fletx.core import FletXPage
from fletx import FletX
from services import AuthService, CartService

class ProductListPage(FletXPage):
    def build(self):
        auth = FletX.find(AuthService)
        cart = FletX.find(CartService)
        
        def add_to_cart(product_id):
            if auth.is_logged_in():
                cart.add_item(product_id, 1)
                # Show confirmation...
            else:
                # Redirect to login...
                pass
        
        return ft.Column([
            ft.Text(f"Welcome {auth.user}" if auth.is_logged_in() else "Guest"),
            ft.ElevatedButton(
                f"Add to Cart (Items: {cart.get_total_items()})",
                on_click=lambda _: add_to_cart(101)
            )
        ])

class CartPage(FletXPage):
    def build(self):
        cart = FletX.find(CartService)
        
        return ft.Column([
            ft.Text(f"Cart Items: {cart.get_total_items()}"),
            ft.ElevatedButton(
                "Checkout",
                on_click=lambda _: self.navigate("/checkout")
            )
        ])
```

### Step 3: Initialize Your App

```python
# main.py
from fletx import FletXApp
from routes import setup_routes
from services import register_services

# Setup services first
register_services()

# Setup routes
setup_routes()

# Run the app
app = FletXApp()
app.run()
```

---

## Best Practices

### 1. Register Services Before Creating Pages

Always call `register_services()` before `app.run()`:

```python
# ✅ Good
register_services()
app = FletXApp()
app.run()

# ❌ Avoid - services not registered when pages need them
app = FletXApp()
app.run()
register_services()
```

### 2. Use Service Files for Organization

```
services/
  __init__.py        # Import and register all services
  auth_service.py    # Authentication logic
  cart_service.py    # Shopping cart logic
  settings_service.py # App settings
```

### 3. Let Services Handle Business Logic

Services should contain the logic, pages should just display:

```python
# ✅ Good - Logic in service
class UserService:
    def get_user_full_name(self):
        return f"{self.first_name} {self.last_name}"

class ProfilePage(FletXPage):
    def build(self):
        user_service = FletX.find(UserService)
        return ft.Text(user_service.get_user_full_name())

# ❌ Avoid - Logic in page
class ProfilePage(FletXPage):
    def build(self):
        user_service = FletX.find(UserService)
        # Logic here - harder to test and reuse
        full_name = f"{user_service.first_name} {user_service.last_name}"
        return ft.Text(full_name)
```

### 4. Don't Abuse Global State

Use DI for truly shared services, not everything:

```python
# ✅ Good - Services for business logic
FletX.put(AuthService())
FletX.put(DatabaseService())
FletX.put(NotificationService())

# ❌ Avoid - Don't put everything in DI
FletX.put({"theme_color": "blue"})  # Use page state instead
FletX.put(current_user_id)  # Put it in AuthService
```

---

## Summary

| Task | Code |
|------|------|
| Register a service | `FletX.put(MyService())` |
| Retrieve a service | `FletX.find(MyService)` |
| Register with tag | `FletX.put(MyService(), tag="name")` |
| Retrieve with tag | `FletX.find(MyService, tag="name")` |
| Remove a service | `FletX.delete(MyService)` |
| Clear all services | `FletX.reset()` |

---

## Next Steps

- Learn about [Services](services.md) for more detailed service patterns
- Explore [Controllers](controllers.md) to use DI in controller classes
- Read about [Routing](routing.md) to see DI in action with navigation
- Check the [Architecture](architecture.md) guide for app structure
