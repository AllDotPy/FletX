from argparse import (
    Namespace, ArgumentParser
)
from functools import partial
from abc import ABC
from importlib.util import find_spec
from typing import ClassVar, Dict, Type, List

from fletx.utils.exceptions import (
    CommandError, CommandExecutionError,
    CommandNotFoundError
)


####
##    COMMAND REGISTRY
#####
class CommandRegistry:
    """
    Registry for all commands in the FletX CLI.
    This class is responsible for storing and managing all available commands.
    It provides methods to register new commands and retrieve existing ones.
    """

    _commands: ClassVar[Dict[str, Type["BaseCommand"]]] = {} # type: ignore

    @classmethod
    def register(cls, name: str, command_cls: Type["BaseCommand"]) -> None: # type: ignore
        """Register a new command class."""
        cls._commands[name] = command_cls

    @classmethod
    def get(cls, name: str) -> Type["BaseCommand"]: # type: ignore
        """Get a command class by its name."""

        if name not in cls._commands:
            raise CommandNotFoundError(f"Command '{name}' not found.")
        return cls._commands[name]

    @classmethod
    def all(cls) -> List[Type["BaseCommand"]]: # type: ignore
        """Get all registered command classes."""
        return list(cls._commands.values())
    

####
##    COMMAND PARSER
#####
class CommandParser(ArgumentParser):
    """
    Customized ArgumentParser class to improve error messages and prevent
    SystemExit in several occasions. SystemExit is unacceptable when a
    command is called programmatically.
    """

    def __init__(
        self, *, 
        missing_args_message = None, 
        called_from_command_line = None, 
        **kwargs
    ):
        self.missing_args_message = missing_args_message
        self.called_from_command_line = called_from_command_line
        super().__init__(**kwargs)

    def parse_args(self, args = None, namespace = None):
        """Parse the command line arguments and return a Namespace object."""

        # Catch missing argument for a better error message
        if self.missing_args_message and not (
            args or any(not arg.startswith("-") for arg in args)
        ):
            self.error(self.missing_args_message)
        return super().parse_args(args, namespace)

    def error(self, message):
        """
        Handle errors in a customized way.
        This method is called when an error occurs during argument parsing.
        It raises a CommandError instead of calling sys.exit().
        This allows for better error handling when the command is called
        programmatically.
        """

        # If called from command line, use the default error handling
        # to print the error message and exit
        # the program with a non-zero exit code.
        # Otherwise, raise a CommandError with the error message
        # to allow for better error handling in the calling code.
        # This is useful when the command is called programmatically
        # and we want to handle the error in a different way.

        if self.called_from_command_line:
            super().error(message)
        else:
            raise CommandError(f"Error: {message}")

    def add_subparsers(self, **kwargs):
        """
        Add subparsers to the parser.
        This method is called to add subparsers to the main parser.
        It allows for customizing the parser class used for the subparsers.
        If a custom parser class is provided, it will be used instead of
        the default ArgumentParser class.
        """

        # If a custom parser class is provided, use it instead of the default
        # ArgumentParser class. This allows for customizing the behavior
        # of the subparsers.
        # If the parser class is a subclass of CommandParser, pass the
        # called_from_command_line argument to the constructor.
        # This allows for better error handling when the command is called
        # programmatically.
        # Otherwise, use the default ArgumentParser class.
        # This is useful when the command is called from the command line
        # and we want to use the default error handling.

        parser_class = kwargs.get("parser_class", type(self))
        if issubclass(parser_class, CommandParser):
            kwargs["parser_class"] = partial(
                parser_class,
                called_from_command_line = self.called_from_command_line,
            )
        return super().add_subparsers(**kwargs)

    
