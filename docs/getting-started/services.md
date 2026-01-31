# Services

> **TL;DR**: A `FletXService` is a reusable component for handling external systems (APIs, databases, hardware, storage). Services have a lifecycle (`on_start()`, `on_ready()`, `on_stop()`, `on_dispose()`), built-in HTTP client, state management (`IDLE`, `LOADING`, `READY`, `ERROR`), and data storage. Use them to keep controllers lean and focused on business logic.

---

## What is a FletXService?

A `FletXService` is a **specialized component** for handling external communication and heavy lifting:

- **HTTP/API calls** - With built-in HTTP client
- **Database operations** - Queries, persistence, transactions
- **File operations** - Reading, writing, uploading files
- **Hardware access** - Camera, GPS, sensors, etc.
- **Caching** - In-memory or persistent caches
- **Authentication** - Token management, OAuth flows
- **WebSocket connections** - Real-time communication
- **Background tasks** - Long-running operations

Services **separate concerns** from controllers, making your code:

- Easier to test (mock services easily)
- More reusable (share services across pages)
- More maintainable (external logic isolated)
- More scalable (handle complex operations cleanly)

---

## Why Services?

**Without Services - Logic Scattered:**

```python
class UserController(FletXController):
    def __init__(self):
        super().__init__()
        self.user = self.create_rx_dict({})
    
    def fetch_user(self, user_id):
        # API call logic mixed with controller
        import requests
        try:
            response = requests.get(f"https://api.example.com/users/{user_id}")
            self.user.value = response.json()
        except Exception as e:
            self.error_message.value = str(e)
        
        # Parse response, validate, cache, retry logic...
        # All here in the controller!
```

**Problems:**

- Controller is overloaded
- Hard to test API logic
- Difficult to reuse API calls in other controllers
- External logic mixed with business logic
- No error handling strategy

**With Services - Clean Separation:**

```python
class UserAPIService(FletXService):
    def __init__(self):
        super().__init__(http_client=HTTPClient("https://api.example.com"))
    
    def fetch_user(self, user_id):
        try:
            response = self.http_client.get(f"/users/{user_id}")
            return response.json()
        except Exception as e:
            self.set_error(e)
            return None

class UserController(FletXController):
    def __init__(self):
        super().__init__()
        self.user = self.create_rx_dict({})
        self.user_service = UserAPIService()
    
    def fetch_user(self, user_id):
        user_data = self.user_service.fetch_user(user_id)
        if user_data:
            self.user.value = user_data
```

**Benefits:**

- ✅ Services handle external logic
- ✅ Controllers focus on state and UI logic
- ✅ Easy to test (mock service)
- ✅ Easy to reuse across controllers
- ✅ Clear separation of concerns

---

## Your First Service

### Step 1: Create a Service

```python
from fletx.core import FletXService, HTTPClient

class WeatherService(FletXService):
    def __init__(self):
        super().__init__(
            name="WeatherService",
            http_client=HTTPClient("https://api.weather.example.com")
        )
    
    def get_weather(self, city):
        response = self.http_client.get(f"/weather?city={city}")
        return response.json()
```

### Step 2: Use in a Controller

```python
from fletx.core import FletXController

class WeatherController(FletXController):
    def __init__(self):
        super().__init__()
        self.weather = self.create_rx_dict({})
        self.weather_service = WeatherService()
    
    def fetch_weather(self, city):
        data = self.weather_service.get_weather(city)
        self.weather.value = data

```

### Step 3: Use in a Page

```python
from fletx.core import FletXPage
from fletx.decorators import obx
import flet as ft

class WeatherPage(FletXPage):
    def __init__(self):
        super().__init__()
        self.controller = WeatherController()
    
    @obx
    def build(self):
        return ft.Column([
            ft.TextField(label="City"),
            ft.ElevatedButton(
                "Get Weather",
                on_click=lambda _: self.controller.fetch_weather("Paris")
            ),
            ft.Text(f"Weather: {self.controller.weather.get('condition', '')}")
        ])
```

Done! 🎉

---

## Service Lifecycle

Services go through clear stages:

```
IDLE → LOADING → READY → (ERROR) → (IDLE) → DISPOSED
```

