# Build a Todo App with FletX

## Overview
In this tutorial, we'll build a simple but complete Todo application using FletX. You'll learn how to manage state, handle user input, and structure a FletX application.

## What You'll Learn
- Setting up a FletX page
- Managing reactive state with FletX controllers
- Handling user events (input, button clicks)
- Building a list of items dynamically
- Implementing add and delete functionality

## Prerequisites
- Python 3.8+
- FletX installed (`pip install fletx`)
- Basic Python knowledge

## Step 1: Project Setup

Create a new Python file called `todo_app.py`:

```python
from flet import icons
from fletx import FletXPage, FletXController

class TodoController(FletXController):
    def __init__(self):
        super().__init__()
        self.todos = []
```

This creates a basic controller that will hold our todo list state.

## Step 2: Create the TodoController

Extend the TodoController to manage adding and removing todos:

```python
class TodoController(FletXController):
    def __init__(self):
        super().__init__()
        self.todos = []
    
    def add_todo(self, title):
        """Add a new todo to the list"""
        if title.strip():
            self.todos.append({
                "id": len(self.todos) + 1,
                "title": title,
                "completed": False
            })
            self.update()
    
    def remove_todo(self, todo_id):
        """Remove a todo by ID"""
        self.todos = [t for t in self.todos if t["id"] != todo_id]
        self.update()
    
    def toggle_todo(self, todo_id):
        """Toggle completion status of a todo"""
        for todo in self.todos:
            if todo["id"] == todo_id:
                todo["completed"] = not todo["completed"]
        self.update()
```

## Step 3: Build the UI

Now create the main view:

```python
from flet import (
    Column, Row, TextField, IconButton, Text, 
    ListView, Container, Icon, icons, colors
)
from fletx import FletXPage, FletXController

class TodoPage(FletXPage):
    def __init__(self):
        super().__init__()
        self.controller = TodoController()
        self.title = "Todo App"
        self.vertical_alignment = "start"
        self.horizontal_alignment = "center"
    
    def build(self):
        # Input field for new todos
        self.input_field = TextField(
            label="What needs to be done?",
            width=300,
            on_submit=self.add_todo
        )
        
        # Button to add todos
        add_button = IconButton(
            icon=icons.ADD,
            on_click=self.add_todo,
            tooltip="Add todo"
        )
        
        # Container for the input row
        input_row = Row(
            [self.input_field, add_button],
            alignment="center",
            spacing=10
        )
        
        # Container for todos list
        self.todos_container = Column(
            spacing=10,
            scroll="auto"
        )
        
        # Main layout
        return Column(
            [
                Text("My Todo App", size=28, weight="bold"),
                input_row,
                self.todos_container
            ],
            spacing=20,
            padding=20
        )
    
    def add_todo(self, e=None):
        """Handle adding a new todo"""
        title = self.input_field.value.strip()
        if title:
            self.controller.add_todo(title)
            self.input_field.value = ""
            self.input_field.focus()
            self.update_todos_view()
    
    def remove_todo(self, todo_id):
        """Handle removing a todo"""
        self.controller.remove_todo(todo_id)
        self.update_todos_view()
    
    def toggle_todo(self, todo_id):
        """Handle toggling todo completion"""
        self.controller.toggle_todo(todo_id)
        self.update_todos_view()
    
    def update_todos_view(self):
        """Update the todos list display"""
        self.todos_container.clean()
        
        for todo in self.controller.todos:
            # Create a row for each todo
            todo_text = Text(
                todo["title"],
                size=16,
                color=colors.GREY if todo["completed"] else colors.BLACK,
                style="strikethrough" if todo["completed"] else None
            )
            
            delete_btn = IconButton(
                icon=icons.DELETE,
                icon_color=colors.RED_400,
                on_click=lambda e, tid=todo["id"]: self.remove_todo(tid),
                tooltip="Delete todo"
            )
            
            todo_item = Row(
                [todo_text, delete_btn],
                alignment="space_between",
                spacing=10
            )
            
            # Add container styling
            todo_container = Container(
                content=todo_item,
                padding=10,
                border_radius=5
            )
            
            self.todos_container.controls.append(todo_container)
        
        self.update()
```

## Step 4: Run Your App

Create the main entry point:

```python
if __name__ == "__main__":
    app = TodoPage()
    app.run()
```

## What's Happening?

- **TodoController**: Manages the app state (the list of todos)
- **TodoPage**: Renders the UI and handles user interactions
- **Reactive Updates**: When the controller state changes, we call `update_todos_view()` to refresh the display
- **Event Handling**: Button clicks and text submissions trigger state changes

## Next Steps

To enhance this app, you could:
1. Add due dates to todos
2. Persist todos to a file or database
3. Add categories or tags
4. Implement search/filter functionality
5. Add animations when items are added/removed

## Best Practices Demonstrated

✅ **State Management**: Controller handles all business logic
✅ **Separation of Concerns**: UI logic separate from state management
✅ **Reactive Updates**: UI automatically reflects state changes
✅ **Clean Code**: Well-organized, readable structure
✅ **User Experience**: Clear feedback for user actions