####
##    COMMAND BASE CLASS
#####
class BaseCommand(ABC):
    """ 
    Base class for all commands in the FletX CLI.
    This class defines the basic structure and methods that all commands
    should implement. It provides a way to add arguments to the command
    parser and execute the command with the provided arguments.
    """

    command_name: str = ""

    def __init_subclass__(cls, *args, **kwargs):

        # Automatically register the command class in the registry
        if cls.command_name:
            CommandRegistry.register(cls.command_name, cls)
        
        super().__init_subclass__(**kwargs)

    def run_from_argv(self, argv: List[str]) -> None:
        """ 
        Execute the command with the provided arguments.
        This method is called when the command is executed from the command line.
        It parses the arguments and calls the execute method.
        """

        parser = self.create_parser()
        args = parser.parse_args(argv)
        self.execute(args)

    def create_parser(self) -> CommandParser:
        """ 
        Create and return the command parser.
        This method is called to create the argument parser for the command.
        It initializes the parser with the command's description and adds
        the arguments defined in the add_arguments method.
        """

        # Create a new parser instance
        # with the command's description and missing args message
        # (if any)
        parser = CommandParser(
            description = self.get_description(),
            missing_args_message = self.get_missing_args_message(),
            called_from_command_line = True,
        )
        self.add_arguments(parser)
        return parser

    def add_arguments(self, parser: CommandParser) -> None:
        """ 
        Add arguments to the command parser.
        This method is called to add the arguments that the command
        accepts. It should be overridden in the subclass to define
        the specific arguments for the command.
        """
        # This method should be overridden in the subclass
        # to define the specific arguments for the command.
        # It should use the parser instance to add the arguments
        # using the add_argument method.
        # For example:
        # parser.add_argument("--option", help="Description of the option")
        # This method is empty by default to allow for easy overriding
        # in the subclass. It should be implemented in the subclass
        # to define the specific arguments for the command.
        # This allows for better separation of concerns and makes
        # the code more modular and easier to maintain.
        # It also allows for better error handling when the command
        # is called programmatically and we want to handle the error
        # in a different way.

        pass

    def execute(self, args: Namespace) -> None:
        """ 
        Execute the command with the provided arguments.
        This method is called to execute the command after parsing
        the arguments. It calls the handle method with the parsed
        arguments.
        """
        # This method should be overridden in the subclass
        # to define the specific behavior of the command.
        # It should call the handle method with the parsed arguments
        # and any other necessary parameters.
        # For example:
        # self.handle(args.option)

        self.handle(**vars(args))

    def handle(self, *args, **kwargs) -> None:
        """ 
        Handle the command logic.
        This method is called to execute the command logic after
        parsing the arguments. It should be overridden in the subclass
        to define the specific behavior of the command.
        It should use the parsed arguments to perform the necessary
        actions and return the result.
        """
        # This method should be overridden in the subclass
        # to define the specific behavior of the command.
        # It should use the parsed arguments to perform the necessary
        # actions and return the result.
        # For example:
        # def handle(self, option):
        #     # Perform the necessary actions with the option
        #     print(f"Option: {option}")
        # This method is empty by default to allow for easy overriding
        # in the subclass. It should be implemented in the subclass
        # to define the specific behavior of the command.

        raise NotImplementedError("You must implement the 'handle' method.")

    def print_help(self) -> None:
        """ 
        Print the help message for the command.
        This method is called to print the help message for the command.
        It creates a new parser instance and calls the print_help method
        to display the help message.
        """

        parser = self.create_parser()
        parser.print_help()

    def get_description(self) -> str:
        """ Get the command description. """
        return self.__class__.__doc__ or ""

    def get_missing_args_message(self) -> str:
        return "Missing required arguments for this command."


####
##      TEMPLATE COMMAND CLASS
#####
class TemplateCommand(BaseCommand):
    """ Base class for template commands.
    Copy the template files into a specified directory.

    This class provides a way to create commands that generate
    templates files.
    """

    target_tpl_name: str = ""           # Example: "Component" or "Project" or "Module" etc...
    """ The target template name """

    def handle(self, *args, **kwargs) -> None:
        """ Handle the command logic for template commands.
        This method is called to execute the command logic after
        parsing the arguments. It should be overridden in the subclass
        to define the specific behavior of the command.
        """
        # This method should be overridden in the subclass
        # to define the specific behavior of the command.
        # It should use the parsed arguments to perform the necessary
        # actions and return the result.
        # For example:
        # def handle(self, option):
        #     # Perform the necessary actions with the option
        #     print(f"Option: {option}")

    def validate_name(self,name:str):
        """ Validate the name of the template. """

        # Check if the name is empty
        if not name:
            raise CommandExecutionError("Template name cannot be empty.")

        # Check if the name contains invalid characters
        if not name.isidentifier():
            raise CommandExecutionError(
                "Template name can only contain letters, numbers, and underscores."
            )
        
        # Check that __spec__ doesn't exist.
        if find_spec(name):
            raise CommandExecutionError(
                f"Template name '{name}' conflicts with the name of an existing Python module."
                f"You cannot use this as {self.target_tpl_name}."
                "Please choose a different name."
            )

        # Check if the name is too long
        if len(name) > 50:
            raise CommandExecutionError("Template name is too long.")