### Lifecycle States

| State | When | What You Can Do |
|-------|------|-----------------|
| `IDLE` | Created, not started | Initial state |
| `LOADING` | Starting service | Initialization in progress |
| `READY` | Ready to use | Handle requests |
| `ERROR` | Error occurred | Handle error, retry, or stop |
| `DISPOSED` | Cleanup complete | Resources freed |

### Lifecycle Hooks

```python
class DatabaseService(FletXService):
    def __init__(self):
        super().__init__(name="DatabaseService")
        self.connection = None
    
    def on_start(self):
        """Called when service starts"""
        print("Opening database connection...")
        self.connection = self._open_connection()
    
    def on_ready(self):
        """Called when service is ready"""
        print("Database service is ready!")
    
    def on_stop(self):
        """Called when service stops"""
        print("Closing database connection...")
        if self.connection:
            self.connection.close()
    
    def on_dispose(self):
        """Called during final cleanup"""
        print("Database service disposed")
        self.connection = None
    
    def _open_connection(self):
        # Simulate opening connection
        return {"connected": True}
```

### Async Lifecycle

For services needing async operations:

```python
class AsyncAPIService(FletXService):
    async def on_start_async(self):
        """Async version of on_start"""
        print("Starting async service...")
        await self._initialize_async()
    
    async def on_stop_async(self):
        """Async version of on_stop"""
        print("Stopping async service...")
        await self._cleanup_async()
    
    async def _initialize_async(self):
        # Async initialization
        pass
    
    async def _cleanup_async(self):
        # Async cleanup
        pass
```

---

## Service Control

Start, stop, and restart services:

```python
service = MyService(auto_start=False)  # Don't auto-start

# Start the service
service.start()

# Check if ready
if service.is_ready:
    result = service.do_something()

# Restart the service
service.restart()

# Stop the service
service.stop()

# Dispose and cleanup
service.dispose()
```

### Checking Service State

```python
# Check current state
print(service.state)  # ServiceState.READY

# Convenience properties
if service.is_ready:
    # Service is operational
    pass

if service.is_loading:
    # Service is initializing
    pass

if service.has_error:
    # Service has error
    error = service.error
    print(f"Error: {error}")
```

---

## Built-in HTTP Client

Services include an HTTP client for API communication:

```python
from fletx.core import FletXService, HTTPClient

class GitHubService(FletXService):
    def __init__(self):
        super().__init__(
            name="GitHubService",
            http_client=HTTPClient("https://api.github.com")
        )
    
    def get_user(self, username):
        # GET request
        response = self.http_client.get(f"/users/{username}")
        return response.json()
    
    def get_repos(self, username):
        # GET with parameters
        response = self.http_client.get(
            f"/users/{username}/repos",
            params={"per_page": 10}
        )
        return response.json()
    
    def create_gist(self, description, content):
        # POST request
        response = self.http_client.post(
            "/gists",
            json={"description": description, "files": {"code.py": {"content": content}}}
        )
        return response.json()
    
    def update_repo(self, owner, repo, data):
        # PATCH request
        response = self.http_client.patch(
            f"/repos/{owner}/{repo}",
            json=data
        )
        return response.json()
```

---

## Service Data Storage

Services can store and retrieve data:

```python
class UserCacheService(FletXService):
    def __init__(self):
        super().__init__(name="UserCacheService")
    
    def on_start(self):
        # Initialize with data
        self.set_data("users", {})
        self.set_data("last_update", None)
    
    def cache_user(self, user_id, user_data):
        users = self.get_data("users", {})
        users[user_id] = user_data
        self.set_data("users", users)
    
    def get_cached_user(self, user_id):
        users = self.get_data("users", {})
        return users.get(user_id)
    
    def clear_cache(self):
        self.clear_data()
```

### Data Methods

```python
# Set individual data
service.set_data("key", "value")

# Get individual data with default
value = service.get_data("key", default="default_value")

# Get all data (copy)
all_data = service.data

# Clear all data
service.clear_data()
```

---

## Error Handling

Services provide error management:

