## Introduction

The **FletX CLI** (`fletx`) is a command-line tool that makes it easy to manage **FletX** projects. It lets you:

* Create a new FletX project
* Generate components (controllers, services, pages, etc.)
* Run your project with various options

---

## Main command

```bash
fletx <command> [options]
```

---

## Available commands

| Category               | Command    | Description                                          |
| ---------------------- | ---------- | ---------------------------------------------------- |
| **Project Management** | `new`      | Create a new FletX project from template             |
| **Code Generation**    | `generate` | Generate components like controllers, services, etc. |
| **Utilities**          | `run`      | Run a FletX project with various options             |
| **Testing**            | `test`     | Run tests for your FletX project                     |


👉 **Specific help :**

```bash
fletx <command> --help
fletx help <command>
```

---

## `fletx new`

Create a new FletX project.

```bash
fletx new <project_name> [options]
```

### Options

| Option                            | Description                                           | Default           |
| --------------------------------- | ----------------------------------------------------- | ----------------- |
| `--template TEMPLATE`             | Template to use for the project                       | `project`         |
| `--directory DIRECTORY`           | Directory where the project will be created           | current directory |
| `--author AUTHOR`                 | Author name for the project                           |                   |
| `--description DESCRIPTION`       | Project description                                   |                   |
| `--version VERSION`               | Initial version of the project                        | `0.1.0`           |
| `--python-version PYTHON_VERSION` | Minimum required Python version                       | `3.12`            |
| `--overwrite`                     | Overwrite existing files if they exist                |                   |
| `--no-install`                    | Don't install dependencies after creating the project |                   |

---

## `fletx generate`

Generate a component for your project.

```bash
fletx generate <type> <name> [options]
```

where `<type>` can be: `controller`, `service`, `model`, `component`, `page`

### Options

| Option                    | Description                            | Default       |
| ------------------------- | -------------------------------------- | ------------- |
| `--output-dir OUTPUT_DIR` | Output directory                       | based on type |
| `--template TEMPLATE`     | Specific template to use               | based on type |
| `--overwrite`             | Overwrite existing files               |               |
| `--with-test`             | Generate a test file for the component |               |

---

## `fletx run`

Run your FletX project.

```bash
fletx run [target] [options]
```

where `target` is the Python file to run (default: `main.py`)

### Options

| Option                        | Description                         | Default     |
| ----------------------------- | ----------------------------------- | ----------- |
| `--host HOST`                 | Host to bind to                     | `localhost` |
| `--port PORT`                 | Port to bind to                     | `8550`      |
| `--debug`                     | Run in debug mode                   |             |
| `--watch`                     | Enable hot reload (directory watch) |             |
| `--web`                       | Open in a web browser               |             |
| `--desktop`                   | Force desktop mode                  |             |
| `--android`                   | Open on an Android device           |             |
| `--ios`                       | Open on an iOS device               |             |
| `--assets-dir ASSETS_DIR`     | Path to assets directory            |             |
| `--ignore-dir IGNORE_DIR`     | Path to ignore directory            |             |
| `--env ENV`                   | Environment variables `KEY=VALUE`   |             |
| `--requirements REQUIREMENTS` | Path to `requirements.txt` file     |             |
| `--install-deps`              | Install dependencies before running |             |
| `--verbose`                   | Verbose output                      |             |

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

## `fletx test`

Run tests for your FletX project.

```bash
fletx test [options]
```

### Examples

```bash
fletx test                      # Run all tests
fletx test ./tests/test_api.py  # Run a specific test file
fletx test -k "MyTestClass"     # Run tests matching a keyword
fletx test -v                   # Verbose output
fletx test --coverage           # Run tests with coverage report
fletx test --pdb                # Debug on test failure
```

---

## 🧠 Next Steps

* Learn about the [Architecture](architecture.md)
* Explore [reactive UI binding](ui/reactivity.md)
* Dive into [dependency injection](guides/dependency-injection.md)
