## Reactivity & Reactive Objects in FletX

**Reactivity** is a core pillar of the FletX framework. It enables building apps where the UI and behavior **automatically adapt** when data changes — with no need for manually propagating state or triggering refreshes.

---

!!! tip "How to read reactivity diagrams"

    - Boxes are **state holders** (Rx) or **consumers** (widgets/controllers).

    - Arrows show **state change propagation**.

    - Use the Architecture guide’s reactivity figure as a companion visual.

[← Back to Architecture](architecture.md)

### 🔄 Why reactivity matters

In most frameworks, when a value changes (e.g. a user logs in), you need to manually update the UI, synchronize the state, or refresh components.

FletX eliminates all of that. It builds tight bindings between your data and your UI/logic, so everything stays in sync, automatically.

This leads to:

* Cleaner code, fewer bugs
* Better separation of concerns
* Faster development
* A more responsive user experience

### 🔄 What is a reactive object?

A reactive object is an **observable variable** that can be watched. When its value changes, **everything depending on it** (UI elements, logic, services, navigation, etc.) gets automatically **updated** or notified.

You can use it to:

* Refresh widgets
* Trigger API calls
* Display alerts
* Change pages or views
* Execute custom business logic

---

### 📦 Built-in reactive types

| Type          | Description            |
| ------------- | ---------------------- |
| `RxInt`       | Reactive integer       |
| `RxStr`       | Reactive string        |
| `RxBool`      | Reactive boolean       |
| `RxList`   | Reactive list          |
| `RxDict` | Reactive dictionary    |
| `Reactive[T]` | Custom reactive object |


**Example 1**
```python
from fletx.core import RxInt, Reactive

# Simple reactive int
counter = RxInt(0)
counter.increment()

# Custom reactive object
class User:
    def __init__(self, name):
        self.name = name

rx_user = Reactive(User("Henri"))
rx_user.value = (User("Sarah"))
```

**Example 2**
```python
from fletx.core import RxInt

counter = RxInt(0)

counter.listen(lambda v: print("New value:", v))

counter.increment()  # Prints: New value: 1
```

**Example 3**
```python

rx_user = Reactive(User("Luc"))

rx_user.listen(lambda u: print(f"User changed to: {u.name}"))

rx_user.value = User("Sarah")  # Prints: User changed to: Sarah
```

---

### ⚙️ UI Reactivity with FletX Decorators

One of the core pillars of FletX is its reactive widget system, built directly on top of Flet's native controls, thanks to powerful decorators like `@simple_reactive`, `@reactive_form`, etc..

#### 🎯 How does it work?

When you decorate a class that extends a Flet control using `@simple_reactive`:

- It creates a binding between Flet’s properties (like `text`, `value`, `disabled`) and reactive objects like `RxStr`, `RxBool`, etc.
- It listens to those reactive variables and **automatically updates** the widget whenever they change.

#### ✅ Example 1 – Creating a custom reactive widgets

```python
@simple_reactive(
    bindings={
        'value': 'text'  # binds self.value() to the Flet Text's .text property
    }
)
class MyReactiveText(ft.Text):
    def __init__(self, value: RxStr, **kwargs):
        self.value: RxStr = value
        super().__init__(**kwargs)


@two_way_reactive({             # Enables two way binding allowing ui to change 
    'value': 'rx_value',        # reactive object's value 
    'visible': 'rx_visible',    # (like Angular two way data binding system)
    'disabled': 'rx_disabled'   # value <--> rx_value
})
class ReactiveTextField(TextField):
    """Example of two way Reactive TextField"""
    
    def __init__(
        self, 
        rx_value: RxStr = RxStr(""), 
        rx_visible: RxBool = RxBool(True),
        rx_disabled: RxBool = RxBool(False),
        **kwargs
    ):
        # Define reactive properties
        self.rx_value = rx_value
        self.rx_visible = rx_visible
        self.rx_disabled = rx_disabled
        
        super().__init__(**kwargs)
```

**usage in a page**

```python
class MyPage(FletXPage):
    def build(self):
        self.counter = RxInt(0)

        return ft.Column([
            ft.ElevatedButton("Increment", on_click=lambda _: self.counter.increment()),
            MyReactiveText(value=self.counter)
        ])
```
> The text content updates automatically each time the counter changes — no manual update() needed.

#### ✅ Example 2 – Reactive forms
```python
@reactive_form(
    form_fields={
        'email': 'rx_email',
        'password': 'rx_password',
    },
    validation_rules={
        'email': 'email_regex',         # Will call self.email_regex with email input value
        'password': 'validate_pass',    # Will call self.validate_pass with password input value
    },
    on_submit = 'perform_submit',  
    on_submit_failed = 'show_erros',
    auto_validate = True
)
class RegistrationForm(Column):
    """Example of Reactive Form"""
    
    def __init__(self):
        # Reactive Properties
        self.rx_email = RxStr("")
        self.rx_password = RxStr("")
        
        super().__init__(spacing=10)

    def validate_pass(self,value:str) -> bool:
        """Example of password validation function"""
        return True

    def email_regex(self,value):
        """example of email validation function"""
        import re
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, value) is not None

    def _build_form(self):
        """Build form Controls."""
        
        self.controls = [
            Text("Login Form", size = 24, weight = FontWeight.BOLD),
            
            ReactiveTextField(
                label = "Your email",
                rx_value = self.rx_email
            ),
            
            ReactiveTextField(
                label = "password",
                password = True,
                rx_value = self.rx_password
            ),
            ElevatedButton(
                text = "Register for free",
                on_click = lambda _: self.submit(),
                disabled = lambda: not self.rx_is_valid.value
            ),

        ]
```

---

### 🎯 Side-effects and logic triggers

Reactive objects can also trigger **non-UI behaviors**:

```python
self.ctrl.logged_in.listen(lambda value: navigate('/home') if value else None)
```

* Service calls
* Conditional business logic
* etc..

---

### 🔧 Targeted Reactivity

FletX gives you **fine-grained reactivity**, letting you update just a button, a field, or a panel — without refreshing the entire page. This results in **better performance and user experience**.

---

## 🧠 Next Steps

* Explore [Controllers](controllers.md)
* Learn about the [Architecture](architecture.md)
* Dive into [dependency injection](guides/dependency-injection.md)