from typing import Dict, List, Optional
from pieces.base_command import BaseCommand
from pieces.command_interface.mcp_command_group import MCPCommandGroup
from pieces.pieces_argparser import PiecesArgparser
from argparse import _SubParsersAction


class CommandRegistry:
    """Registry for managing all CLI commands."""

    def __init__(self, parser: PiecesArgparser):
        self.commands: Dict[str, BaseCommand] = {}
        self.parser: PiecesArgparser = parser
        self.command_subparser: _SubParsersAction[PiecesArgparser]

    def register(self, command: BaseCommand):
        """Register a command and its aliases."""
        self.commands[command.name] = command
        for alias in command.aliases:
            self.commands[alias] = command

        command_parser = self.command_subparser.add_parser(
            command.name,
            description=command.description,
            help=command.help,
            aliases=command.aliases,
            command_object=command,
        )
        command_parser.set_defaults(func=command.command_func)
        command.add_arguments(command_parser)

    def get_command(self, name: str) -> Optional[BaseCommand]:
        """Get a command by name or alias."""
        return self.commands.get(name)

    def get_all_commands(self) -> List[BaseCommand]:
        """Get all unique commands (excluding aliases)."""
        seen = set()
        unique_commands = []
        for command in self.commands.values():
            if command not in seen:
                seen.add(command)
                unique_commands.append(command)
        return unique_commands

    def setup_parser(self, parser: PiecesArgparser, version: str):
        """Set up the argument parser with all registered commands."""
        self.parser = parser

        # Add global arguments
        parser.add_argument(
            "--version",
            "-v",
            action="store_true",
            help="Displays the Pieces CLI version",
        )
        parser.add_argument(
            "--ignore-onboarding",
            action="store_true",
            help="Ignores the onboarding for the running command",
        )

        # Create subparsers for commands
        self.command_subparser = parser.add_subparsers(dest="command")
        for command in BaseCommand.commands:
            self.register(command)

        # Add the groups manually for now
        # self.register(MCPCommandGroup())

        parser.set_defaults(
            func=lambda **kwargs: print(version)
            if kwargs.get("version")
            else parser.print_help()
        )
        help_subparser = self.command_subparser.add_parser(
            "help", help="Show this message"
        )
        help_subparser.set_defaults(func=lambda **kwargs: parser.print_help())

        return parser
