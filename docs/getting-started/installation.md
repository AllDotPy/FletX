# Introduction

> **TL;DR**: Install FletX with `pip install fletxr[dev]`, create your first app in 5 minutes with `fletx new my_app`, run it with `fletx run`, and you're building! FletX is a framework for building reactive, modular desktop and web apps with Flet.

---

## What is FletX?

FletX is a **reactive application framework** built on top of [Flet](https://flet.dev). It brings modern app architecture patterns (dependency injection, routing, state management, controllers) to Flet applications.

### FletX vs Flet

**Flet** gives you widgets and basic page routing. You write everything in one place:

```python
# Pure Flet - manual, scattered logic
import flet as ft

def main(page: ft.Page):
    page.title = "Counter"
    
    counter = {"value": 0}  # State scattered everywhere
    
    def increment(_):
        counter["value"] += 1
        text.value = str(counter["value"])
        page.update()
    
    text = ft.Text(counter["value"])
    page.add(text, ft.ElevatedButton("Increment", on_click=increment))

ft.app(target=main)
```

**FletX** organizes your app with controllers, routing, DI, and reactive state:

```python
# FletX - organized, reactive, scalable
from fletx import FletXApp, FletXPage, FletXController, RxInt
from fletx.navigation import router_config
from fletx.decorators import obx
import flet as ft

class CounterController(FletXController):
    def __init__(self):
        self.count = RxInt(0)

class CounterPage(FletXPage):
    ctrl = CounterController()
    
    @obx
    def build(self):
        return ft.Column([
            ft.Text(f"Count: {self.ctrl.count}"),
            ft.ElevatedButton("Increment", on_click=lambda _: self.ctrl.count.increment())
        ])

router_config.add_route("/", CounterPage)
app = FletXApp().run()
```

**Why FletX?**

- ✅ Organized structure - no spaghetti code
- ✅ Reactive UI - UI updates automatically when state changes
- ✅ Scalable - works for small apps and large projects
- ✅ Developer experience - CLI, generators, best practices built-in

---

## Prerequisites

Before installing FletX, make sure you have:

- **Python >=3.10,<=3.13** ([download here](https://www.python.org/downloads/))
- **A package manager**: 
  - `pip` (comes with Python)
  - `uv` (recommended, faster): `pip install uv`

Check your Python version:

```bash
python --version
```

---

## Installation

### Step 1: Install FletX

```bash
pip install fletxr[dev]
```

> ✅ This installs both Flet and FletX. The `[dev]` extras include development tools.
>
> 💡 Using `uv`? Run: `uv pip install fletxr[dev]`

### Step 2: Verify Installation

Test that everything works:

```bash
fletx --version
```

You should see the FletX version number.

---

## Creating Your First App

You have two options: **Quick start with CLI** (recommended) or **manual setup**.

### Option 1: Quick Start with CLI (Recommended)

The FletX CLI creates a complete project structure for you:

```bash
# Create a new project
fletx new my_counter_app

# Navigate into it
cd my_counter_app

# Run it
fletx run
```

That's it! Your app is running. The CLI sets up:
- Project structure
- Example pages and controllers
- Routing configuration
- Build configuration

<div align="center">
  <table>
    <tr>
      <td>
        web
        <img src = "https://github.com/AllDotPy/FletX/blob/master/screeshots/videos/web.gif?raw=true" width="400">
      </td>
      <td rowspan="2">
        Mobile
        <img src = "https://github.com/AllDotPy/FletX/blob/master/screeshots/videos/mobile.gif?raw=true" width="300">
      </td>
    </tr>
    <tr >
      <td>
        Desktop
        <img src = "https://github.com/AllDotPy/FletX/blob/master/screeshots/videos/desktop.gif?raw=true" width="400">
      </td>
    </tr>
  </table>
</div>

### Option 2: Manual Setup

Create a `main.py` file:

```python
import flet as ft
from fletx import FletXApp
from fletx.core import FletXPage, FletXController, RxInt
from fletx.navigation import router_config
from fletx.decorators import obx

# Step 1: Create a controller to manage state
class CounterController(FletXController):
    def __init__(self):
        self.count = RxInt(0)

# Step 2: Create a page that uses the controller
class CounterPage(FletXPage):
    ctrl = CounterController()
    
    # @obx makes this widget reactive - it rebuilds when count changes
    @obx
    def counter_text(self):
        return ft.Text(
            value = f'Count: {self.ctrl.count}',
            size = 50, 
            weight = "bold",
            color = 'red' if not self.ctrl.count.value % 2 == 0 else 'white'
        )
    
    def build(self):
        return ft.Column(
            controls = [
                self.counter_text(),
                ft.ElevatedButton(
                    "Increment",
                    on_click = lambda e: self.ctrl.count.increment()  # Auto UI update
                )
            ]
        )

# Step 3: Register the route
router_config.add_route(path="/", component=CounterPage)

# Step 4: Create and run the app
if __name__ == "__main__":
    app = FletXApp(
        title="My First FletX App",
        initial_route="/"
    )
    app.run()
```

Run it:

```bash
python main.py
```

Desktop
<img src = "https://github.com/AllDotPy/FletX/blob/master/screeshots/videos/obx.gif?raw=true" width="400">

---

## Understanding the App Structure

When you create an app with `fletx new`, you get this structure:

```
my_app/
├── app/
│   ├── __init__.py
│   ├── controllers/          # Controllers manage state and logic
│   │   └── counter_ctrl.py
│   ├── pages/                # UI pages (what users see)
│   │   ├── home_page.py
│   │   └── settings_page.py
│   ├── services/             # Business logic (API, database, etc.)
│   │   ├── __init__.py
│   │   └── auth_service.py
│   ├── components/           # Reusable widgets
│   │   ├── __init__.py
│   │   └── navigation_bar.py
│   ├── models/               # Data structures
│   │   ├── __init__.py
│   │   └── user_model.py
│   └── routes.py             # All routes defined here
├── assets/                   # Images, fonts, static files
│   ├── images/
│   └── fonts/
├── tests/                    # Unit and integration tests
├── main.py                   # Application entry point
├── pyproject.toml            # Python dependencies and metadata
├── .python-version           # Python version specification
└── README.md                 # Project documentation
```

**Key directories:**

| Directory | Purpose |
|-----------|---------|
| `controllers/` | Manage app state using reactive variables (`RxInt`, `RxStr`, etc.) |
| `pages/` | Define UI pages using `FletXPage` |
| `services/` | Shared business logic (database, API calls, authentication) |
| `components/` | Reusable UI widgets you build from Flet controls |
| `models/` | Data classes and structures |
| `routes.py` | Define all app routes in one place |

---

## Your First Real App

Let's create a simple todo app to understand the structure:

### Step 1: Define the Data Model

```python
# app/models/todo.py
class Todo:
    def __init__(self, id: int, title: str, completed: bool = False):
        self.id = id
        self.title = title
        self.completed = completed
```

### Step 2: Create a Service

```python
# app/services/todo_service.py
from app.models.todo import Todo

class TodoService:
    def __init__(self):
        self.todos = []
        self.next_id = 1
    
    def add_todo(self, title: str):
        todo = Todo(self.next_id, title)
        self.todos.append(todo)
        self.next_id += 1
        return todo
    
    def get_todos(self):
        return self.todos
    
    def toggle_todo(self, todo_id: int):
        for todo in self.todos:
            if todo.id == todo_id:
                todo.completed = not todo.completed
    
    def delete_todo(self, todo_id: int):
        self.todos = [t for t in self.todos if t.id != todo_id]
```

### Step 3: Create a Controller

```python
# app/controllers/todo_controller.py
from fletx.core import FletXController, RxList
from app.services.todo_service import TodoService

class TodoController(FletXController):
    def __init__(self):
        self.todos = RxList([])
        self.service = TodoService()
        super().__init__()
    
    def add_todo(self, title: str):
        self.service.add_todo(title)
        self.update_todos_list()
    
    def toggle_todo(self, todo_id: int):
        self.service.toggle_todo(todo_id)
        self.update_todos_list()
    
    def delete_todo(self, todo_id: int):
        self.service.delete_todo(todo_id)
        self.update_todos_list()
    
    def update_todos_list(self):
        self.todos.value = self.service.get_todos()
```

### Step 4: Create a Page

```python
# app/pages/todo_page.py
import flet as ft
from fletx.core import FletXPage
from fletx.decorators import obx
from app.controllers.todo_controller import TodoController

class TodoPage(FletXPage):
    ctrl = TodoController()
    
    def build(self):
        input_field = ft.TextField(
            label="Add a todo",
            width=300
        )
        
        def add_todo(_):
            if input_field.value.strip():
                self.ctrl.add_todo(input_field.value)
                input_field.value = ""
                self.update()
        
        add_button = ft.ElevatedButton("Add", on_click=add_todo)
        
        @obx
        def todo_list():
            return ft.Column([
                ft.Checkbox(
                    label=todo.title,
                    value=todo.completed,
                    on_change=lambda _: self.ctrl.toggle_todo(todo.id)
                )
                for todo in self.ctrl.todos
            ])
        
        return ft.Column([
            ft.Text("My Todos", size=32, weight="bold"),
            ft.Row([input_field, add_button]),
            todo_list()
        ])
```

### Step 5: Register the Route

```python
# app/routes.py
from fletx.navigation import router_config
from app.pages.todo_page import TodoPage

def setup_routes():
    router_config.add_route(
        path="/",
        component=TodoPage
    )
```

### Step 6: Run the App

```python
# main.py
from fletx import FletXApp
from app.routes import setup_routes

if __name__ == "__main__":
    setup_routes()
    
    app = FletXApp(
        title="My Todo App",
        initial_route="/"
    )
    app.run()
```

---

## Using the FletX CLI

The CLI helps you generate code and manage your project:

```bash
# Create a new project
fletx new my_app --author "Your Name" --description "My awesome app"

# Generate a new page
fletx generate page products_page

# Generate a new controller
fletx generate controller products_controller --with-test

# Run with hot reload (in development)
fletx run --debug

# Build for web
fletx run --web

# Run tests
fletx test
```

---

## Next Steps

Now that you have FletX installed and your first app running:

1. **Learn about [Routing](routing.md)** - Navigate between pages
2. **Understand [Dependency Injection](dependency-injection.md)** - Share services across your app
3. **Explore [State Management with Controllers](controllers.md)** - Manage app state reactively
4. **Check [Services](services.md)** - Organize business logic
5. **Read [Architecture](architecture.md)** - See the big picture

