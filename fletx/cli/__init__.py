#!/usr/bin/env python3
"""
FletX CLI - A command-line tool for managing Flet projects with GetX-like architecture.
"""

import sys
import os
from typing import List, Optional
from pathlib import Path

from fletx.utils.exceptions import (
    CommandError, CommandExecutionError,
    CommandNotFoundError
)
from fletx.utils import (
    import_module_from
)
from fletx.cli.commands import (
    CommandRegistry, CommandParser,
    BaseCommand, CommandRegistry, TestCommand
)

# Add the current directory to the Python path to allow imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

__all__ = [
    'CommandRegistry',
    'CommandParser',
    'BaseCommand',
    'FletXCLI'
]


####
##      FLETX CLI ENTRY POINT
#####
class FletXCLI:
    """
    Main CLI class that handles command routing and execution.
    """
    
    def __init__(self):
        # Import all command modules to trigger registration
        self._discover_commands()
    
    def _discover_commands(self):
        """Discover and import all command modules."""

        commands_dir = Path(__file__).parent / "commands"
        
        for file_path in commands_dir.glob("*.py"):
            if file_path.name != "__init__.py" and file_path.name != "base.py":
                module_name = file_path.stem
                try:
                    import_module_from(f"fletx.cli.commands.{module_name}")
                except ImportError as e:
                    print(
                        f"Warning: Could not import command module '{module_name}': {e}"
                    )
    
    def execute_from_command_line(
        self, 
        argv: Optional[List[str]] = None
    ):
        """
        Execute a command from the command line arguments.
        
        Args:
            argv: List of command line arguments. If None, uses sys.argv.
        """

        if argv is None:
            argv = sys.argv[1:]
        
        if not argv:
            self.print_help()
            return
        
        command_name = argv[0]
        command_args = argv[1:]
        
        try:
            # Special handling for help command
            if command_name in ['-h', '--help', 'help']:
                if command_args:
                    self.print_command_help(command_args[0])
                else:
                    self.print_help()
                return
            
            # Get and execute the command
            command_class = CommandRegistry.get(command_name)
            command_instance = command_class()
            command_instance.run_from_argv(command_args)
            
        # Command not found
        except CommandNotFoundError:
            print(f"Error: Unknown command '{command_name}'")
            print("Type 'fletx help' for usage information.")
            sys.exit(1)

        # Command Error
        except CommandError as e:
            print(str(e))
            sys.exit(1)
        
        # Execution Error
        except CommandExecutionError as e:
            print(f"Execution Error: {e}")
            sys.exit(1)

        # Keyboard Interuption
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            sys.exit(1)
        
        # Unexpected Errors
        except Exception as e:
            print(f"Unexpected error: {e}")
            sys.exit(1)
    
    def print_help(self):
        """Print the main help message."""

        print("FletX - A command-line tool for managing Flet projects")
        print()
        print("Usage:")
        print("     fletx <command> [options]")
        print()
        print("Available commands:")
        
        commands = CommandRegistry.all()
        if not commands:
            print("     No commands available.")
            return
        
        # Group commands by category
        project_commands = []
        component_commands = []
        utility_commands = []
        
        for command_class in commands:
            command_name = getattr(command_class, 'command_name', '')
            description = self._get_short_description(command_class)
            
            # Projects Command
            if 'project' in command_name or command_name in ['new', 'init']:
                project_commands.append((command_name, description))
            
            # Components Commands
            elif 'generate' in command_name or command_name in [
                'component', 'module', 'controller', 'service'
            ]:
                component_commands.append((command_name, description))

            # Utilities
            else:
                utility_commands.append((command_name, description))
        
        if project_commands:
            print("\n  Project Management:")
            for name, desc in sorted(project_commands):
                print(f"    {name:<15} {desc}")
        
        if component_commands:
            print("\n  Code Generation:")
            for name, desc in sorted(component_commands):
                print(f"    {name:<15} {desc}")
        
        if utility_commands:
            print("\n  Utilities:")
            for name, desc in sorted(utility_commands):
                print(f"    {name:<15} {desc}")
        
        print()
        print("For help on a specific command, use:")
        print("  fletx <command> --help")
        print("  fletx help <command>")
    
    def print_command_help(self, command_name: str):
        """Print help for a specific command."""

        try:
            command_class = CommandRegistry.get(command_name)
            command_instance = command_class()
            command_instance.print_help()
        except CommandNotFoundError:
            print(f"Error: Unknown command '{command_name}'")
            print("Type 'fletx help' for a list of available commands.")
    
    def _get_short_description(self, command_class) -> str:
        """Extract a short description from the command's docstring."""
        
        doc = command_class.__doc__ or ""
        lines = doc.strip().split('\n')
        return lines[0].strip() if lines else "No description available"
