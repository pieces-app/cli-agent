import argparse
from typing import Dict, List, Tuple, Optional, Any
from abc import ABC, abstractmethod
from pieces.base_command import BaseCommand


class CommandInfo:
    """Data class to hold command information."""

    def __init__(self, name: str, help: str, description: str, aliases: List[str]):
        self.name: str = name
        self.help: str = help
        self.description: str = description
        self.aliases: List[str] = aliases


class OptionInfo:
    """Data class to hold option information."""

    def __init__(
        self,
        flags: Tuple[str, ...],
        dest: str,
        help: str,
        type: Optional[type] = None,
        nargs: Optional[str] = None,
        choices: Optional[List[Any]] = None,
    ):
        self.flags = flags
        self.dest = dest
        self.help = help or ""
        self.type = type
        self.nargs = nargs
        self.choices = choices

    @property
    def short_flag(self) -> Optional[str]:
        """Get the short flag (e.g., '-f') if it exists."""
        for flag in self.flags:
            if flag.startswith("-") and not flag.startswith("--"):
                return flag[1:]  # Remove the dash
        return None

    @property
    def long_flag(self) -> Optional[str]:
        """Get the long flag (e.g., '--file') if it exists."""
        for flag in self.flags:
            if flag.startswith("--"):
                return flag[2:]  # Remove the dashes
        return None

    def is_file_type(self) -> bool:
        """Check if this option expects file/directory input."""
        return self.dest in ["file", "files", "path", "directory", "folder"]

    def is_integer_type(self) -> bool:
        """Check if this option expects integer input."""
        return self.type is int and self.nargs in ["*", "+", "?"]


class PositionalInfo:
    """Data class to hold positional argument information."""

    def __init__(
        self,
        dest: str,
        help: str,
        type: Optional[type] = None,
        nargs: Optional[str] = None,
        choices: Optional[List[Any]] = None,
    ):
        self.dest = dest
        self.help = help or dest
        self.type = type
        self.nargs = nargs
        self.choices = choices

    def is_file_type(self) -> bool:
        """Check if this positional expects file/directory input."""
        return self.dest in ["file", "files", "path"]


class CommandParser:
    """Parses argparse commands and extracts completion information."""

    def __init__(self, parser: argparse.ArgumentParser):
        self.parser = parser
        self.commands_info: Dict[str, CommandInfo] = {}
        self.aliases_map: Dict[str, str] = {}
        self.subcommand_details: Dict[str, Dict[str, Any]] = {}
        self._parse_commands()
        self._parse_subcommands()

    def _parse_commands(self):
        """Parse commands from BaseCommand registry."""
        for command in BaseCommand.commands:
            # command = command_class()  # Instantiate the command
            cmd_info = CommandInfo(
                name=command.name,
                help=command.help,
                description=command.description,
                aliases=command.aliases,
            )
            self.commands_info[command.name] = cmd_info

            # Map aliases to main command
            for alias in command.aliases:
                self.aliases_map[alias] = command.name

    def _parse_subcommands(self):
        """Parse subcommand details from argparse."""
        subparsers_actions = [
            action
            for action in self.parser._actions
            if isinstance(action, argparse._SubParsersAction)
        ]

        for subparsers_action in subparsers_actions:
            for choice, sub_parser in subparsers_action.choices.items():
                options = []
                positionals = []

                # Check if this subparser has its own subparsers (command group)
                sub_subparsers_actions = [
                    action
                    for action in sub_parser._actions
                    if isinstance(action, argparse._SubParsersAction)
                ]

                if sub_subparsers_actions:
                    # This is a command group, parse its subcommands
                    for sub_subparsers_action in sub_subparsers_actions:
                        for (
                            sub_choice,
                            sub_sub_parser,
                        ) in sub_subparsers_action.choices.items():
                            sub_options = []
                            sub_positionals = []

                            for action in sub_sub_parser._actions:
                                if action.option_strings:
                                    opt_info = OptionInfo(
                                        flags=tuple(action.option_strings),
                                        dest=action.dest,
                                        help=action.help,
                                        type=action.type,
                                        nargs=action.nargs,
                                        choices=action.choices,
                                    )
                                    sub_options.append(opt_info)
                                elif (
                                    action.dest != "help"
                                    and not action.dest.startswith("_")
                                ):
                                    pos_info = PositionalInfo(
                                        dest=action.dest,
                                        help=action.help,
                                        type=action.type,
                                        nargs=action.nargs,
                                        choices=action.choices,
                                    )
                                    sub_positionals.append(pos_info)

                            # Store with parent_subcommand format
                            key = f"{choice}_{sub_choice}"
                            self.subcommand_details[key] = {
                                "options": sub_options,
                                "positionals": sub_positionals,
                            }

                # Also parse the main command's options
                for action in sub_parser._actions:
                    if action.option_strings:
                        # It's an optional argument
                        opt_info = OptionInfo(
                            flags=tuple(action.option_strings),
                            dest=action.dest,
                            help=action.help,
                            type=action.type,
                            nargs=action.nargs,
                            choices=action.choices,
                        )
                        options.append(opt_info)
                    elif (
                        action.dest != "help"
                        and not action.dest.startswith("_")
                        and not isinstance(action, argparse._SubParsersAction)
                    ):
                        # It's a positional argument
                        pos_info = PositionalInfo(
                            dest=action.dest,
                            help=action.help,
                            type=action.type,
                            nargs=action.nargs,
                            choices=action.choices,
                        )
                        positionals.append(pos_info)

                self.subcommand_details[choice] = {
                    "options": options,
                    "positionals": positionals,
                }


class CompletionGenerator(ABC):
    """Abstract base class for shell completion generators."""

    def __init__(self, parser: CommandParser, tool_name: str):
        self.parser = parser
        self.tool_name = tool_name

    @abstractmethod
    def generate(self) -> str:
        """Generate the completion script."""
        pass

    def escape_string(self, text: str) -> str:
        """Escape special characters for the shell."""
        return text.replace('"', '\\"').replace("\n", " ")
