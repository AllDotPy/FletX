# FletX CLI Guide

## TL;DR

>The **FletX CLI** (`fletx`) automates project scaffolding, component generation, and development workflows:

```bash
fletx new my_project           # Create a new project
fletx generate controller Home # Add a controller
fletx run --web --watch        # Run with hot reload
```

---

## The Problem You're Solving

Managing a FletX project requires:

1. **Scaffolding**: Creating the initial project structure with proper folders and configurations
2. **Consistency**: Generating components (controllers, services, pages) that follow FletX conventions
3. **Development**: Running your app locally during development with feedback and debugging
4. **Testing**: Validating your code works as expected

Without the CLI, you'd manually create files, remember folder structures, and write boilerplate code every time. The FletX CLI eliminates this friction.

---

## The Solution: Progressive Commands

The CLI provides four core commands. Let's explore them from beginner to advanced.

### Pattern 1: Create Your First Project

**Scenario**: You're starting a brand-new FletX application.

```bash
# Basic project creation
fletx new my_app

# This creates:
# my_app/
# ├── main.py                    # Entry point
# ├── pyproject.toml             # Project metadata
# ├── requirements.txt           # Dependencies
# └── app/
#     ├── __init__.py
#     ├── routes.py              # Route definitions
#     ├── controllers/           # Business logic
#     ├── pages/                 # UI screens
#     ├── services/              # Reusable utilities
#     └── ...
```

**What happens**: The CLI uses a template to scaffold your entire project structure, including necessary dependencies and configuration files.

### Pattern 2: Add Customization During Creation

**Scenario**: You want to document your project metadata from the start.

```bash
fletx new my_app \
  --author "Jane Doe" \
  --description "My awesome FletX app" \
  --version "0.2.0" \
  --python-version "3.10"
```

**Key options**:

- `--author`: Set the project author (also reads `$USER` env variable)
- `--description`: Project description for `pyproject.toml`
- `--version`: Initial version number
- `--python-version`: Minimum Python version required
- `--no-install`: Skip automatic dependency installation (useful if you customize `requirements.txt` first)
- `--directory`: Create project in a specific folder instead of current directory

### Pattern 3: Generate Code Components

**Scenario**: Your project exists, and you need to add a new feature. You don't want to manually create the file structure.

```bash
# Create a new controller
fletx generate controller ProductList --with-test

# Create a service
fletx generate service ApiClient

# Create a page
fletx generate page Settings
```

**What's generated**:

```bash
# For controllers:
# app/controllers/product_list_controller.py

# For services:
# app/services/api_client_service.py

# For pages:
# app/pages/settings_page.py
```

Each generated file includes:

- Proper imports and class structure
- Docstrings explaining purpose and usage
- Lifecycle hooks (if applicable, e.g., for controllers)
- TypeHints for better IDE support

**Advanced**: Generate with test file

```bash
fletx generate service DatabaseService --with-test

# Creates two files:
# - app/services/database_service.py
# - tests/services/database_service_test.py
```

**Supported component types**:

- `controller`: Contains reactive state and business logic
- `service`: Reusable utility class (no UI logic)
- `page`: Full screen with navigation and lifecycle
- `component`: Reusable UI widget (part of pages)
- `middleware`: Route interceptor
- `guard`: Route protection logic

### Pattern 4: Run Your Project

**Scenario 1**: Simple local development

```bash
# Run on default localhost:8550
fletx run

# Or specify a different entry point
fletx run app/main.py
```

**Scenario 2**: Web development with hot reload

```bash
# Open in browser + watch for file changes
fletx run --web --watch
```

When you save a file, the app automatically reloads—perfect for iterating on UI and logic.

**Scenario 3**: Debug mode with logging

```bash
# Enable verbose output + debug mode
fletx run --debug --verbose
```

This shows internal logs, making it easier to diagnose issues.

**Scenario 4**: Desktop or mobile testing

```bash
# Desktop app (native window)
fletx run --desktop

# Or open on Android/iOS device (requires device connection)
fletx run --android
```

**Scenario 5**: Environment-specific configuration

```bash
# Set environment variables for your app
fletx run --env API_URL=https://api.example.com --env DEBUG=true

# Or use a .env-like file
fletx run --env-file .env.development
```

