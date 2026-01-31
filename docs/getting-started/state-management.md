# FletX State Management

> How FletX makes managing app data **reactive**, **modular**, and **fun** — no manual refresh calls required.

---

## What Is Reactive State Management?

In traditional Python apps, changing a variable doesn't affect your UI automatically — you must manually tell it to refresh.

FletX introduces **reactive variables** that automatically notify the UI whenever their value changes.
Think of it like:

> **"When data changes, the UI reacts — instantly."**

---

## ⚖️ Static vs. Reactive Variables

#### 🧱 Static (Non-Reactive)

```python
count = 0

def increment():
    global count
    count += 1
    print(count)  # UI doesn't update automatically
```

Static variables store data but **don’t trigger any automatic UI refresh**, you’d need to manually call a render or update function whenever the value changes.

---

#### ⚡ Reactive (FletX)

```python
from fletx.core import RxInt

count = RxInt(0)

def increment():
    count.value += 1  # UI updates automatically ✨
```

Reactive variables are **data wrappers** (e.g., `RxInt`, `RxStr`, `RxBool`) that:

- Keep track of their dependencies.
- Automatically notify bound widgets or observers when their value changes.
- Make state updates seamless — no manual re-rendering.

---

> 💡 **Tip:** Use reactive types when you want automatic UI updates or computed state reactions.
> For static data that never changes, plain Python variables are fine.

---

## 🧮 Example 1 — Simple Counter App

```python
import flet as ft
from fletx.core import RxInt
from fletx.widgets import obx

count = RxInt(0)

def main(page: ft.Page):
    def increment(e):
        count.value += 1

    page.add(
        ft.Column([
            obx(lambda: ft.Text(f"Count: {count.value}")),
            ft.ElevatedButton("Increment", on_click=increment)
        ])
    )

ft.app(target=main)
```

🔍 **How it works**

- `RxInt(0)` → creates a reactive integer
- `obx()` → rebuilds the widget when reactive values inside it change
- Changing `count.value` automatically refreshes the text — no extra code!

---

## 🧠 Using a Controller

As apps grow, logic should live outside the UI.
Controllers in FletX manage both state and business logic cleanly.

#### Without Controller

```python
count = RxInt(0)

def increment():
    count.value += 1
```

#### With Controller

```python
from fletx.core.controller import FletXController
from fletx.core import RxInt


class CounterController(FletXController):
    def __init__(self):
        super().__init__()
        self.count = RxInt(0)

    def increment(self):
        self.count.value += 1


# Usage example
ctrl = CounterController()

```

> ✅ **Why this matters:** It separates UI (presentation) from logic (state management), making your app easier to maintain and test.

**Full example:**

```python
import flet as ft
from fletx.core.controller import FletXController as Controller
from fletx.core import RxInt
from fletx.widgets.obx import Obx

class CounterController(Controller):
    def __init__(self):
        self.count = RxInt(0)

    def increment(self):
        self.count.value += 1

def main(page: ft.Page):
    ctrl = CounterController()

    page.add(
        ft.Column([
            Obx(lambda: ft.Text(f"Count: {ctrl.count.value}")),
            ft.ElevatedButton("Increment", on_click=lambda e: ctrl.increment())
        ])
    )

ft.app(target=main)
```

---

## 🧱 Reactive Data Types Overview

| Type              | Description         | Example                      |
| ----------------- | ------------------- | ---------------------------- |
| `RxInt`           | Reactive integer    | `count = RxInt(0)`           |
| `RxStr`           | Reactive string     | `name = RxStr("Sam")`        |
| `RxBool`          | Reactive boolean    | `is_loading = RxBool(False)` |
| `RxFloat`         | Reactive float      | `price = RxFloat(0.0)`       |
| `reactive_list()` | Reactive list       | `tasks = reactive_list([])`  |
| `reactive_dict()` | Reactive dictionary | `user = reactive_dict({})`   |

> ⚠️ **Note:** Reactive containers like lists and dicts, notify the UI when their content changes (not just when reassigned).

---

## 🧩 Reactive Lists and Dicts

```python
import flet as ft
from fletx.core.state import RxList
from fletx.widgets.obx import Obx

tasks = RxList(["Learn FletX", "Write Docs"])

def main(page: ft.Page):
    def add_task(e):
        tasks.append(f"New Task {len(tasks) + 1}")

    page.add(
        ft.Column([
            Obx(lambda: ft.Column([ft.Text(t) for t in tasks])),
            ft.ElevatedButton("Add Task", on_click=add_task)
        ])
    )

ft.app(target=main)
```

