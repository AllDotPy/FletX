# Build a Todo App with FletX

## Overview
In this tutorial, we'll build a simple but complete Todo application using FletX. You'll learn how to manage state, handle user input, structure a FletX application using the proper project setup, and use reactive components.

## What You'll Learn
- Creating a FletX project using `fletx new`
- Building reactive state management using RxList
- Managing reactive components with `@reactive_list` decorator
- Handling user events (input, button clicks)
- Building a list of items dynamically
- Implementing add and delete functionality

## Prerequisites
- Python 3.12+
- FletX installed (`pip install fletx` or `pip install FletX --pre` for pre-release)
- Basic Python knowledge

## Step 1: Project Setup

Create a new FletX project:

```bash
fletx new todo_app
cd todo_app
```

This creates the proper FletX project structure with all necessary configuration.

## Step 2: Create the Todo Controller

In your controller file, create a `TodoController` that manages the application state using reactive objects:

```python
from fletx import FletXController

class TodoController(FletXController):
    def __init__(self):
        super().__init__()
        # Use RxList instead of regular list so UI can subscribe to changes
        self.todos = self.create_rx_list([])
    
    def add_todo(self, title: str):
        """Add a new todo item"""
        self.todos.append({
            "title": title,
            "completed": False
        })
    
    def delete_todo(self, index: int):
        """Delete a todo item by index"""
        if 0 <= index < len(self.todos):
            self.todos.pop(index)
    
    def toggle_todo(self, index: int):
        """Toggle completed status of a todo"""
        if 0 <= index < len(self.todos):
            todo = self.todos[index]
            todo["completed"] = not todo["completed"]
            # Update the list to trigger UI refresh
            self.todos[index] = todo
```

## Step 3: Create a Reactive Todo List Component

Generate a reactive component:

```bash
fletx generate component todo_list
```

Then update your component file with the `@reactive_list` decorator:

```python
from fletx import FletXComponent, reactive_list
from flet import Row, Checkbox, IconButton, icons, Column, Text

@reactive_list
class TodoList(FletXComponent):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
    
    def build(self):
        return Column(
            controls=[
                Row(
                    controls=[
                        Checkbox(
                            label=todo.get("title", ""),
                            value=todo.get("completed", False),
                            on_change=lambda e, idx=i: self.controller.toggle_todo(idx)
                        ),
                        IconButton(
                            icon=icons.DELETE,
                            on_click=lambda e, idx=i: self.controller.delete_todo(idx)
                        )
                    ]
                )
                for i, todo in enumerate(self.controller.todos)
            ]
        )
```

## Step 4: Create the Main Page

Create a `TodoPage` that brings everything together:

```python
from fletx import FletXPage, FletXApp
from flet import Column, Row, TextField, IconButton, icons, Container, padding
from todo_list import TodoList
from controller import TodoController

class TodoPage(FletXPage):
    def __init__(self):
        super().__init__()
        self.controller = TodoController()
    
    def build(self):
        input_field = TextField(
            label="Add a new task",
            expand=True
        )
        
        def add_todo():
            if input_field.value.strip():
                self.controller.add_todo(input_field.value.strip())
                input_field.value = ""
                self.update()
        
        return Column(
            controls=[
                Row(
                    controls=[
                        input_field,
                        IconButton(
                            icon=icons.ADD,
                            on_click=lambda e: add_todo()
                        )
                    ]
                ),
                TodoList(self.controller)
            ],
            padding=padding.all(20)
        )
```

## Step 5: Run Your Application

Update your `main.py` file to use `FletXApp` instead of running the page directly:

```python
from fletx import FletXApp
from pages.todo_page import TodoPage

if __name__ == "__main__":
    app = FletXApp(page_class=TodoPage)
    app.run()
```

## Key Concepts Explained

### Reactive List (RxList)
The `RxList` created with `self.create_rx_list([])` automatically notifies the UI when items change. This means you don't need to manually call `self.update()`. The UI subscribes to these changes and updates automatically.

### @reactive_list Decorator
This decorator makes your component automatically rebuild whenever the reactive list changes. This is the proper way to handle dynamic lists in FletX.

### Project Structure
Using `fletx new` provides the correct project structure and configuration. This is required for FletX applications to work properly.

## Complete Example

For a complete working example with more features, check out the [fake-shop](https://github.com/AllDotPy/fake-shop) repository which demonstrates best practices for FletX development.

## Next Steps

- Add persistence by saving todos to a file or database
- Implement todo categories or tags
- Add filtering options (show all, completed, pending)
- Style the application with custom themes
