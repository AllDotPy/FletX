
<p align="center">
    <img src="assets/logo/fletx_t.png" height="100" style="height:150px;">
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
    <a href="https://discord.gg/GRez7BTZVy">
        <img src="https://img.shields.io/discord/1381155066232176670" alt="Discord" />
    </a>
    <a href="https://github.com/AllDotPy/FletX">
        <img src="https://img.shields.io/github/commit-activity/m/AllDotPy/FletX" alt="GitHub commit activity" />
    </a>
</p>

# ✨ Welcome to FletX

**FletX** is a lightweight, modular, and reactive architectural framework built on top of [Flet](https://flet.dev), designed to help you build scalable Python UI applications with clean code, structured layers, and modern development patterns.

---

## :material-head-question-outline: What is FletX?

Inspired by frameworks like **GetX** in the Flutter ecosystem, **FletX** introduces powerful architectural patterns to Flet:

- ✅ **Reactive state management**
- ✅ **Modular routing system** with dynamic parameters and guards
- ✅ **Controllers and services** to separate logic from UI
- ✅ **Global and local dependency injection**
- ✅ **Lifecycle hooks** for pages and the app
- ✅ **Unified configuration with fluent API**
- ✅ **Built-in support for asynchronous programming**

---

## 🧠 Philosophy

FletX is built on 3 core principles:

1. **Simplicity** — Focus on code clarity and maintainability  
2. **Modularity** — Encourage component-based structure and reusable logic  
3. **Flexibility** — Allow full control over your app flow, while staying non-intrusive  

> FletX is not a UI library. It doesn’t reinvent Flet’s widgets — it empowers you to use them better by providing a powerful and extensible application layer.

---

## ⚡ Quick Example

```python
import flet as ft

from fletx.app import FletXApp
from fletx.core import (
    FletXPage, FletXController, RxInt, RxStr
)
from fletx.navigation import router_config
from fletx.decorators import (
    simple_reactive
)


class CounterController(FletXController):

    def __init__(self):
        self.count = RxInt(0)
        super().__init__()


@simple_reactive(bindings={'value': 'text'})
class MyReactiveText(ft.Text):

    def __init__(self, rx_text: RxStr, **kwargs):
        self.text: RxStr = rx_text
        super().__init__(**kwargs)


class CounterPage(FletXPage):
    ctrl = CounterController()

    def build(self):
        return ft.Column(
            controls=[
                MyReactiveText(rx_text=self.ctrl.count, size=200, weight="bold"),
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

    app.run()


if __name__ == "__main__":
    main()
```

---

## 🚀 Explore FletX

<div class="grid cards" markdown>

-   :material-power:{ .lg .middle } **Get Started**

    ---

    Set up **FletX** and build your first UI in minutes.

    [→ Installation Guide](getting-started/installation.md)

-   :material-api:{ .lg .middle } **API Reference**

    ---

    Complete reference for all available methods and configurations.

    [→ API Documentation](api-reference.md)

-   :material-rocket-launch:{ .lg .middle } **Guides**

    ---

    Learn routing, state, and architecture with hands-on guides.

    [→ Routing Guide](guides/routing.md) | [→ State Management](guides/state.md)

-   :material-github:{ .lg .middle } **Contribute**

    ---

    Help improve FletX with your feedback and code.

    [→ Contribution Guide](contributing.md)

</div>

---

## 📌 Additional Links

* [GitHub Repository](https://github.com/AllDotPy/FletX)
* [PyPI Package](https://pypi.org/project/FletXr/)
* [Join the Community on Discord](https://discord.gg/GRez7BTZVy)
* [License](LICENSE)

---

Made with ❤️ by [AllDotPy](https://alldotpy.com)