> 💡 **Reactive Lists** track changes automatically. When you append or remove an item, the UI updates — no manual refresh required.

---

## 🧮 Computed (Derived) Values

Sometimes, a variable depends on others — you can create a **computed** value that updates automatically.

```python
import flet as ft
from fletx.core.state import RxInt, Computed
from fletx.widgets.obx import Obx

price = RxInt(10)
quantity = RxInt(2)

# Create a computed value that auto-updates
total = Computed(lambda: price.value * quantity.value)

def main(page: ft.Page):
    page.add(
        Obx(lambda: ft.Text(f"Total: ${total.value}"))
    )

ft.app(target=main)

```

> ✅ **Result:** Changing either `price` or `quantity` updates `total` instantly.

---

## ⚙️ Batch Updates (Efficient State Mutations)

When multiple reactive state updates happen together, FletX lets you group them efficiently using a batching context.

This ensures updates trigger **only one UI refresh**, improving performance in reactive UIs.

```python
import asyncio
from fletx.core.state import RxInt
from fletx.decorators.reactive import reactive_batch

count = RxInt(0)
double = RxInt(0)

@reactive_batch()
def increment_both():
    count.value += 1
    double.value = count.value * 2

# Run inside an asyncio event loop
async def main():
    increment_both()
    await asyncio.sleep(0)  # allow batch to flush
    print(count.value, double.value)

asyncio.run(main())

```

> ✅ Only **one** UI refresh occurs after the batched updates — improving performance.

---

## 📏 `.value` vs. Direct Assignment

Beginners often trip on this difference:

```python
count = RxInt(0)

# ✅ Correct - updates the reactive value
count.value = 10

# ❌ Wrong - breaks reactivity entirely
count = 10
```

> ⚠️ **Warning:** Always update `.value`, never overwrite the reactive variable itself.

**Another common mistake:**

```python
count = RxInt(5)

# ❌ Wrong - compares the object, not the value
if count > 3:
    print("Greater than 3")

# ✅ Correct - compares the actual value
if count.value > 3:
    print("Greater than 3")
```

---

## 🌐 Async Operations

FletX works great with async Python — perfect for API calls and background tasks.

```python
import flet as ft
import asyncio
from fletx.core.state import RxBool, RxStr
from fletx.core.controller import FletXController as Controller
from fletx.widgets.obx import Obx


class DataController(Controller):
    def __init__(self):
        super().__init__()
        self.is_loading = RxBool(False)
        self.data = RxStr("")
        self.error = RxStr("")

    async def fetch_data(self):
        self.is_loading.value = True
        self.error.value = ""
        try:
            await asyncio.sleep(1)  # simulate API call
            self.data.value = "Data loaded!"
        except Exception as e:
            self.error.value = str(e)
        finally:
            self.is_loading.value = False


def main(page: ft.Page):
    ctrl = DataController()

    def run_async_task(coro):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.run_until_complete(coro)

    page.add(
        ft.Column(
            [
                Obx(
                    lambda: ft.Text(
                        "Loading..."
                        if ctrl.is_loading.value
                        else ctrl.data.value or f"Error: {ctrl.error.value}"
                    )
                ),
                ft.ElevatedButton(
                    "Load",
                    on_click=lambda e: run_async_task(ctrl.fetch_data()),
                ),
            ]
        )
    )


ft.app(target=main)

```

---

## 🧪 Testing State Logic

FletX state is pure Python — you can test it without a UI.

#### Simple Test

```python
def test_counter():
    count = RxInt(0)
    count.value += 1
    assert count.value == 1
```

#### Testing Controllers

```python
def test_controller():
    ctrl = CounterController()

    assert ctrl.count.value == 0
    ctrl.increment()
    assert ctrl.count.value == 1
```

> 💡 **Pro Tip:** This makes your controllers and reactive logic easily unit-testable — no GUI needed.

---

## ⚠️ Common Pitfalls

### 1️⃣ Breaking Reactivity with Reassignment

```python
tasks = reactive_list([1, 2, 3])

# ❌ Wrong - loses reactivity
tasks = [4, 5, 6]

# ✅ Correct - mutate in place
tasks.clear()
tasks.extend([4, 5, 6])

# ✅ Also correct
tasks[:] = [4, 5, 6]
```

### 2️⃣ Creating Lambdas in Loops

```python
# ❌ Wrong - all will show the same value
for i in range(5):
    page.add(obx(lambda: ft.Text(f"{i}")))

# ✅ Correct - use a function factory
def make_text(index):
    return lambda: ft.Text(f"{index}")

for i in range(5):
    page.add(obx(make_text(i)))
```

### 3️⃣ Heavy Computation in obx()

