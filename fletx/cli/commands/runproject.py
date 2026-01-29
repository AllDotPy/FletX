"""
Command to run FletX projects.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, List

from fletx.cli.commands import (
    BaseCommand, CommandParser
)
from fletx.utils.exceptions import (
    CommandExecutionError, # ProjectError
)


class RunCommand(BaseCommand):
    """Run a FletX project with various options."""
    
    command_name = "run"
    
    def add_arguments(self, parser: CommandParser) -> None:
        """Add arguments specific to the run command."""

        parser.add_argument(
            "target",
            nargs = "?",
            default = "main.py",
            help = "Python file to run (default: main.py)"
        )
        parser.add_argument(
            "-h",
            "--host",
            default = "localhost",
            help = "Host to bind to (default: localhost)"
        )
        parser.add_argument(
            "-p",
            "--port",
            type = int,
            default = 8550,
            help = "Port to bind to (default: 8550)"
        )
        parser.add_argument(
            "--debug",
            action = "store_true",
            help = "Run in debug mode"
        )
        parser.add_argument(
            "-W",
            "--watch",
            action = "store_true",
            help = "Enable recursive script directory watch for hot reload in development"
        )
        parser.add_argument(
            "-w",
            "--web",
            action = "store_true",
            help = "Open app in a web browser"
        )
        parser.add_argument(
            "-d",
            "--desktop",
            action = "store_true",
            help = "Force desktop mode"
        )
        parser.add_argument(
            "-A",
            "--android",
            action = "store_true",
            help = "Open app on Android divice"
        )
        parser.add_argument(
            "-X",
            "--ios",
            action = "store_true",
            help = "Open app on iOS divice"
        )
        parser.add_argument(
            "--assets-dir",
            help = "Path to assets directory"
        )
        parser.add_argument(
            "--ignore-dir",
            help = "Path to upload directory"
        )
        parser.add_argument(
            "-e",
            "--env",
            action = "append",
            help = "Environment variables in KEY=VALUE format"
        )
        parser.add_argument(
            "-r",
            "--requirements",
            help = "Path to requirements.txt file"
        )
        parser.add_argument(
            "--install-deps",
            action = "store_true",
            help = "Install dependencies before running"
        )
        parser.add_argument(
            "-v",
            "--verbose",
            action = "store_true",
            help = "Verbose output"
        )
    
    def handle(self, **kwargs) -> None:
        """Handle the run command."""

        target = kwargs.get("target", "main.py")
        host = kwargs.get("host", "localhost")
        port = kwargs.get("port", 8550)
        debug = kwargs.get("debug", False)
        watch = kwargs.get("watch", False)
        web = kwargs.get("web", False)
        desktop = kwargs.get("desktop", False)
        android = kwargs.get("android", False)
        ios = kwargs.get("ios", False)
        assets_dir = kwargs.get("assets_dir")
        ignore_dir = kwargs.get("ignore_dir")
        env_vars = kwargs.get("env", [])
        requirements = kwargs.get("requirements")
        install_deps = kwargs.get("install_deps", False)
        verbose = kwargs.get("verbose", False)
        
        # Validate project structure
        self._validate_project()
        
        # Find target file
        target_path = self._find_target_file(target)
        
        # Install dependencies if requested
        if install_deps:
            self._install_dependencies(requirements)
        
        # Prepare environment variables
        env = self._prepare_environment(env_vars, debug, verbose)
        
        # Build command arguments
        cmd_args = self._build_command_args(
            target_path, host, port, debug, watch, web, desktop, android,
            ios, assets_dir, ignore_dir
        )
        
        # Run the project
        self._run_project(cmd_args, env, verbose)
    
    def _validate_project(self) -> None:
        """Validate that we're in a valid FletX project."""

        current_dir = Path.cwd()
        
        # Check for project markers
        project_markers = [
            ".fletx/config.json",
            "fletx.json",
            "requirements.txt",
            "main.py"
        ]
        
        has_marker = any((current_dir / marker).exists() for marker in project_markers)
        
        if not has_marker:
            print("Warning: This doesn't appear to be a FletX project directory.")
            print(
                "Expected to find one of: .fletx/config.json, "
                "fletx.json, requirements.txt, or main.py"
            )
    
    def _find_target_file(self, target: str) -> Path:
        """Find and validate the target file to run."""

        target_path = Path(target)
        
        # If target is not absolute, make it relative to current directory
        if not target_path.is_absolute():
            target_path = Path.cwd() / target_path
        
        # Check if file exists
        if not target_path.exists():
            # Try some common alternatives
            alternatives = [
                Path.cwd() / "main.py",
                Path.cwd() / "app.py",
                Path.cwd() / "run.py",
                Path.cwd() / f"{target}.py"
            ]
            
            for alt in alternatives:
                if alt.exists():
                    print(f"Target '{target}' not found, using '{alt.name}' instead.")
                    return alt
            
            raise CommandExecutionError(f"Target file '{target}' not found.")
        
        # Check if it's a Python file
        if target_path.suffix != ".py":
            raise CommandExecutionError(
                f"Target file '{target}' is not a Python file."
            )
        
        return target_path
    
    def _install_dependencies(
        self, 
        requirements_path: Optional[str]
    ) -> None:
        """Install project dependencies."""

        if requirements_path:
            req_file = Path(requirements_path)
        else:
            # Look for requirements.txt in common locations
            possible_locations = [
                Path.cwd() / "requirements.txt",
                Path.cwd() / "requirements" / "requirements.txt",
                Path.cwd() / "deps" / "requirements.txt"
            ]
            
            req_file = None
            for location in possible_locations:
                if location.exists():
                    req_file = location
                    break
        
        if not req_file or not req_file.exists():
            print("No requirements.txt found, skipping dependency installation.")
            return
        
        print(f"Installing dependencies from {req_file}...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(req_file)
            ], check=True)
            print("Dependencies installed successfully.")

        except subprocess.CalledProcessError as e:
            raise CommandExecutionError(
                f"Failed to install dependencies: {e}"
            )
    
    def _prepare_environment(
        self, 
        env_vars: List[str], 
        debug: bool, 
        verbose: bool
    ) -> dict:
        """Prepare environment variables for the subprocess."""

        env = os.environ.copy()
        
        # Add custom environment variables
        if env_vars:
            for env_var in env_vars:
                if "=" not in env_var:
                    print(f"Warning: Invalid environment variable format: {env_var}")
                    continue
                
                key, value = env_var.split("=", 1)
                env[key] = value
        
        # Set debug mode
        if debug:
            env["FLETX_DEBUG"] = "1"
            env["FLET_DEBUG"] = "1"
        
        # Set verbose mode
        if verbose:
            env["FLETX_VERBOSE"] = "1"
        
        return env
    
    def _build_command_args(
        self, target_path: Path, host: str, port: int, debug: bool,
        watch: bool, web: bool, desktop: bool, android: bool, ios: bool,
        assets_dir: Optional[str], ignore_dir: Optional[str],
    ) -> List[str]:
        """Build the command arguments for running the project."""

        cmd_args = ['flet', str(target_path)]
        
        # Add Flet-specific arguments if the target file uses them
        flet_args = []

        if watch:
            flet_args.append("-r")
        
        if host != "localhost":
            flet_args.extend(["--host", host])
        
        if port != 8550:
            flet_args.extend(["--port", str(port)])
        
        if web:
            flet_args.append("--web")

        elif desktop:
            # No thing to do, flet will launch the app in a window by default
            # flet_args.append("")
            pass

        if android:
            flet_args.append("--android")

        elif ios:
            flet_args.append("--ios")
        
        if assets_dir:
            flet_args.extend(["--assets", assets_dir])
        
        if ignore_dir:
            flet_args.extend(["--upload-dir", ignore_dir])
        
        # Check if the target file supports these arguments
        if self._supports_flet_args(target_path):
            cmd_args.extend(flet_args)
        
        return cmd_args
    
    def _supports_flet_args(self, target_path: Path) -> bool:
        """Check if the target file supports Flet command-line arguments."""

        try:
            content = target_path.read_text(encoding="utf-8")
            # Simple heuristic: check if file uses flet.app or similar patterns
            patterns = ["flet.app", "ft.app", "flet_fastapi", "flet_django", "FletXApp"]

            return any(pattern in content for pattern in patterns)
        
        except Exception:
            return False
    
    def _run_project(
        self, 
        cmd_args: List[str], 
        env: dict, 
        verbose: bool
    ) -> None:
        """Run the project with the given arguments."""

        if verbose:
            print(f"Running command: {' '.join(cmd_args)}")
            print(f"Working directory: {Path.cwd()}")
        
        try:
            print("Starting FletX application...")
            print(f"Target: {cmd_args[1]}")
            print("\nPress Ctrl+C to stop the application.")
            print("-" * 50)
            
            # Run the subprocess
            process = subprocess.Popen(
                cmd_args,
                env = env,
                cwd = Path.cwd()
            )
            
            # Wait for the process to complete
            process.wait()
            
        except KeyboardInterrupt:
            print("\nStopping application...")
            if process:
                process.terminate()
                process.wait()

        except subprocess.CalledProcessError as e:
            raise CommandExecutionError(
                f"Failed to run project: {e}"
            )
        
        except Exception as e:
            raise CommandExecutionError(
                f"Unexpected error while running project: {e}"
            )
    
    def get_description(self) -> str:
        """Get the command description."""
        return "Run a FletX project with various configuration options."
    
    def get_missing_args_message(self) -> str:
        """Get the missing arguments message."""
        return "No target specified, will try to run main.py"
