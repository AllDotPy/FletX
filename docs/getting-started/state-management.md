# FletX State Management

> How FletX makes managing app data **reactive**, **modular**, and **fun** — no manual refresh calls required.

---

**Requirements:**

- FletX: `0.1.0+`
- Flet: `0.23.0+`
- Python: `3.8+`

---

## What Is Reactive State Management?

In traditional Python apps, changing a variable doesn't affect your UI automatically — you must manually tell it to refresh.

FletX introduces **reactive variables** that automatically notify the UI whenever their value changes.
Think of it like:

> **"When data changes, the UI reacts — instantly."**

---

## ⚖️ Static vs. Reactive Variables

#### Static (Non-Reactive)

```python
count = 0

def increment():
    global count
    count += 1
    print(count)  # UI doesn't update automatically
```

#### Reactive (FletX)

```python
from fletx import RxInt

count = RxInt(0)

def increment():
    count.value += 1  # UI updates automatically ✨
```

</tab>
</tabs>

> 💡 **Tip:** Reactive variables wrap your data type (e.g., int, str, bool) and automatically notify widgets that depend on them.

---

## 🧮 Example 1 — Simple Counter App

```python
import flet as ft
from fletx import RxInt, obx

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
from fletx import Controller, RxInt

class CounterController(Controller):
    def __init__(self):
        self.count = RxInt(0)

    def increment(self):
        self.count.value += 1

# Usage in main
ctrl = CounterController()
```

</tab>
</tabs>

> ✅ **Why this matters:** It separates UI (presentation) from logic (state management), making your app easier to maintain and test.

**Full example:**

```python
import flet as ft
from fletx import Controller, RxInt, obx

class CounterController(Controller):
    def __init__(self):
        self.count = RxInt(0)

    def increment(self):
        self.count.value += 1

def main(page: ft.Page):
    ctrl = CounterController()

    page.add(
        ft.Column([
            obx(lambda: ft.Text(f"Count: {ctrl.count.value}")),
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
from fletx import reactive_list, obx

tasks = reactive_list(["Learn FletX", "Write Docs"])

def main(page: ft.Page):
    def add_task(e):
        tasks.append("New Task")

    page.add(
        ft.Column([
            obx(lambda: ft.Column([ft.Text(t) for t in tasks])),
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
from fletx import RxInt, computed, obx
import flet as ft

price = RxInt(10)
quantity = RxInt(2)

# Create a computed value
total = computed(lambda: price.value * quantity.value)

def main(page: ft.Page):
    page.add(
        obx(lambda: ft.Text(f"Total: ${total.value}"))
    )

ft.app(target=main)
```

> ✅ **Result:** Changing either `price` or `quantity` updates `total` instantly.

---

## 👀 Watching for State Changes

Sometimes, you don't want to rebuild the UI — just **react to changes** logically.

#### Single Watch

```python
def on_count_change(value):
    print(f"Count changed to {value}")

# Set up watcher
ctrl.count.watch(on_count_change)
```

#### Multiple Watch

```python
from fletx import watch_multiple

def on_state_change():
    print("Either count or username changed!")

watch_multiple([ctrl.count, ctrl.username], on_state_change)
```

> 💡 **When to use:** Ideal for logging, analytics, or triggering side effects like network calls.

> ⚠️ **Important:** Remember to dispose of watchers when they're no longer needed to prevent memory leaks (see Cleanup section below).

---

## 🔍 Deep Watching (Lists & Dicts)

Reactive lists and dicts also trigger watchers when modified:

```python
from fletx import reactive_list

tasks = reactive_list(["Learn", "Write"])

def on_tasks_update(new_value):
    print("Tasks updated:", new_value)

tasks.watch(on_tasks_update)
tasks.append("Deploy")  # triggers watcher
```

> This allows you to track dynamic data like user input, notifications, or live updates.

---

## ⚙️ Batch Updates (Efficient State Mutations)

When multiple state updates happen together, FletX lets you group them efficiently.