```python
# ❌ Bad - recalculates every render
obx(lambda: ft.Text(f"Result: {expensive_function(data.value)}"))

# ✅ Better - use computed
result = computed(lambda: expensive_function(data.value))
obx(lambda: ft.Text(f"Result: {result.value}"))
```

---

## 🧭 Best Practices for State Management

| ✅ Practice                                          | 💬 Why It Matters                |
| ---------------------------------------------------- | -------------------------------- |
| Group related reactive variables inside a Controller | Keeps logic modular and testable |
| Use `computed()` for derived data                    | Automatically stays in sync      |
| Wrap multiple updates with `@batch`                  | Reduces unnecessary rebuilds     |
| Always mutate via `.value`                           | Prevents breaking reactivity     |
| Keep `obx()` sections small                          | Improves UI performance          |
| Use `watch()` for side effects only                  | Keeps UI updates clean           |
| Dispose watchers when done                           | Prevents memory leaks            |
| Use computed values for expensive operations         | Caches results automatically     |

---

## ⚡ Quick Troubleshooting

| Issue                | Cause                          | Fix                             |
| -------------------- | ------------------------------ | ------------------------------- |
| UI not updating      | Forgot `.value`                | Always use `.value`             |
| obx() not rebuilding | Logic outside lambda           | Wrap reactive reads in `lambda` |
| Controller resets    | Not stored in persistent scope | Keep reference at module level  |
| Repeated rebuilds    | Nested obx or frequent updates | Use `@batch` or reduce scope    |
| Memory growing       | Watchers not disposed          | Call `.dispose()` on watchers   |
| Wrong loop values    | Lambda closure issue           | Use function factory pattern    |

---

## 📊 Performance Guidelines

| Metric                       | Recommendation | Notes                           |
| ---------------------------- | -------------- | ------------------------------- |
| Reactive vars per controller | 20-30 max      | Split large controllers         |
| `obx()` widgets per page     | < 50           | Use `batch()` for bulk updates  |
| `reactive_list` size         | < 1000 items   | Use pagination for larger lists |
| Nested `obx()` depth         | Avoid nesting  | Causes redundant rebuilds       |
| Watcher callback duration    | < 10ms         | Move heavy work to async tasks  |

---

## 🎯 Real-World Pattern — Todo App

Here's a complete example showing everything working together:

```python
import flet as ft
from fletx.core.controller import FletXController as Controller
from fletx.core.state import RxList, RxStr, Computed
from fletx.decorators.reactive import reactive_batch
from fletx.widgets.obx import Obx


class TodoController(Controller):
    def __init__(self):
        super().__init__()
        self.todos = RxList([])
        self.filter = RxStr("all")
        self._next_id = 1

        # ✅ Computed values defined properly
        self.filtered_todos = Computed(self._compute_filtered_todos)
        self.active_count = Computed(self._compute_active_count)

    # -- Computed logic --
    def _compute_filtered_todos(self):
        if self.filter.value == "active":
            return [t for t in self.todos if not t["completed"]]
        if self.filter.value == "completed":
            return [t for t in self.todos if t["completed"]]
        return list(self.todos)

    def _compute_active_count(self):
        return sum(1 for t in self.todos if not t["completed"])

    # -- Core actions --
    def add_todo(self, text):
        if text.strip():
            self.todos.append({
                "id": self._next_id,
                "text": text.strip(),
                "completed": False,
            })
            self._next_id += 1

    def toggle_todo(self, todo_id):
        for todo in self.todos:
            if todo["id"] == todo_id:
                todo["completed"] = not todo["completed"]
                self.todos.notify()
                break

    def delete_todo(self, todo_id):
        self.todos[:] = [t for t in self.todos if t["id"] != todo_id]

    def clear_completed(self):
        with reactive_batch():
            self.todos[:] = [t for t in self.todos if not t["completed"]]


def main(page: ft.Page):
    ctrl = TodoController()

    def build_todo_list():
        return ft.Column([
            ft.Text(f"Active: {ctrl.active_count.value}"),
            ft.Column([
                ft.Checkbox(
                    label=todo["text"],
                    value=todo["completed"],
                    on_change=lambda e, tid=todo["id"]: ctrl.toggle_todo(tid),
                )
                for todo in ctrl.filtered_todos.value
            ])
        ])

    page.add(Obx(build_todo_list))


ft.app(target=main)

```

---

## 🧠 Next Steps

Now that you've mastered **state management**:

- Explore [Controllers](controllers.md)
- Learn about the [Architecture](architecture.md)
- Dive into [dependency injection](guides/dependency-injection.md)
