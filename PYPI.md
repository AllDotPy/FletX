<p align = 'center'>
    <img src='https://github.com/AllDotPy/FletX/blob/master/fletx_t.png?raw=true' height = '100'></img>
</p>

# FletX 🚀  
**The open-source GetX-inspired Python Framework for Building Reactive, Cross-Platform Apps with Flet**

[![PyPI Version](https://img.shields.io/pypi/v/FletXr)](https://pypi.org/project/FletXr/)
[![Downloads](https://static.pepy.tech/badge/FletXr)](https://pepy.tech/project/FletXr)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Discord](https://img.shields.io/discord/1381155066232176670)](https://discord.gg/GRez7BTZVy)

## Why FletX? ✨


FletX brings Flutter's beloved **GetX** patterns to Python, combining Flet's UI capabilities with:

- ⚡ **Reactive state management**  
- 🧭 **Declarative routing**  
- 💉 **Dependency injection**  
- 🧩 **Modular architecture**  
- 🎨 **Widget library**  

Perfect for building **desktop, web, and mobile apps** with Python at lightning speed.

---
## Showcase

<div align="center">
  <table>
    <tr>
      <td>
        Counter App
        <img src = "https://github.com/AllDotPy/FletX/blob/master/screeshots/videos/counter.gif?raw=true" width="400">
      </td>
      <td rowspan="2">
        Todo App
        <img src = "https://github.com/AllDotPy/FletX/blob/master/screeshots/videos/reactive_list.gif?raw=true" width="300">
      </td>
    </tr>
    <tr >
      <td>
        Reactive Forms
        <img src = "https://github.com/AllDotPy/FletX/blob/master/screeshots/videos/reactive_forms.gif?raw=true" width="400">
      </td>
    </tr>
  </table>
</div>


<!-- ### Counter App
<img src = "https://github.com/AllDotPy/FletX/blob/master/screeshots/videos/counter.gif" width="400">

### Todo App
<img src = "https://github.com/AllDotPy/FletX/blob/master/screeshots/videos/todo.gif" width="400">

### Reactive Forms
<img src = "https://github.com/AllDotPy/FletX/blob/master/screeshots/videos/reactive_forms.gif" width="400"> -->


## Quick Start 🏁

> NOTE: FletX currently supports Python `>=3.10,<=3.13`. Compatibility with newer versions is in progress — we're actively working to expand support soon.

### Installation
```bash
pip install FletXr --pre
```

### Create project
```sh
fletx new my_project --no-install
```

### Created project structure 🏗️

```sh
my_project/
├── app/
│   ├── controllers/     # Business logic controllers
│   ├── services/       # Business services and API calls
│   ├── models/         # Data models
│   ├── components/     # Reusable widgets
│   ├── pages/          # Application pages
│   └── routes.py       # App routing modules
├── assets/             # Static assets (images, fonts, etc.)
├── tests/              # Test files
├── .python-version     # Python version
├── pyproject.toml      # Python dependencies
├── README.md           # Quick start README
└── main.py            # Application entry point
```

**To run the project, just navigate to the project folder and run this command**

```bash
fletx run --web # Will open app in a navigator
        # --desktop to open app in a desktop window
        # --android to open app on Android device
        # --ios to open app on a iOs device
        # --help for more option
```

---

### Basic Usage (Counter App)
```python
import flet as ft

from fletx.app import FletXApp
from fletx.core import (
    FletXPage, FletXController, RxInt, RxStr
)
from fletx.navigation import router_config
from fletx.widgets import Obx


class CounterController(FletXController):

    def __init__(self):
        count = RxInt(0)  # Reactive state
        super().__init__()


class CounterPage(FletXPage):
    ctrl = CounterController()
    
    def build(self):
        return ft.Column(
            controls = [
                Obx(
                    builder_fn = lambda: ft.Text(
                        value = f'{self.ctrl.count}',
                        size = 100, 
                        weight = ft.FontWeight.BOLD
                    )
                ),
                ft.ElevatedButton(
                    "Increment",
                    on_click = lambda e: self.ctrl.count.increment()  # Auto UI update
                )
            ]
        )


def main():

    # Defining route
    router_config.add_route(
        **{'path': '/', 'component': CounterPage}
    )
    app = FletXApp(
        title = "My Counter",
        initial_route = "/",
        debug = True
    ).with_window_size(400, 600).with_theme(
        ft.Theme(color_scheme_seed=ft.Colors.BLUE)
    )
    
    # Run sync
    app.run()

if __name__ == "__main__":
    main()

```

---

## Core Features 🧠

### 1. Reactive State Management
```python
class SearchController(FletXController):
    """Search controller"""
    
    def __init__(self):
        self.query = RxStr("")
        self.results = RxList([])
        self.is_loading = RxBool(False)
        self.is_enabled = RxBool(True)

        super().__init__()
        
        # Configure reactives effects
        self._setup_reactive_effects()
    
    def _setup_reactive_effects(self):
        """Configure reactive effects"""
        
        # Search with debounce
        @reactive_debounce(0.5)
        @reactive_when(self.is_enabled)
        def search_handler():
            if self.query.value.strip():
                self.perform_search(self.query.value)
        
        # Listen query changes
        self.query.listen(search_handler)
        
        # Cache expensive search results
        @reactive_memo(maxsize=50)
        def expensive_search(query: str):
            # Expensive search simulation
            import time
            time.sleep(0.1)  # Simulate 
            return [f"Result {i} for '{query}'" for i in range(5)]
        
        self.expensive_search = expensive_search

        # Other actions here...
```

### 2. Smart Routing
```python
# Define routes
from fletx.navigation import router_config, navigate

# 1. simple routing
router_config.add_routes([
    {"path": "/", "component": HomePage},
    {"path": "/settings", "component": SettingsPage}
])

# 2. Dynamic routes with parameters
router_config.add_routes([
    {
        "path": "/users/:id",
        "component": lambda route: UserDetailPage(route.params['id'])
    },
    {
        "path": "/products/*category",
        "component": lambda route: ProductsPage(route.params['category'])
    }
])
# Navigate programmatically
navigate("/users/123")
```

### 3. Dependency Injection
```python
# Register services
FletX.put(AuthService(), tag="auth")

# Retrieve anywhere
auth_service = FletX.find(AuthService, tag="auth")
```

### 4. Reactive Widgets
FletX allows you to quickly create reactive widgets from flet Controls by using
reactive widget decorators.
```python
from fletx.decorators import (
    reactive_control, simple_reactive,
    reactive_state_machine, reactive_form,
    two_way_reactive, reactive_list, obx
    ...
)
```

---

## Community & Support 💬

- [Documentation](https://alldotpy.github.io/FletX/) 📚.
- [Discord Community](https://discord.gg/GRez7BTZVy) 💬
- [Issue Tracker](https://github.com/AllDotPy/FletX/issues) 🐛
- [Video Courses](https://www.youtube.com/watch?v=BSp7TUu3Dvo) 🎥

---

## 🤝 Contributing

We welcome contributions from the community! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) guide for more information.

---

## License 📜

MIT © 2025 AllDotPy

```bash
# Happy coding! 
# Let's build amazing apps with Python 🐍
```

<br>
<p align = 'center'>
    <img src='https://github.com/AllDotPy/FletX/blob/master/alldotpy.png?raw=true' height = '60'></img>
</p>
<p align = 'center'>Made with ❤️ By AllDotPy</p>