Your FletX app can read these via `os.environ.get()`.

### Pattern 5: Run Tests

**Scenario 1**: Quick test verification

```bash
# Run all tests
fletx test
```

**Scenario 2**: Run specific test file

```bash
fletx test tests/controllers/test_user_controller.py
```

**Scenario 3**: Run tests matching a keyword

```bash
# Only tests with "user" in the name
fletx test -k "user"
```

**Scenario 4**: Generate a coverage report

```bash
# See which lines are covered by tests
fletx test --coverage
```

**Scenario 5**: Debug test failures interactively

```bash
# Drop into debugger on failure
fletx test --pdb
```

---

## Real-World Example: Build a Todo App

Let's build a minimal todo app step-by-step using the CLI:

### Step 1: Create the project

```bash
fletx new todo_app \
  --author "Developer" \
  --description "A simple todo list app"

cd todo_app
```

### Step 2: Generate core components

```bash
# Create the main controller for todos
fletx generate controller TodoList --with-test

# Create a service to handle storage
fletx generate service TodoStorage --with-test

# Create the main page
fletx generate page Home
```

### Step 3: Examine generated code

```bash
# Look at the controller structure
cat app/controllers/todo_list_controller.py

# Look at the service
cat app/services/todo_storage_service.py

# Look at the page
cat app/pages/home_page.py
```

Each file has the correct imports and basic structure ready for you to fill in logic.

### Step 4: Implement logic (you edit the files)

In `app/controllers/todo_list_controller.py`:

```python
from fletx.core import FletXController, create_rx_string, create_rx_list

class TodoListController(FletXController):
    def __init__(self):
        self.todos = create_rx_list([])
        self.input_value = create_rx_string("")
    
    def add_todo(self, text):
        self.todos.add({"id": len(self.todos), "text": text, "done": False})
        self.input_value.set("")
    
    def toggle_todo(self, todo_id):
        for todo in self.todos:
            if todo["id"] == todo_id:
                todo["done"] = not todo["done"]
        self.todos.refresh()
```

### Step 5: Run with hot reload

```bash
# Start the app with auto-reload
fletx run --web --watch

# Browser opens automatically
# Edit controllers/pages, save, and see changes instantly
```

### Step 6: Test your controller

```bash
# Generate and run tests
fletx test --coverage

# See which parts of your code are tested
```

---

## Common CLI Workflows

### Workflow 1: Rapid Prototyping

```bash
# Start fresh
fletx new proto --no-install

# Generate pieces quickly
fletx generate page Dashboard
fletx generate controller Dashboard
fletx generate service ApiClient

# Run and iterate
fletx run --web --watch --debug
```

### Workflow 2: Team Collaboration

```bash
# Use shared template (if available)
fletx new project_name --template team-standard

# Generate consistent components
fletx generate controller UserAuth --with-test
fletx generate service UserAuthService --with-test

# Test and commit
fletx test
git add .
git commit -m "Add user auth"
```

### Workflow 3: CI/CD Integration

```bash
# In your CI pipeline:

# Install and test
pip install -r requirements.txt
fletx test --coverage

# Check compatibility
fletx check --json
```

---

## CLI Reference: Complete Options

### `fletx new <name>`

| Option | Type | Default | Purpose |
|--------|------|---------|---------|
| `--template` | string | `project` | Choose project template |
| `--directory` | path | current dir | Where to create the project |
| `--author` | string | `$USER` | Project author name |
| `--description` | string | Generated | Project description |
| `--version` | string | `0.1.0` | Initial version |
| `--python-version` | string | `3.12` | Min Python version |
| `--overwrite` | flag | false | Overwrite existing files |
| `--no-install` | flag | false | Skip dependency installation |

### `fletx generate <type> <name>`

| Type | Purpose | Output |
|------|---------|--------|
| `controller` | Reactive state + logic | `app/controllers/<name>_controller.py` |
| `service` | Utility class | `app/services/<name>_service.py` |
| `page` | Full screen | `app/pages/<name>_page.py` |
| `component` | Reusable widget | `app/components/<name>_component.py` |
| `middleware` | Route interceptor | `app/middlewares/<name>_middleware.py` |
| `guard` | Route protection | `app/guards/<name>_guard.py` |

