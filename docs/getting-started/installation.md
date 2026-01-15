# 🚀 Getting Started with FletX

Welcome to the official getting started guide for **FletX** — the reactive and modular application architecture for [Flet](https://flet.dev) in Python.

This guide will walk you through:

* Installation
* Creating your first FletX app
* Directory structure

---

## 🧱 Prerequisites

Before starting, make sure you have:

* Python 3.12
* Python package manager
    * `uv` (recommanded)
    * `pip` 

---

## 📦 Installation

```bash
pip install fletxr[dev]
```

> ✅ This will install both Flet and FletX. `fletxr` is the official package name on PyPI.

---

## 🧪 Creating Your First App

You can either start manually or use the FletX CLI to scaffold a new project. Let’s explore both options:

### Option 1: Manual Setup

Create a file `main.py`:

```python
import flet as ft

from fletx.app import FletXApp
from fletx.core import (
    FletXPage, FletXController, RxInt, RxStr
)
from fletx.navigation import router_config
from fletx.decorators import (
    obx
)


class CounterController(FletXController):

    def __init__(self):
        self.count = RxInt(0)
        super().__init__()

class CounterPage(FletXPage):
    ctrl = CounterController()

    @obx
    def counter_text(self):
        return ft.Text(
            value=f'Count: {self.ctrl.count}',
            size=50,
            weight="bold",
            color='red' if not self.ctrl.count.value % 2 == 0 else 'white'
        )

    def build(self):
        return ft.Column(
            controls=[
                self.counter_text(),
                ft.ElevatedButton(
                    "Increment",
                    on_click=lambda e: self.ctrl.count.increment()
                )
            ]
        )

def main():
    router_config.add_route(path='/', component=CounterPage)
    app = FletXApp(
        title="My Counter",
        initial_route="/",
        debug=True
    ).with_window_size(400, 600).with_theme(
        ft.Theme(color_scheme_seed=ft.Colors.BLUE)
    )

    app.run_async()


if __name__ == "__main__":
    main()
```

Run the app:

```bash
# Standard way
python main.py

# Or using flet
flet run main.py
```

### Option 2: Using the CLI

Use the FletX CLI to scaffold a new project:

```bash
fletx new my_app

# Navigate into the project folder
cd my_app

# Run the project
fletx run 
```

---

## 📁 Project Structure

```
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

---


## Example: Create and run

```bash
# Create a project
fletx new my_project --author "John Doe" --description "My FletX app"

# Generate a controller
fletx generate controller MyController --with-test

# Run the project
fletx run --web --debug
```

---

## 🧠 Next Steps

* Learn about the [FletX CLI](fletx-cli.md)
* Explore [reactive UI binding](ui/reactivity.md)
* Dive into [dependency injection](guides/dependency-injection.md)

---

FletX makes architecture clean — so you can focus on building features, not structure.

Happy coding! 🚀
