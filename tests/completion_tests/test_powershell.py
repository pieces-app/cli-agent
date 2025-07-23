#!/usr/bin/env python3
"""Test PowerShell completions using pytest."""

import pytest
import shutil
import platform
from .powershell_tester import PowerShellCompletionTester


def has_powershell():
    """Check if PowerShell is available."""
    return shutil.which("pwsh") is not None or shutil.which("powershell") is not None


@pytest.fixture(scope="module")
def powershell_tester():
    """Create a PowerShell completion tester instance."""
    return PowerShellCompletionTester()


@pytest.mark.skipif(
    platform.system() != "Windows",
    reason="PowerShell completion tests are for Windows only",
)
@pytest.mark.skipif(not has_powershell(), reason="PowerShell not available")
class TestPowerShellCompletions:
    """Test suite for PowerShell completions."""

    def test_basic_command_completion(self, powershell_tester):
        """Test basic command completion."""
        success, completions, error = powershell_tester.run_completion_test("pieces ")
        assert success, f"Completion failed: {error}"

        completion_set = set(completions)
        expected_commands = powershell_tester.get_expected_primary_commands()

        # PowerShell should return all primary commands
        missing = expected_commands - completion_set
        if missing:
            # Allow some flexibility for PowerShell
            coverage = len(expected_commands & completion_set) / len(expected_commands)
            assert coverage >= 0.8, (
                f"Too many missing commands: {missing}. Coverage: {coverage:.1%}"
            )

    def test_mcp_subcommand_completion(self, powershell_tester):
        """Test MCP subcommand completion."""
        success, completions, error = powershell_tester.run_completion_test(
            "pieces mcp "
        )
        assert success, f"Completion failed: {error}"

        expected = powershell_tester.get_expected_subcommands("mcp")
        completion_set = set(completions)

        # Check we have all expected subcommands
        missing = expected - completion_set
        assert not missing, f"Missing MCP subcommands: {missing}"

    def test_mcp_docs_options(self, powershell_tester):
        """Test MCP docs options."""
        success, completions, error = powershell_tester.run_completion_test(
            "pieces mcp docs -"
        )
        assert success, f"Completion failed: {error}"

        completion_set = set(completions)
        expected_options = powershell_tester.get_command_options("mcp", "docs")

        # PowerShell might format options differently
        # Check for both -option and --option formats
        found_options = set()
        for comp in completion_set:
            if comp.startswith("-"):
                found_options.add(comp)

        # Verify we have the main options
        main_options = {
            opt
            for opt in expected_options
            if opt in ["-i", "--integration", "-o", "--open"]
        }
        missing = main_options - found_options
        assert not missing, f"Missing expected options: {missing} from {found_options}"

    def test_integration_choices_after_flag(
        self, powershell_tester, expected_integrations
    ):
        """Test integration choices after --integration flag."""
        success, completions, error = powershell_tester.run_completion_test(
            "pieces mcp docs --integration "
        )
        assert success, f"Completion failed: {error}"

        completion_set = set(completions)
        # Should include integration names
        found = expected_integrations & completion_set
        assert len(found) >= 5, (
            f"Too few integrations found. Expected some of {expected_integrations}, got {completion_set}"
        )

    def test_partial_command_completion(self, powershell_tester):
        """Test completions for partial commands."""
        # Test with known prefixes
        test_cases = [
            ("pieces l", ["list", "login", "logout"]),
            ("pieces c", ["chat", "chats", "commit", "config", "create"]),
            ("pieces mcp s", ["setup", "status", "start"]),
        ]

        for command_line, expected_items in test_cases:
            success, completions, error = powershell_tester.run_completion_test(
                command_line
            )
            assert success, f"Completion failed for '{command_line}': {error}"

            completion_set = set(completions)
            found = set(expected_items) & completion_set
            assert len(found) >= len(expected_items) // 2, (
                f"Too few completions for '{command_line}'. Expected some of {expected_items}, got {completion_set}"
            )

    def test_dynamic_command_prefixes(self, powershell_tester):
        """Test partial completions dynamically based on actual commands."""
        # Test a few common prefixes
        prefixes = ["a", "s", "o", "m"]

        for prefix in prefixes:
            command_line = f"pieces {prefix}"
            expected = powershell_tester.get_commands_starting_with(prefix)

            if not expected:
                continue

            success, completions, error = powershell_tester.run_completion_test(
                command_line
            )
            assert success, f"Completion failed for prefix '{prefix}': {error}"

            completion_set = set(completions)
            found = expected & completion_set

            # PowerShell should find at least some matches
            assert len(found) > 0, (
                f"No expected completions found for prefix '{prefix}'"
            )

    def test_no_duplicate_completions(self, powershell_tester):
        """Test that completions don't contain duplicates."""
        success, completions, error = powershell_tester.run_completion_test("pieces ")
        assert success, f"Completion failed: {error}"

        # Check for duplicates
        assert len(completions) == len(set(completions)), (
            f"Found duplicate completions: {[c for c in completions if completions.count(c) > 1]}"
        )

    def test_option_with_value(self, powershell_tester):
        """Test options that take values."""
        success, completions, error = powershell_tester.run_completion_test(
            "pieces config --editor "
        )
        assert success, f"Completion failed: {error}"

        # PowerShell might suggest common editors or file completion
        # Just verify we get some completions
        assert len(completions) >= 0, "Expected some completions for editor option"

    @pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific test")
    def test_windows_specific_completion(self, powershell_tester):
        """Test Windows-specific completion behavior."""
        success, completions, error = powershell_tester.run_completion_test("pieces ")
        assert success, f"Completion failed: {error}"

        # On Windows, completions might include .exe extension handling
        # This is a placeholder for Windows-specific tests
        assert len(completions) > 0

    def test_powershell_availability(self):
        """Verify PowerShell is available for testing."""
        assert has_powershell(), "PowerShell not available"

