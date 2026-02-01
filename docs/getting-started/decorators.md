# Reactive Decorators

>**TL;DR** — Decorators that let you control precisely *how* and *when* reactive code executes.

## Problem

When you write reactive UI code, you quickly face challenges:

- A value changes 10 times in 100ms → 10 recomputations instead of 1
- User search triggers an API request on every keystroke
- An effect function subscribes 50 times to the same event
- Code runs even when its conditions no longer apply

## Solution

FletX provides a toolkit of decorators that factorize recurring patterns. Use them to debounce, throttle, memoize, batch, filter, and structure your reactive effects.

## Progression: simple → advanced

We'll progress from simple use cases (5 min) to sophisticated patterns (20 min). All examples use real APIs from `fletx/decorators/*`.

---

## 1. Batch updates: `@reactive_batch()`

**When to use it:** You mutate an `RxList` or multiple `Reactive` values in quick succession, and you want *one* UI update instead of many.

**Example:**

```python
from fletx.decorators import reactive_batch
from fletx.core.state import RxList

items = RxList([])

@reactive_batch()
def refresh_ui():
    print('Updating UI with:', items.value)

# Add 3 items quickly
items.append('user1')
items.append('user2')
items.append('user3')
# refresh_ui() runs ONCE on the next tick (not 3 times)
```

**Tip:** Keep `refresh_ui()` small and without heavy side effects. It's just a grouper.

---

## 2. Wait for a pause: `@reactive_debounce(delay)`

**When to use it:** User input (search box), API calls, heavy computations triggered by the user.

**Example:**

```python
from fletx.decorators import reactive_debounce
from fletx.core.state import RxStr

search_query = RxStr("")

@reactive_debounce(0.4)  # wait 400ms of silence
def perform_search(q: RxStr):
    print(f"Searching for: {q.value}")
    # API call here...

# User types: s -> e -> a -> r -> c -> h
# perform_search() is called only once, 400ms after user stops typing
```

**Tip:** Use 0.3–0.5s for user input, 1–2s for heavy computation. Don't abuse long delays in critical flows.

---

## 3. Limit frequency: `@reactive_throttle(interval)`

**When to use it:** Scroll, resize, high-frequency events. You want to execute *at most* once per interval.

**Example:**

```python
from fletx.decorators import reactive_throttle

@reactive_throttle(0.1)  # max once per 100ms
def on_scroll_event(e):
    print("Updating visible items...")
    # recalc visible range
```

**Tip:** Throttle maintains responsiveness (fast execution), whereas debounce waits for inactivity.

---

## 4. Execute only if: `@reactive_when(condition)`

**When to use it:** A flag enables/disables behavior. Feature flags, admin mode, permissions.

**Example:**

```python
from fletx.decorators import reactive_when
from fletx.core.state import RxBool

is_logged_in = RxBool(False)

@reactive_when(is_logged_in)
def sync_user_data():
    print("Syncing...")
    # network call
```

**Tip:** The condition can be a callable or a `Reactive[bool]`.

---

## 5. Observe selectively: `@reactive_select(*reactive_props)`

**When to use it:** An object has many properties. You only want to react to certain ones.

**Example:**

```python
from fletx.decorators import reactive_select
from fletx.core.state import RxStr, RxInt

user_name = RxStr("Alice")
user_age = RxInt(25)

@reactive_select(user_name)  # observe only user_name
def display_name():
    print(f"Name: {user_name.value}")

user_age.value = 26  # no recalc
user_name.value = "Bob"  # recalc!
```

**Tip:** Reduces unnecessary recomputations when a state has many properties.

---

## 6. Pure derivations: `@reactive_computed(deps=None)`

**When to use it:** Create a reactive value computed from other reactives.

**Example:**

```python
from fletx.decorators import reactive_computed
from fletx.core.state import RxInt

width = RxInt(100)
height = RxInt(50)

@reactive_computed([width, height])
def area():
    return width.value * height.value

print(area.value)  # 5000 → Computed[int]
```

**Tip:** The function must be pure (no side effects). FletX automatically caches the result as long as dependencies don't change.

---

## 7. Cache computations: `@reactive_memo(maxsize=64, key_fn=None)`

**When to use it:** An expensive function called multiple times with the same arguments.

**Example:**

