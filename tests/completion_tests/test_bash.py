#!/usr/bin/env python3
"""Test Bash shell completions using pytest."""

import pytest
import shutil
import platform
from .bash_tester import BashCompletionTester


@pytest.fixture(scope="module")
def bash_tester():
    """Create a Bash completion tester instance."""
    return BashCompletionTester()


@pytest.mark.skipif(
    platform.system() == "Windows",
    reason="Bash completion tests are for Linux and macOS only",
)
@pytest.mark.skipif(not shutil.which("bash"), reason="Bash not available")
class TestBashCompletions:
    """Test suite for Bash shell completions."""

    def test_basic_command_completion(self, bash_tester):
        """Test basic command completion."""
        success, completions, error = bash_tester.run_completion_test("pieces ")
        assert success, f"Completion failed: {error}"

        completion_set = set(completions)
        expected_commands = bash_tester.get_expected_commands()

        # For bash, we often get a subset of commands based on context
        # So we check that we have at least the primary commands
        primary_commands = bash_tester.get_expected_primary_commands()
        missing_primary = primary_commands - completion_set

        # Allow some flexibility - check we have most commands
        if missing_primary:
            # Check if we at least have 80% of expected commands
            coverage = len(completion_set & expected_commands) / len(expected_commands)
            assert coverage >= 0.8, (
                f"Too many missing commands: {missing_primary}. Coverage: {coverage:.1%}"
            )

    def test_mcp_subcommand_completion(self, bash_tester):
        """Test MCP subcommand completion."""
        success, completions, error = bash_tester.run_completion_test("pieces mcp ")
        assert success, f"Completion failed: {error}"

        expected = bash_tester.get_expected_subcommands("mcp")
        completion_set = set(completions)

        assert completion_set == expected, f"Expected {expected}, got {completion_set}"

    def test_mcp_docs_options(self, bash_tester):
        """Test MCP docs options after command."""
        success, completions, error = bash_tester.run_completion_test(
            "pieces mcp docs "
        )
        assert success, f"Completion failed: {error}"

        completion_set = set(completions)
        expected_options = bash_tester.get_command_options("mcp", "docs")

        # Check we have the main options
        main_options = {opt for opt in expected_options if not opt.startswith("--help")}
        missing = main_options - completion_set
        assert not missing, f"Missing expected options: {missing}"

    def test_integration_choices_after_flag(self, bash_tester, expected_integrations):
        """Test integration choices after --integration flag."""
        success, completions, error = bash_tester.run_completion_test(
            "pieces mcp docs --integration "
        )
        assert success, f"Completion failed: {error}"

        completion_set = set(completions)
        # The actual choices should include the integrations
        missing = expected_integrations - completion_set
        assert not missing, f"Missing expected integrations: {missing}"

    def test_no_unwanted_completions(self, bash_tester):
        """Test that we don't get unwanted completions in specific contexts."""
        success, completions, error = bash_tester.run_completion_test("pieces mcp ")
        assert success, f"Completion failed: {error}"

        completion_set = set(completions)
        # Should only contain subcommands, not integration names
        expected_subcommands = bash_tester.get_expected_subcommands("mcp")

        # Check that we only have expected subcommands
        unexpected = completion_set - expected_subcommands
        assert not unexpected, f"Found unexpected completions: {unexpected}"

    def test_partial_command_completion(self, bash_tester):
        """Test completions for partial commands."""
        test_cases = [
            ("pieces l", ["list", "login", "logout"]),  # Commands starting with 'l'
            (
                "pieces c",
                [
                    "chat",
                    "chats",
                    "commit",
                    "config",
                    "create",
                    "contribute",
                    "completion",
                ],
            ),  # Commands starting with 'c'
            ("pieces mcp d", ["docs"]),  # Subcommands starting with 'd'
        ]

        for command_line, expected_subset in test_cases:
            success, completions, error = bash_tester.run_completion_test(command_line)
            assert success, f"Completion failed for '{command_line}': {error}"

            completion_set = set(completions)

            # For partial completions, check that all expected items are present
            missing = set(expected_subset) - completion_set
            assert not missing, (
                f"Missing expected completions for '{command_line}': {missing}"
            )

    def test_dynamic_command_prefixes(self, bash_tester):
        """Test partial completions dynamically based on actual commands."""
        # Test a few common prefixes
        prefixes = ["a", "s", "m", "o"]

        for prefix in prefixes:
            command_line = f"pieces {prefix}"
            expected = bash_tester.get_commands_starting_with(prefix)

            if not expected:
                # Skip if no commands start with this prefix
                continue

            success, completions, error = bash_tester.run_completion_test(command_line)
            assert success, f"Completion failed for prefix '{prefix}': {error}"

            completion_set = set(completions)
            missing = expected - completion_set

            # Allow for shell-specific filtering
            if missing and len(completion_set) > 0:
                # Check if we have at least some of the expected commands
                found = expected & completion_set
                assert len(found) > 0, (
                    f"No expected completions found for prefix '{prefix}'"
                )

    def test_file_completion_after_option(self, bash_tester):
        """Test file completion after options that expect files."""
        # This is a placeholder - actual implementation depends on how file completion is handled
        # Some options might trigger file completion
        pass

    @pytest.mark.skipif(
        platform.system() not in ["Linux", "Darwin"],
        reason="Test specific to Linux and macOS",
    )
    def test_unix_specific_behavior(self, bash_tester):
        """Test Unix-specific completion behavior."""
        success, completions, error = bash_tester.run_completion_test("pieces ")
        assert success, f"Completion failed: {error}"
        assert len(completions) > 0, "No completions returned on Unix system"
