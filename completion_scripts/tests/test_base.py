#!/usr/bin/env python3
"""Base test utilities for shell completion testing."""

import subprocess
import sys
import os
from typing import List, Set, Tuple, Optional
from pathlib import Path

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
        # Get the path relative to the test file location
        test_dir = Path(__file__).parent
        generator_path = test_dir.parent / "autocomplete_generator.py"

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
        generated_dir = Path(__file__).parent / "generated"
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

        # Get all base commands
        for cmd in BaseCommand.commands:
            # cmd = cmd_class()  # Instantiate the command
            self.commands[cmd.name] = cmd

            # Handle command groups (like mcp)
            if isinstance(cmd, CommandGroup):
                self.subcommands[cmd.name] = {}
                for sub_name, sub_cmd in cmd.subcommands.items():
                    if sub_name == sub_cmd.name:  # Skip aliases
                        self.subcommands[cmd.name][sub_name] = sub_cmd

    def get_expected_commands(self) -> Set[str]:
        """Get all expected top-level commands."""
        commands = set()
        for cmd in BaseCommand.commands:
            # cmd = cmd_class()  # Instantiate the command
            commands.add(cmd.name)
            commands.update(cmd.aliases)
        return commands

    def get_expected_subcommands(self, command: str) -> Set[str]:
        """Get expected subcommands for a command group."""
        if command in self.subcommands:
            return set(self.subcommands[command].keys())
        return set()

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

    def validate_completions(
        self,
        command_line: str,
        completions: List[str],
        expected: Set[str],
        should_not_contain: Optional[Set[str]] = None,
    ) -> Tuple[bool, str]:
        """
        Validate that completions match expected values.
        Returns (success, error_message)
        """
        completion_set = set(completions)

        # Check for unwanted completions
        if should_not_contain:
            unwanted = completion_set.intersection(should_not_contain)
            if unwanted:
                return False, f"Found unwanted completions: {unwanted}"

        # Check if we have expected completions
        missing = expected - completion_set
        if missing and expected:  # Only fail if we explicitly expected something
            return False, f"Missing expected completions: {missing}"

        return True, ""


def run_test(
    test_name: str,
    tester: CompletionTester,
    command_line: str,
    expected: Optional[Set[str]] = None,
    should_not_contain: Optional[Set[str]] = None,
    should_contain: Optional[Set[str]] = None,
) -> bool:
    """Run a single test and print results."""
    print(f"\n🧪 {test_name}")
    print(f"   Command: {command_line}")

    success, completions, error = tester.run_completion_test(command_line)

    if not success:
        print(f"   ❌ FAIL: {error}")
        return False

    if (
        expected is not None
        or should_not_contain is not None
        or should_contain is not None
    ):
        completion_set = set(completions)

        # Check for unwanted completions
        if should_not_contain:
            unwanted = completion_set.intersection(should_not_contain)
            if unwanted:
                print(f"   ❌ FAIL: Found unwanted completions: {unwanted}")
                return False

        # Check if we have required completions
        if should_contain:
            missing = should_contain - completion_set
            if missing:
                print(f"   ❌ FAIL: Missing required completions: {missing}")
                print(
                    f"   Got: {completions[:10]}{'...' if len(completions) > 10 else ''}"
                )
                return False

        # Check exact match if expected is provided
        if expected is not None:
            missing = expected - completion_set
            extra = completion_set - expected
            if missing or extra:
                if missing:
                    print(f"   ❌ FAIL: Missing expected completions: {missing}")
                if extra:
                    print(f"   ❌ FAIL: Unexpected completions: {extra}")
                print(
                    f"   Got: {completions[:10]}{'...' if len(completions) > 10 else ''}"
                )
                return False

    print(f"   ✅ PASS")
    return True
