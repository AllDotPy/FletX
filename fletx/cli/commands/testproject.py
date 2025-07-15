import pytest
from fletx.cli.commands.base import BaseCommand
from fletx.utils.exceptions import CommandExecutionError

class TestCommand(BaseCommand):
    """
    Run tests for the FletX project using pytest.
    """

    command_name = "test"

    def add_arguments(self, parser):
        """
        Add arguments for the test command.
        """
        parser.add_argument(
            "path",
            nargs="?",
            default=".",
            help="Path to the test file or directory (default: current directory)."
        )
        parser.add_argument(
            "-k",
            "--keyword",
            help="Run tests matching the given keyword expression."
        )
        parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="Enable verbose output."
        )
        parser.add_argument(
            "--coverage",
            action="store_true",
            help="Run tests with a coverage report (requires pytest-cov)."
        )
        parser.add_argument(
            "--pdb",
            action="store_true",
            help="Start the debugger on test failure."
        )

    def handle(self, path=".", keyword=None, verbose=False, coverage=False, pdb=False):
        """
        Handle the test command logic.
        """
        pytest_args = [path]

        if keyword:
            pytest_args.extend(["-k", keyword])
        if verbose:
            pytest_args.append("-v")
        if coverage:
            pytest_args.extend(["--cov", "."])
        if pdb:
            pytest_args.append("--pdb")

        try:
            exit_code = pytest.main(pytest_args)
            if exit_code != 0:
                raise CommandExecutionError("Some tests failed.")
        except Exception as e:
            raise CommandExecutionError(f"Error running tests: {e}")