```python
class PaymentService(FletXService):
    def __init__(self):
        super().__init__(http_client=HTTPClient("https://payment.api.com"))
    
    def process_payment(self, amount, card):
        try:
            response = self.http_client.post(
                "/payment",
                json={"amount": amount, "card": card}
            )
            return response.json()
        except Exception as e:
            # Set error state
            self.set_error(e)
            return None
    
    def on_state_changed(self):
        """Called when service state changes"""
        if self.has_error:
            print(f"Payment error: {self.error}")
```

### Error Properties

```python
# Check for errors
if service.has_error:
    error = service.error
    print(f"Error occurred: {error}")

# Set error manually
service.set_error(Exception("Something went wrong"))
```

---

## Complete Real-World Example

```python
from fletx.core import FletXService, FletXController, FletXPage, HTTPClient
from fletx.decorators import obx
import flet as ft

# Service Layer
class PostAPIService(FletXService):
    def __init__(self):
        super().__init__(
            name="PostAPIService",
            http_client=HTTPClient("https://jsonplaceholder.typicode.com")
        )
    
    def on_start(self):
        print("Post API Service started")
        self.set_data("posts_cache", [])
    
    def fetch_posts(self):
        """Fetch all posts"""
        try:
            response = self.http_client.get("/posts")
            posts = response.json()
            self.set_data("posts_cache", posts)
            return posts
        except Exception as e:
            self.set_error(e)
            return []
    
    def fetch_post_details(self, post_id):
        """Fetch single post with comments"""
        try:
            post = self.http_client.get(f"/posts/{post_id}").json()
            comments = self.http_client.get(f"/posts/{post_id}/comments").json()
            return {"post": post, "comments": comments}
        except Exception as e:
            self.set_error(e)
            return None
    
    def create_post(self, title, body, user_id):
        """Create a new post"""
        try:
            response = self.http_client.post(
                "/posts",
                json={"title": title, "body": body, "userId": user_id}
            )
            return response.json()
        except Exception as e:
            self.set_error(e)
            return None

# Controller Layer
class PostController(FletXController):
    def __init__(self):
        super().__init__()
        self.posts = self.create_rx_list([])
        self.selected_post = self.create_rx_dict({})
        self.post_service = PostAPIService()
        
        # Computed
        self.post_count = self.create_computed(
            lambda: len(self.posts)
        )
    
    def on_ready(self):
        # Load posts when controller is ready
        self.load_posts()
    
    def load_posts(self):
        self.set_loading(True)
        try:
            posts = self.post_service.fetch_posts()
            self.posts.value = posts
            self.emit_local("posts_loaded", len(posts))
        finally:
            self.set_loading(False)
    
    def select_post(self, post_id):
        details = self.post_service.fetch_post_details(post_id)
        if details:
            self.selected_post.value = details
    
    def create_post(self, title, body):
        result = self.post_service.create_post(title, body, 1)
        if result:
            self.posts.append(result)
            self.emit_local("post_created", result)

# View Layer
class PostPage(FletXPage):
    def __init__(self):
        super().__init__(padding=20)
        self.controller = PostController()
        self.title_input = ft.TextField(label="Title")
        self.body_input = ft.TextField(label="Body", multiline=True, min_lines=3)
    
    def on_init(self):
        self.controller.on_local("posts_loaded", self._on_posts_loaded)
    
    def _on_posts_loaded(self, event):
        print(f"Loaded {event.data} posts")
    
    def _create_post(self):
        title = self.title_input.value
        body = self.body_input.value
        if title and body:
            self.controller.create_post(title, body)
            self.title_input.value = ""
            self.body_input.value = ""
            self.refresh()
    
    @obx
    def build(self):
        # Loading state
        if self.controller.is_loading:
            return ft.Center(content=ft.ProgressRing())
        
        # Error state
        if self.controller.error_message:
            return ft.Center(
                content=ft.Column([
                    ft.Icon(ft.icons.ERROR, color=ft.colors.RED),
                    ft.Text(f"Error: {self.controller.error_message}"),
                    ft.ElevatedButton("Retry", on_click=lambda _: self.controller.load_posts())
                ])
            )
        
        # Posts list
        return ft.Column([
            # Header
            ft.Text(
                f"Posts ({self.controller.post_count})",
                size=24,
                weight="bold"
            ),
            
            # Create post form
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        self.title_input,
                        self.body_input,
                        ft.ElevatedButton(
                            "Create Post",
                            on_click=lambda _: self._create_post()
                        )
                    ], spacing=10),
                    padding=15
                )
            ),
            
            # Posts list
            ft.ListView([
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(post["title"], weight="bold", size=14),
                            ft.Text(post["body"][:100] + "...", size=12, color=ft.colors.GREY),
                            ft.Row([
                                ft.TextButton(
                                    "View Details",
                                    on_click=lambda _, pid=post["id"]: self.controller.select_post(pid)
                                )
                            ])
                        ], spacing=5),
                        padding=10
                    )
                )
                for post in self.controller.posts
            ])
        ], scroll=ft.ScrollMode.AUTO, spacing=15)
```

