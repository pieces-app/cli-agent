from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Self
import argparse
from pieces.settings import Settings
import sys


class BaseCommand(ABC):
    """Base class for all CLI commands with enhanced metadata support."""

    commands: List[Self] = []
    _is_command_group = False

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not getattr(cls, "_is_command_group", False):
            cls.instance = cls()

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        if not getattr(instance, "_is_command_group", False):
            cls.commands.append(instance)
        return instance

    def __init__(self):
        if self._is_command_group:
            self.__class__.instance = self
        self.name: str = self.get_name()
        self.aliases: List[str] = self.get_aliases()
        self.help: str = self.get_help()
        self.description: str = self.get_description()
        self.examples: List[str] = self.get_examples()
        self.docs: str = self.get_docs()

    def command_func(self, *args, **kwargs):
        return_code = self.execute(*args, **kwargs)
        if not Settings.run_in_loop:
            sys.exit(return_code)
        return return_code

    @abstractmethod
    def get_name(self) -> str:
        """Return the primary command name."""
        pass

    def get_aliases(self) -> List[str]:
        """Return alternative names for this command."""
        return []

    @abstractmethod
    def get_help(self) -> str:
        """Return a short help message for the command."""
        pass

    def get_description(self) -> str:
        """Return a detailed description for the command."""
        return self.get_help()  # Default to help text if no description provided

    def get_examples(self) -> List[str]:
        """Return a list of usage examples."""
        return []

    def get_docs(self) -> str:
        """Return extended documentation for the command."""
        return ""

    @abstractmethod
    def add_arguments(self, parser: argparse.ArgumentParser):
        """Add command-specific arguments to the parser."""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> int:
        """Execute the command with the given arguments.

        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        pass


class CommandGroup(BaseCommand):
    """Base class for commands that have subcommands."""

    _is_command_group = True
    instance: Self = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.instance = cls()
        cls.commands.append(cls.instance)

    def __init__(self):
        super().__init__()
        self.subcommands: Dict[str, BaseCommand] = {}
        self._register_subcommands()

    @abstractmethod
    def _register_subcommands(self):
        """Register all subcommands for this group."""
        pass

    def add_subcommand(self, command: BaseCommand):
        """Add a subcommand to this group."""
        self.subcommands[command.name] = command
        for alias in command.aliases:
            self.subcommands[alias] = command

    def execute(self, **kwargs) -> int:
        """Default execution for command groups - show help."""
        self.parser.print_help()
        return 0

    def add_arguments(self, parser: argparse.ArgumentParser):
        """Add subparsers for command groups."""
        self.parser = parser
        subparsers = parser.add_subparsers(dest=self.name)

        for cmd_name, command in self.subcommands.items():
            # Skip aliases
            if cmd_name != command.name:
                continue

            subparser = subparsers.add_parser(
                command.name,
                aliases=command.aliases,
                help=command.help,
                description=command.description,
                command_object=command,
            )

            command.add_arguments(subparser)
            subparser.set_defaults(func=command.command_func)
