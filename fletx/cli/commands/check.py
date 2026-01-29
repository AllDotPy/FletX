"""
Command to check version compatibility between FletX and Flet.
"""

import sys

from fletx.cli.commands import (
    BaseCommand, CommandParser
)
from fletx.utils.version_checker import (
    VersionChecker, CompatibilityResult
)


class CheckCommand(BaseCommand):
    """Check version compatibility between FletX and Flet."""
    
    command_name = "check"
    
    def add_arguments(self, parser: CommandParser) -> None:
        """Add arguments specific to the check command."""
        parser.add_argument(
            "--json",
            action="store_true",
            help="Output results in JSON format"
        )
        parser.add_argument(
            "--quiet",
            action="store_true",
            help="Only output errors and warnings"
        )
        parser.add_argument(
            "--exit-code",
            action="store_true",
            help="Exit with non-zero code if incompatible"
        )
    
    def handle(self, **kwargs) -> None:
        """Handle the check command."""
        
        json_output = kwargs.get("json", False)
        quiet = kwargs.get("quiet", False)
        exit_code = kwargs.get("exit_code", False)
        
        try:
            # Initialize version checker
            checker = VersionChecker()
            
            # Perform compatibility check
            result = checker.check_compatibility()
            
            # Output results
            if json_output:
                self._output_json(result)
            else:
                self._output_human_readable(result, quiet)
            
            # Exit with appropriate code
            if exit_code and not result.is_compatible:
                sys.exit(1)
                
        except Exception as e:
            error_msg = f"Failed to check version compatibility: {e}"
            if json_output:
                self._output_json_error(error_msg)
            else:
                print(f"[ERROR] {error_msg}")
            
            if exit_code:
                sys.exit(1)
    
    def _output_human_readable(self, result: CompatibilityResult, quiet: bool) -> None:
        """Output results in human-readable format."""
        
        if not quiet:
            print("FletX Version Compatibility Check")
            print("=" * 40)
            print()
        
        # Main compatibility status
        if result.is_compatible:
            print(f"[OK] {result.fletx_version} is compatible with {result.flet_version}")
        else:
            print(f"[ERROR] {result.fletx_version} is not compatible with {result.flet_version}")
        
        # Additional message
        if result.message:
            print(f"\n[INFO] {result.message}")
        
        # Suggestions
        if result.suggestions:
            if not quiet:
                print("\n[SUGGESTIONS]")
            for suggestion in result.suggestions:
                print(f"   - {suggestion}")
        
        # Version details (if not quiet)
        if not quiet:
            print("\nVersion Details:")
            print(f"   FletX: {result.fletx_version.version_str}")
            print(f"   Flet:  {result.flet_version.version_str}")
            
            try:
                python_version = VersionChecker().get_python_version()
                print(f"   Python: {python_version.version_str}")
            except:  # noqa: E722
                pass
    
    def _output_json(self, result: CompatibilityResult) -> None:
        """Output results in JSON format."""
        import json
        
        output = {
            "compatible": result.is_compatible,
            "fletx_version": result.fletx_version.version_str,
            "flet_version": result.flet_version.version_str,
            "message": result.message,
            "suggestions": result.suggestions
        }
        
        try:
            python_version = VersionChecker().get_python_version()
            output["python_version"] = python_version.version_str
        except:  # noqa: E722
            output["python_version"] = "unknown"
        
        print(json.dumps(output, indent=2))
    
    def _output_json_error(self, error_msg: str) -> None:
        """Output error in JSON format."""
        import json
        
        output = {
            "compatible": False,
            "error": error_msg,
            "fletx_version": "unknown",
            "flet_version": "unknown",
            "python_version": "unknown",
            "message": error_msg,
            "suggestions": []
        }
        
        print(json.dumps(output, indent=2))
    
    def get_description(self) -> str:
        """Get the command description."""
        return "Check version compatibility between FletX and Flet packages."
    
    def get_missing_args_message(self) -> str:
        """Get the missing arguments message."""
        return None