```python
from fletx.decorators import reactive_memo
from fletx.core.state import RxList

users = RxList([...])

@reactive_memo(maxsize=32)
def filter_active_users():
    # FletX automatically detects that you read `users`
    return [u for u in users.value if u.active]

# Call 1: compute and cache
result1 = filter_active_users()
# Call 2: return from cache (users unchanged)
result2 = filter_active_users()
# users changes → cache invalidated
users.append(new_user)
# Call 3: recompute
result3 = filter_active_users()
```

**Tip:** Provide `key_fn` if your arguments are complex.

---

## 8. Run side effects: `@reactive_effect(deps=None, auto_run=True)` and `use_effect(effect_fn, deps)`

**When to use it:** Timers, sockets, subscriptions, DOM modifications, non-GET API calls.

**Example 1 — `reactive_effect` declarative:**

```python
from fletx.decorators import reactive_effect
from fletx.core.state import RxInt

counter = RxInt(0)

@reactive_effect([counter])
def log_changes():
    print(f"Counter is now: {counter.value}")

counter.value = 1  # → prints "Counter is now: 1"

# To stop observing:
# log_changes.dispose()
```

**Example 2 — `use_effect` in a builder:**

```python
from fletx.decorators.effects import use_effect

def my_builder():
    def setup_timer():
        timer = asyncio.create_task(do_something())
        
        def cleanup():
            timer.cancel()  # critical cleanup!
        
        return cleanup
    
    use_effect(setup_timer, [some_dependency])
    return ft.Text("Timer running")
```

**Tip:** **Always** return a cleanup function if you open external resources (timers, sockets, subscriptions). FletX calls it when the component is destroyed.

---

## 9. Reactive builder: `@obx` (from `fletx/decorators/widgets.py`)

**When to use it:** Create a widget that rebuilds reactively when its dependencies change — but preserves widget identity in the tree.

**Example:**

```python
from fletx.decorators.widgets import obx
from fletx.core.state import RxInt
import flet as ft

class CounterController:
    def __init__(self):
        self.count = RxInt(0)
    
    @obx
    def counter_display(self):
        # Whenever self.count changes, this builder runs
        # and the Text is regenerated in place
        color = 'red' if self.count.value % 2 == 0 else 'blue'
        return ft.Text(
            value=f"Count: {self.count.value}",
            color=color
        )
```

**Tip:** FletX automatically detects all reads of `Reactive` during the build. No need to list dependencies.

---

## 10. Reusable reactive controls

### 10.1. Bind a property: `@reactive_control()`, `@simple_reactive()`, `@two_way_reactive()`

**When to use it:** You're creating a reusable widget and want its properties to sync with reactives.

**Example — simple binding:**

```python
from fletx.decorators.widgets import simple_reactive
from fletx.core.state import RxStr

@simple_reactive({'value': 'rx_text'})
class MyTextField(ft.TextField):
    def __init__(self):
        self.rx_text = RxStr("Hello")
        super().__init__()

# Use it:
tf = MyTextField()
# tf.value is now bound to tf.rx_text
tf.rx_text.value = "World"  # → tf.value changes automatically
```

**Example — two-way binding:**

```python
from fletx.decorators.widgets import two_way_reactive

@two_way_reactive({'value': 'rx_text'})
class MyTextField(ft.TextField):
    def __init__(self):
        self.rx_text = RxStr("")
        super().__init__()

# User types in the field → rx_text changes too
```

### 10.2. Computed properties: `@computed_reactive()`

**Example:**

```python
from fletx.decorators.widgets import computed_reactive
from fletx.core.state import RxInt

@computed_reactive(
    text=lambda self: f"Score: {self.rx_score.value}",
    color=lambda self: 'green' if self.rx_score.value > 50 else 'red'
)
class ScoreLabel(ft.Text):
    def __init__(self):
        self.rx_score = RxInt(0)
        super().__init__()
```

### 10.3. Reactive lists: `@reactive_list()`

**When to use it:** You have an `RxList` and want it to render automatically.

**Example:**

```python
from fletx.decorators.widgets import reactive_list
from fletx.core.state import RxList
import flet as ft

@reactive_list(
    items_attr='rx_todos',
    item_builder=lambda todo, idx: ft.ListTile(
        title=ft.Text(todo),
        leading=ft.Text(str(idx))
    ),
    empty_builder=lambda: ft.Text("No todos yet")
)
class TodoList(ft.Column):
    def __init__(self):
        self.rx_todos = RxList(['Buy milk', 'Walk dog'])
        super().__init__()
```

### 10.4. Forms: `@reactive_form()`

**When to use it:** You're building a form with validations and a submit handler.

