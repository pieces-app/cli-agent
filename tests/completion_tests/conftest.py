"""Pytest configuration for completion tests."""

import pytest
import subprocess
import sys
import os
from pathlib import Path
from typing import List, Set, Tuple, Optional, Dict

# Add parent directories to path to import pieces modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pieces.app import PiecesCLI
from pieces.base_command import BaseCommand, CommandGroup


class CompletionTester:
    """Base class for testing shell completions."""

    def __init__(self, shell: str):
        self.shell = shell
        self.cli = PiecesCLI()
        self.parser = self.cli.parser
        self._parse_commands()

        # Generate completion script
        test_dir = Path(__file__).parent
        generator_path = (
            test_dir.parent.parent / "completion_scripts" / "autocomplete_generator.py"
        )

        std = subprocess.run(
            ["python", str(generator_path), f"--{shell}"],
            capture_output=True,
            text=True,
            cwd=str(test_dir.parent.parent),  # Run from project root
        )

        if std.returncode != 0:
            raise RuntimeError(f"Failed to generate {shell} completion: {std.stderr}")

        if not std.stdout:
            raise RuntimeError(f"No output from {shell} completion generator")

        # Create generated directory if it doesn't exist
        generated_dir = test_dir / "generated"
        generated_dir.mkdir(exist_ok=True)

        # Create a new file with the completions
        self.completion_file = generated_dir / f"{shell}_completions.{shell}"
        with open(self.completion_file, "w") as f:
            f.write(std.stdout)

    def _parse_commands(self):
        """Parse all available commands and their options from the parser."""
        self.commands = {}
        self.command_options = {}
        self.subcommands = {}
        self.command_aliases = {}

        # Get all base commands
        for cmd in BaseCommand.commands:
            self.commands[cmd.name] = cmd

            # Store aliases mapping
            for alias in cmd.aliases:
                self.command_aliases[alias] = cmd.name

            # Handle command groups (like mcp)
            if isinstance(cmd, CommandGroup):
                self.subcommands[cmd.name] = {}
                for sub_name, sub_cmd in cmd.subcommands.items():
                    if sub_name == sub_cmd.name:  # Skip aliases
                        self.subcommands[cmd.name][sub_name] = sub_cmd

    def get_expected_commands(self) -> Set[str]:
        """Get all expected top-level commands including aliases."""
        commands = set()
        for cmd in BaseCommand.commands:
            commands.add(cmd.name)
            commands.update(cmd.aliases)
        return commands

    def get_expected_primary_commands(self) -> Set[str]:
        """Get only primary command names (no aliases)."""
        return {cmd.name for cmd in BaseCommand.commands}

    def get_commands_starting_with(self, prefix: str) -> Set[str]:
        """Get all commands (including aliases) that start with a given prefix."""
        all_commands = self.get_expected_commands()
        return {cmd for cmd in all_commands if cmd.startswith(prefix)}

    def get_expected_subcommands(self, command: str) -> Set[str]:
        """Get expected subcommands for a command group."""
        # Handle aliases
        actual_command = self.command_aliases.get(command, command)

        if actual_command in self.subcommands:
            return set(self.subcommands[actual_command].keys())
        return set()

    def get_subcommands_starting_with(self, command: str, prefix: str) -> Set[str]:
        """Get subcommands that start with a given prefix."""
        subcommands = self.get_expected_subcommands(command)
        return {sub for sub in subcommands if sub.startswith(prefix)}

    def get_command_options(
        self, command: str, subcommand: Optional[str] = None
    ) -> Set[str]:
        """Get expected options for a command or subcommand."""
        options = set()

        # Find the parser for this command/subcommand
        subparsers_actions = [
            action
            for action in self.parser._actions
            if hasattr(action, "_subparsers") and action._subparsers
        ]

        for subparsers_action in subparsers_actions:
            choices = getattr(subparsers_action, "choices", None)
            if choices and command in choices:
                cmd_parser = choices[command]

                if subcommand:
                    # Look for subcommand parser
                    sub_subparsers = [
                        action
                        for action in cmd_parser._actions
                        if hasattr(action, "_subparsers") and action._subparsers
                    ]
                    for sub_action in sub_subparsers:
                        sub_choices = getattr(sub_action, "choices", None)
                        if sub_choices and subcommand in sub_choices:
                            cmd_parser = sub_choices[subcommand]
                            break

                # Extract options from the parser
                for action in cmd_parser._actions:
                    if action.option_strings:
                        options.update(action.option_strings)

        return options

    def get_option_choices(
        self, command: str, option: str, subcommand: Optional[str] = None
    ) -> Set[str]:
        """Get expected choices for a specific option."""
        choices = set()

        # Find the parser and option
        subparsers_actions = [
            action
            for action in self.parser._actions
            if hasattr(action, "_subparsers") and action._subparsers
        ]

        for subparsers_action in subparsers_actions:
            action_choices = getattr(subparsers_action, "choices", None)
            if action_choices and command in action_choices:
                cmd_parser = action_choices[command]

                if subcommand:
                    # Look for subcommand parser
                    sub_subparsers = [
                        action
                        for action in cmd_parser._actions
                        if hasattr(action, "_subparsers") and action._subparsers
                    ]
                    for sub_action in sub_subparsers:
                        sub_choices = getattr(sub_action, "choices", None)
                        if sub_choices and subcommand in sub_choices:
                            cmd_parser = sub_choices[subcommand]
                            break

                # Find the specific option
                for action in cmd_parser._actions:
                    if option in action.option_strings and action.choices:
                        choices.update(str(c) for c in action.choices)

        return choices

    def run_completion_test(self, command_line: str) -> Tuple[bool, List[str], str]:
        """
        Run a completion test for a given command line.
        Returns (success, completions, error_message)
        """
        raise NotImplementedError("Subclasses must implement run_completion_test")


@pytest.fixture
def completion_tester(request):
    """Fixture that provides the appropriate completion tester based on shell."""
    # This will be overridden in individual test files
    return None


@pytest.fixture
def expected_integrations():
    """Dynamically discover available MCP integrations."""
    # Import here to avoid circular imports
    from pieces.mcp.integration import mcp_integrations

    return set(mcp_integrations)


@pytest.fixture
def expected_integrations_with_meta(expected_integrations):
    """Expected integration names including 'all' and 'current'."""
    # These are meta-options available in the docs command
    return expected_integrations | {"all", "current", "raycast", "wrap"}