```python
from fletx import RxInt, batch

count = RxInt(0)
double = RxInt(0)

@batch
def increment_both():
    count.value += 1
    double.value = count.value * 2
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

## 🧹 Cleanup & Memory Management

When using watchers, it's important to clean them up to prevent memory leaks.

```python
from fletx import Controller, RxInt

class MyController(Controller):
    def __init__(self):
        self.count = RxInt(0)
        self._watchers = []

    def setup(self):
        # Store watcher reference for later cleanup
        watcher = self.count.watch(self._on_count_change)
        self._watchers.append(watcher)

    def _on_count_change(self, value):
        print(f"Count: {value}")

    def dispose(self):
        # Clean up watchers when controller is no longer needed
        for watcher in self._watchers:
            watcher.dispose()
        self._watchers.clear()
```

> 💡 **Pro Tip:** Always dispose of watchers when components are removed or the app closes.

---

## 🔗 Coordinating Multiple States

You can link multiple reactive variables together easily:

```python
from fletx import RxInt, watch_multiple

a = RxInt(0)
b = RxInt(0)

def show_sum():
    print(f"a + b = {a.value + b.value}")

watch_multiple([a, b], show_sum)
```

Every time `a` or `b` changes, the sum recalculates.

---

## 🌐 Async Operations

FletX works great with async Python — perfect for API calls and background tasks.

```python
from fletx import Controller, RxBool, RxStr
import flet as ft

class DataController(Controller):
    def __init__(self):
        self.is_loading = RxBool(False)
        self.data = RxStr("")
        self.error = RxStr("")

    async def fetch_data(self):
        self.is_loading.value = True
        self.error.value = ""

        try:
            # Simulate API call
            await asyncio.sleep(1)
            self.data.value = "Data loaded!"
        except Exception as e:
            self.error.value = str(e)
        finally:
            self.is_loading.value = False

def main(page: ft.Page):
    ctrl = DataController()

    page.add(
        ft.Column([
            obx(lambda: ft.Text("Loading..." if ctrl.is_loading.value else ctrl.data.value)),
            ft.ElevatedButton("Load", on_click=lambda e: ctrl.fetch_data())
        ])
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

#### Testing Watchers

```python
def test_watcher():
    updates = []
    count = RxInt(0)
    count.watch(lambda v: updates.append(v))

    count.value = 5
    count.value = 10

    assert updates == [5, 10]
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
from fletx import Controller, reactive_list, RxStr, computed, batch

class TodoController(Controller):
    def __init__(self):
        self.todos = reactive_list([])
        self.filter = RxStr("all")  # all, active, completed
        self._next_id = 1

    @computed
    def filtered_todos(self):
        if self.filter.value == "active":
            return [t for t in self.todos if not t["completed"]]
        elif self.filter.value == "completed":
            return [t for t in self.todos if t["completed"]]
        return list(self.todos)

    @computed
    def active_count(self):
        return sum(1 for t in self.todos if not t["completed"])

    def add_todo(self, text):
        if text.strip():
            self.todos.append({
                "id": self._next_id,
                "text": text.strip(),
                "completed": False
            })
            self._next_id += 1

    def toggle_todo(self, todo_id):
        for todo in self.todos:
            if todo["id"] == todo_id:
                todo["completed"] = not todo["completed"]
                self.todos.notify()  # Trigger update
                break

    def delete_todo(self, todo_id):
        self.todos[:] = [t for t in self.todos if t["id"] != todo_id]

    @batch
    def clear_completed(self):
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
                    on_change=lambda e, tid=todo["id"]: ctrl.toggle_todo(tid)
                )
                for todo in ctrl.filtered_todos.value
            ])
        ])

    page.add(obx(build_todo_list))

ft.app(target=main)
```

---

## 🧠 Next Steps

Now that you've mastered **state management**:

- Explore [Controllers](controllers.md)
- Learn about the [Architecture](architecture.md)
- Dive into [dependency injection](guides/dependency-injection.md)
