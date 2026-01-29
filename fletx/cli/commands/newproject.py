"""
Command to create new FletX projects.
"""

import os
from pathlib import Path

from fletx.cli.commands import (
    TemplateCommand, CommandParser
)
from fletx.utils.exceptions import (
    CommandExecutionError, #ProjectError
)
from fletx.cli.templates import (
    TemplateManager, #TemplateValidator
)
from fletx import __version__


class NewProjectCommand(TemplateCommand):
    """Create a new FletX project from template."""
    
    command_name = "new"
    target_tpl_name = "Project"
    
    def add_arguments(self, parser: CommandParser) -> None:
        """Add arguments specific to the newproject command."""
        parser.add_argument(
            "name",
            help="Name of the new project"
        )
        parser.add_argument(
            "-t",
            "--template",
            default="project",
            help="Template to use for the project (default: project)"
        )
        parser.add_argument(
            "-D",
            "--directory",
            help="Directory where the project should be created (default: current directory)"
        )
        parser.add_argument(
            "--author",
            help="Author name for the project"
        )
        parser.add_argument(
            "-d",
            "--description",
            help="Project description"
        )
        parser.add_argument(
            "-v",
            "--version",
            default="0.1.0",
            help="Initial project version (default: 0.1.0)"
        )
        parser.add_argument(
            "--python-version",
            default="3.12",
            help="Minimum Python version required (default: 3.12)"
        )
        parser.add_argument(
            "-W",
            "--overwrite",
            action="store_true",
            help="Overwrite existing files if they exist"
        )
        parser.add_argument(
            "-N",
            "--no-install",
            action="store_true",
            help="Don't install dependencies after creating the project"
        )
    
    def handle(self, **kwargs) -> None:
        """Handle the new project command."""

        name = kwargs.get("name")
        template = kwargs.get("template", "project")
        directory = kwargs.get("directory")
        author = kwargs.get("author", os.environ.get("USER", "Developer"))
        description = kwargs.get("description", f"A new FletX project: {name}")
        version = kwargs.get("version", "0.1.0")
        python_version = kwargs.get("python_version", "3.12")
        overwrite = kwargs.get("overwrite", False)
        no_install = kwargs.get("no_install", False)
        
        # Validate project name
        self.validate_name(name)
        
        # Determine target directory
        if directory:
            target_dir = Path(directory) / name
        else:
            target_dir = Path.cwd() / name
        
        # Check if project directory already exists
        if target_dir.exists() and not overwrite:
            if any(target_dir.iterdir()):
                raise CommandExecutionError(
                    f"Directory '{target_dir}' already exists and is not empty. "
                    "Use --overwrite to overwrite existing files."
                )
        
        # Initialize template manager
        template_manager = TemplateManager()
        
        # Check if template exists
        if not template_manager.template_exists(template):
            available_templates = template_manager.get_available_templates()
            raise CommandExecutionError(
                f"Template '{template}' not found. "
                f"Available templates: {', '.join(available_templates)}"
            )
        
        # Prepare context for template rendering
        context = {
            "project_name": name,
            "name": name,
            "author": author,
            "description": description,
            "version": version,
            "python_version": python_version,
            "fletx_version": __version__
        }
        
        try:
            # Generate project from template
            print(f"Creating new FletX project '{name}'...")
            template_manager.generate_from_template(
                template, target_dir, context, overwrite
            )
            
            print(f"\nProject '{name}' created successfully at: {target_dir}")
            
            # Create project configuration
            self._create_project_config(target_dir, context)
            
            # Install dependencies if requested
            if not no_install:
                self._install_dependencies(target_dir)
            
            # Print next steps
            self._print_next_steps(name, target_dir, no_install)
            
        except Exception as e:
            raise CommandExecutionError(f"Failed to create project: {e}")
    
    def _create_project_config(self, project_dir: Path, context: dict) -> None:
        """Create project configuration file."""

        config = {
            "name": context["project_name"],
            "version": context["version"],
            "author": context["author"],
            "description": context["description"],
            "python_version": context["python_version"],
            "fletx_version": __version__, # Actual version of FletX
        }
        
        # Create .fletx directory
        fletx_dir = project_dir / ".fletx"
        fletx_dir.mkdir(exist_ok=True)
        
        # Write configuration
        import json
        config_file = fletx_dir / "config.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        
        print(f"Created project configuration: {config_file}")
    
    def _install_dependencies(self, project_dir: Path) -> None:
        """Install project dependencies."""

        import subprocess
        import sys
        
        requirements_file = project_dir / "requirements.txt"
        if not requirements_file.exists():
            print("No requirements.txt found, skipping dependency installation.")
            return
        
        print("Installing dependencies...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], check = True, cwd = project_dir)
            print("Dependencies installed successfully.")

        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to install dependencies: {e}")
            print("You can install them manually using: pip install -r requirements.txt")
    
    def _print_next_steps(
        self, 
        project_name: str, 
        project_dir: Path, 
        no_install: bool
    ) -> None:
        """Print next steps for the user."""

        print("\n{'='*50}")
        print("🎉 Project created successfully!")
        print("{'='*50}")
        print("\nNext steps:")
        print("  1. cd {project_dir.name}")
        
        if no_install:
            print("  2. pip install -r requirements.txt")
            print("  3. fletx run")
        else:
            print("  2. fletx run")
        
        print("\nProject structure:")
        self._print_project_structure(project_dir)
    
    def _print_project_structure(
        self, 
        project_dir: Path, 
        max_depth: int = 2
    ) -> None:
        """Print a simple project structure."""

        def _print_tree(path: Path, prefix: str = "", depth: int = 0):
            if depth > max_depth:
                return
            
            items = sorted([p for p in path.iterdir() if not p.name.startswith('.')])
            for i, item in enumerate(items):
                is_last = i == len(items) - 1
                current_prefix = "└── " if is_last else "├── "
                print(f"{prefix}{current_prefix}{item.name}")
                
                if item.is_dir() and depth < max_depth:
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    _print_tree(item, next_prefix, depth + 1)
        
        print(f"{project_dir.name}/")
        _print_tree(project_dir)
    
    def get_missing_args_message(self) -> str:
        """Get the missing arguments message."""
        return "You must provide a project name. Usage: fletx newproject <name>"