**Options**:

| Option | Type | Purpose |
|--------|------|---------|
| `--output-dir` | path | Custom output directory |
| `--template` | string | Specific template name |
| `--overwrite` | flag | Overwrite existing component |
| `--with-test` | flag | Generate test file automatically |

### `fletx run [target]`

| Option | Type | Default | Purpose |
|--------|------|---------|---------|
| `--host` or `-h` | string | `localhost` | Bind address |
| `--port` or `-p` | int | `8550` | Port number |
| `--debug` | flag | false | Enable debug logging |
| `--watch` or `-W` | flag | false | Auto-reload on file changes |
| `--web` or `-w` | flag | false | Open in browser |
| `--desktop` or `-d` | flag | false | Force desktop mode |
| `--android` or `-A` | flag | false | Deploy to Android |
| `--ios` or `-X` | flag | false | Deploy to iOS |
| `--env` or `-e` | string | - | Set env var (`KEY=VALUE`) |
| `--install-deps` or `-r` | flag | false | Install requirements first |
| `--verbose` or `-v` | flag | false | Verbose logging |

### `fletx test [path]`

| Option | Type | Purpose |
|--------|------|---------|
| `-k` / `--keyword` | string | Run tests matching keyword |
| `-v` / `--verbose` | flag | Verbose output |
| `--coverage` | flag | Generate coverage report |
| `--pdb` | flag | Debug on failure |

---

## Best Practices

| Practice | Why | How |
|----------|-----|-----|
| **Use templates for consistency** | Ensures all projects follow your team's architecture | `fletx new app --template team-standard` |
| **Generate with tests** | Catches bugs early and documents expected behavior | `fletx generate controller X --with-test` |
| **Use `--watch` during development** | Immediate feedback speeds up iteration | `fletx run --web --watch` |
| **Test before committing** | Prevents broken code in the repository | `fletx test` in git hooks or CI |
| **Use `--env` for sensitive config** | Avoids hardcoding secrets | `--env API_KEY=$SECRET_KEY` |
| **Version your Python requirement** | Prevents compatibility issues across machines | `--python-version 3.11` in `new` command |

---

## Troubleshooting

### "Project already exists"

```bash
# Use --overwrite to replace
fletx new my_project --overwrite

# Or specify different directory
fletx new my_project --directory ./projects/new_app
```

### "Template not found"

```bash
# Check available templates
fletx --help

# Use explicit template name
fletx new app --template project
```

### "Port 8550 already in use"

```bash
# Run on a different port
fletx run --port 8551
```

### "Module not found when running"

```bash
# Install dependencies first
fletx run --install-deps

# Or manually
pip install -r requirements.txt
```

### "Tests don't run"

```bash
# Install test dependencies
pip install pytest pytest-cov

# Then run
fletx test -v
```

---

## Common Pitfalls

**Pitfall 1**: Generating a component that already exists (overwrites your code)

```bash
# Safe: use --with-test only, don't --overwrite
fletx generate controller Widget --with-test

# Risky: --overwrite deletes your edits!
# fletx generate controller Widget --overwrite
```

**Pitfall 2**: Running `fletx run` from the wrong directory

```bash
# Wrong: run from outside project
$ cd ~ && fletx run

# Correct: run from project root
$ cd my_project && fletx run
```

**Pitfall 3**: Forgetting `--watch` during active development

```bash
# Tedious: manually restart after each save
$ fletx run

# Better: auto-reload on save
$ fletx run --web --watch
```

---

## Next Steps

- **[Architecture](architecture.md)**: Understand how controllers, pages, and services connect
- **[Controllers](controllers.md)**: Learn to build reactive state and business logic
- **[Pages](pages.md)**: Create screens and handle navigation
- **[Services](services.md)**: Build reusable utilities and integrations
- **[Dependency Injection](dependency-injection.md)**: Manage component dependencies elegantly
- **[State Management](state-management.md)**: Use reactive primitives (RxInt, RxList, etc.)
- **[Decorators](decorators.md)**: Control execution timing and memoization
