
<p align="center">
    <img src="assets/logo/fletx_t.png" height="140" alt="FletX logo">
</p>

<p align="center">
    <a href="https://pypi.org/project/FletXr/">
        <img src="https://img.shields.io/pypi/v/FletXr" alt="PyPI Version" />
    </a>
    <a href="https://pepy.tech/project/FletXr">
        <img src="https://static.pepy.tech/badge/FletXr" alt="Downloads" />
    </a>
    <a href="LICENSE">
        <img src="https://img.shields.io/badge/license-MIT-blue" alt="License" />
    </a>
    <a href="https://github.com/AllDotPy/FletX">
        <img src="https://img.shields.io/github/commit-activity/m/AllDotPy/FletX" alt="GitHub commit activity" />
    </a>
</p>

# Welcome to FletX

FletX is a lightweight, modular, and reactive architectural layer built on top of [Flet](https://flet.dev). It helps you structure Python UI apps using clear separation of concerns (Pages → Controllers → Services), predictable lifecycle hooks, and a small set of reactive primitives.

---

**Quick orientation**

- Use `Pages` to describe UI and navigation.
- Use `Controllers` for state and business logic.
- Use `Services` for reusable integrations (APIs, storage).
- Use the CLI to scaffold and run projects quickly.

---

## What is FletX? (short)

FletX brings architecture patterns familiar from mobile/web frameworks (for example, GetX) to Flet applications: reactive state management, modular routing, dependency injection, and lifecycle hooks — without replacing Flet widgets.

Key features:

- Reactive state primitives (`Rx*`, `Computed`, `Observer`) for straightforward UI updates.
- A routing system with guards and nested routes.
- Controllers and Services to separate UI from logic.
- A small set of decorators and helpers for effects, memoization, and batched updates.
- A CLI for scaffolding, generation, running, and testing.

---

## TL;DR — Get started in three commands

```bash
fletx new my_app             # scaffold a project
cd my_app
fletx run --web --watch      # run with hot reload
```

---

## Simple Example (counter)

This minimal example shows how a `Page` and a `Controller` work together:

```python
import flet as ft
from fletx.app import FletXApp
from fletx.core import FletXPage, FletXController, RxInt
from fletx.decorators import obx


class CounterController(FletXController):
    def __init__(self):
        self.count = RxInt(0)

    def increment(self):
        self.count.increment()


class CounterPage(FletXPage):
    ctrl = CounterController()

    @obx
    def counter_label(self):
        return ft.Text(f"Count: {self.ctrl.count}")

    def build(self):
        return ft.Column(controls=[
            self.counter_label(),
            ft.ElevatedButton("+", on_click=lambda e: self.ctrl.increment())
        ])


def main():
    app = FletXApp(title="Counter", initial_route="/", debug=True)
    app.run()


if __name__ == "__main__":
    main()
```

---

## Learn Path — Start here

- **Installation**: getting-started/installation.md — Set up your environment and the CLI.
- **Routing**: getting-started/routing.md — Learn navigation, guards, and route parameters.
- **State**: getting-started/state-management.md — Reactive primitives and patterns.
- **Controllers**: getting-started/controllers.md — Where business logic lives.
- **Pages**: getting-started/pages.md — Page lifecycle and composition.
- **Services**: getting-started/services.md — External integrations and utilities.
- **Decorators**: getting-started/decorators.md — Effects, memoization, and more.

---

## Tools & Resources

- **CLI**: `fletx` — scaffold, generate, run, and test projects. See getting-started/fletx-cli.md for usage.
- **API Reference**: api-reference.md — exhaustive list of classes and helpers.
- **Examples**: examples/template — a starter project you can run and adapt.

---

## Community & Contributing

- GitHub: https://github.com/AllDotPy/FletX
- Discord: https://discord.gg/GRez7BTZVy
- To contribute: read CONTRIBUTING.md and open a PR.

---

Made with ❤️ by AllDotPy