---

## Best Practices

### 1. Keep Services Focused

```python
# ✅ Good - service handles one concern
class UserAPIService(FletXService):
    def fetch_users(self):
        pass
    
    def fetch_user(self, user_id):
        pass

# ❌ Avoid - service doing too much
class AppService(FletXService):
    def fetch_users(self):
        pass
    
    def fetch_posts(self):
        pass
    
    def fetch_comments(self):
        pass
    
    def send_email(self):
        pass
```

### 2. Use Dependency Injection

```python
# ✅ Good - inject service dependencies
class UserController(FletXController):
    def __init__(self, user_service):
        super().__init__()
        self.user_service = user_service

# ❌ Avoid - create service directly
class UserController(FletXController):
    def __init__(self):
        super().__init__()
        self.user_service = UserAPIService()  # Hard to test
```

### 3. Handle Errors Properly

```python
# ✅ Good - error handling
def fetch_data(self):
    try:
        response = self.http_client.get("/data")
        return response.json()
    except Exception as e:
        self.set_error(e)
        return None

# ❌ Avoid - ignoring errors
def fetch_data(self):
    response = self.http_client.get("/data")
    return response.json()  # Crashes on error
```

### 4. Clean Up Resources

```python
# ✅ Good - cleanup in on_stop
def on_start(self):
    self.websocket = WebSocket()
    self.websocket.connect()

def on_stop(self):
    if self.websocket:
        self.websocket.close()

# ❌ Avoid - leaving resources open
def on_start(self):
    self.websocket = WebSocket()
    self.websocket.connect()
    # No cleanup!
```

### 5. Setup Data in on_start

```python
# ✅ Good - initialize data
def on_start(self):
    self.set_data("cache", {})
    self.set_data("config", {"timeout": 30})

# ❌ Avoid - uninitialized data
def fetch_from_cache(self, key):
    cache = self.get_data("cache", {})  # May not exist yet
```

---

## Summary

| Feature | Purpose |
|---------|---------|
| `FletXService` | Base class for services |
| `HTTPClient` | Built-in HTTP client |
| `on_start()` | Initialize service |
| `on_start_async()` | Async initialization |
| `on_ready()` | Called when ready |
| `on_stop()` | Cleanup on stop |
| `on_stop_async()` | Async cleanup |
| `on_dispose()` | Final cleanup |
| `on_state_changed()` | State change hook |
| `state` | Current service state |
| `is_ready` | Check if ready |
| `is_loading` | Check if loading |
| `has_error` | Check for errors |
| `error` | Get error |
| `set_error()` | Set error |
| `set_data()` | Store service data |
| `get_data()` | Retrieve service data |
| `clear_data()` | Clear all data |
| `start()` | Start service |
| `stop()` | Stop service |
| `restart()` | Restart service |
| `dispose()` | Dispose service |
| `http_client` | Access HTTP client |
| `IDLE` | Idle state |
| `LOADING` | Loading state |
| `READY` | Ready state |
| `ERROR` | Error state |
| `DISPOSED` | Disposed state |

---

## Next Steps

- Learn about [Controllers](controllers.md) that use services
- Explore [Dependency Injection](dependency-injection.md) to share services
- Check [Architecture](architecture.md) for service patterns
- Read about [State Management](state-management.md) for service data