**Example:**

```python
from fletx.decorators.widgets import reactive_form
from fletx.core.state import RxStr

@reactive_form(
    form_fields={
        'email': 'rx_email',
        'password': 'rx_password'
    },
    validation_rules={
        'email': lambda v: '@' in v,
        'password': lambda v: len(v) >= 8
    },
    on_submit=lambda form: print("Form values:", form.get_values())
)
class LoginForm(ft.Column):
    def __init__(self):
        self.rx_email = RxStr("")
        self.rx_password = RxStr("")
        super().__init__()
```

### 10.5. State machine: `@reactive_state_machine()`

**When to use it:** A widget has multiple states (idle, loading, error, success) and transitions between them.

**Example:**

```python
from enum import Enum
from fletx.decorators.widgets import reactive_state_machine
import flet as ft

class LoadState(Enum):
    IDLE = 'idle'
    LOADING = 'loading'
    SUCCESS = 'success'
    ERROR = 'error'

@reactive_state_machine(
    states=LoadState,
    initial_state=LoadState.IDLE,
    transitions={
        (LoadState.IDLE, 'start'): LoadState.LOADING,
        (LoadState.LOADING, 'done'): LoadState.SUCCESS,
        (LoadState.LOADING, 'fail'): LoadState.ERROR,
        (LoadState.ERROR, 'retry'): LoadState.LOADING,
    }
)
class DataLoader(ft.Container):
    def __init__(self):
        super().__init__()
    
    def fetch_data(self):
        if self.transition('start'):
            # do async work...
            pass
```

---

## Complete example: search engine

```python
from fletx.core.state import RxStr, RxList
from fletx.decorators import reactive_debounce, reactive_memo
from fletx.decorators.widgets import obx, reactive_list
import flet as ft

class SearchApp:
    def __init__(self):
        self.query = RxStr("")
        self.results = RxList([])
        self.all_items = ["Apple", "Apricot", "Banana", "Blueberry"]
    
    @reactive_memo(maxsize=32)
    def compute_results(self, q: str):
        # Cache: if q hasn't changed, return from cache
        return [item for item in self.all_items if item.lower().startswith(q.lower())]
    
    @reactive_debounce(0.35)
    def search(self, q: RxStr):
        # Executes only 350ms after query stops changing
        self.results.value = self.compute_results(q.value)
    
    @obx
    def search_box(self):
        # Rebuilds if self.query changes
        return ft.TextField(
            label="Search",
            on_change=lambda e: self.query.set(e.control.value)
        )
    
    @obx
    def result_list(self):
        # Rebuilds if self.results changes
        return ft.Column([
            ft.Text(item) for item in self.results.value
        ])

# Usage:
app = SearchApp()
# When query changes → search() is called after 350ms → results updates → result_list() rebuilds
```

---

## Best practices (summary)

| Problem | Solution |
|---------|----------|
| Too many updates | `@reactive_batch()` or group mutations |
| User search + API calls | `@reactive_debounce()` |
| Scroll/resize high frequency | `@reactive_throttle()` |
| Function called often with same arg | `@reactive_memo()` |
| Complex condition for execution | `@reactive_when()` |
| Pure derived value | `@reactive_computed()` |
| Effects (timers, sockets) | `@reactive_effect()` or `use_effect()` |
| Widget that reacts to changes | `@obx` |
| Reusable control | `@reactive_control`, `@reactive_form`, `@reactive_list` |

---

## Common pitfalls

1. **Not cleaning up effects** → memory leaks. Always return a cleanup function.
2. **Keeping cache too long** → stale data. Prefer small `maxsize`.
3. **Too aggressive debounce** → user waits. Stay under 500ms.
4. **Forgetting that `computed` auto-caches** → no need for memo if you use `Computed`.
5. **Mixing computation and effects** → hard to test. Keep them separate.

---

## References

- `fletx/decorators/reactive.py` — batch, memo, debounce, throttle, when, select, effect, computed
- `fletx/decorators/effects.py` — use_effect
- `fletx/decorators/widgets.py` — obx, reactive_control, reactive_form, reactive_list, reactive_state_machine

See also:

- [Controllers](controllers.md) — how to structure your reactive logic
- [State Management](state-management.md) — understand `RxInt`, `RxList`, `Computed`
- [Pages](pages.md) — integrate decorators and pages into your app

---

**Ready to try?** Start with `@reactive_debounce()` on a search box. It's the most common use case!
