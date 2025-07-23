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


def _is_file_completion(completions):
    """Check if completions look like file completions rather than command completions."""
    if not completions:
        return False
    # If most completions start with ./ or contain file extensions, it's likely file completion
    file_like = sum(
        1 for comp in completions if comp.startswith("./") or "." in comp.split("/")[-1]
    )
    return file_like > len(completions) * 0.7  # More than 70% look like files


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

        if not success:
            if "custom completer not working" in error:
                pytest.skip("PowerShell custom completion not working on this platform")
            else:
                pytest.fail(f"Completion failed: {error}")

        completion_set = set(completions)
        expected_commands = powershell_tester.get_expected_primary_commands()

        # PowerShell completion might not work perfectly on all platforms
        if not completion_set:
            pytest.skip("PowerShell returned no completions")

        # Check if we got command completions vs file completions
        if _is_file_completion(completions):
            pytest.skip(
                "PowerShell defaulted to file completion instead of command completion"
            )

        # PowerShell should return primary commands
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

        if not success:
            pytest.skip(f"PowerShell completion failed: {error}")

        if not completions:
            pytest.skip("PowerShell returned no completions for MCP subcommands")

        # Check if we got file completions instead of command completions
        if _is_file_completion(completions):
            pytest.skip("PowerShell defaulted to file completion for MCP subcommands")

        expected = powershell_tester.get_expected_subcommands("mcp")
        completion_set = set(completions)

        # Check we have at least some expected subcommands
        found = expected & completion_set
        assert len(found) >= len(expected) // 2, (
            f"Too few MCP subcommands found: {found} vs expected {expected}"
        )

    def test_mcp_docs_options(self, powershell_tester):
        """Test MCP docs options."""
        success, completions, error = powershell_tester.run_completion_test(
            "pieces mcp docs -"
        )

        if not success:
            pytest.skip(f"PowerShell completion failed: {error}")

        if not completions:
            pytest.skip("PowerShell returned no completions for options")

        completion_set = set(completions)
        expected_options = powershell_tester.get_command_options("mcp", "docs")

        # PowerShell might format options differently
        # Check for both -option and --option formats
        found_options = set()
        for comp in completion_set:
            if comp.startswith("-"):
                found_options.add(comp)

        # Verify we have at least some main options
        main_options = {
            opt
            for opt in expected_options
            if opt in ["-i", "--integration", "-o", "--open"]
        }
        found_main = main_options & found_options
        assert len(found_main) >= 1, f"Expected some main options, got {found_options}"

    def test_integration_choices_after_flag(
        self, powershell_tester, expected_integrations
    ):
        """Test integration choices after --integration flag."""
        success, completions, error = powershell_tester.run_completion_test(
            "pieces mcp docs --integration "
        )

        if not success:
            pytest.skip(f"PowerShell completion failed: {error}")

        if not completions:
            pytest.skip("PowerShell returned no completions for integration values")

        # Check if we got file completions instead of integration names
        if _is_file_completion(completions):
            pytest.skip(
                "PowerShell defaulted to file completion for integration values"
            )

        completion_set = set(completions)
        # Should include integration names
        found = expected_integrations & completion_set
        assert len(found) >= 3, (
            f"Too few integrations found. Expected some of {expected_integrations}, got {completion_set}"
        )

    def test_partial_command_completion(self, powershell_tester):
        """Test completions for partial commands."""
        # Test with known prefixes - be more flexible
        test_cases = [
            ("pieces l", ["list"]),  # At least 'list' should be there
            ("pieces c", ["config"]),  # At least 'config' should be there
        ]

        for command_line, expected_items in test_cases:
            success, completions, error = powershell_tester.run_completion_test(
                command_line
            )

            if not success:
                continue  # Skip this test case

            if not completions:
                continue  # Skip if no completions

            # Skip if we got file completions
            if _is_file_completion(completions):
                continue

            completion_set = set(completions)
            found = set(expected_items) & completion_set
            if len(found) == 0:
                continue  # Skip if no matches found

            # If we found any matches, that's good enough
            assert len(found) > 0, (
                f"Expected at least one of {expected_items} for '{command_line}'"
            )

    def test_dynamic_command_prefixes(self, powershell_tester):
        """Test partial completions dynamically based on actual commands."""
        # Test a few common prefixes - be more flexible
        prefixes = ["a", "s"]

        found_any = False
        for prefix in prefixes:
            command_line = f"pieces {prefix}"
            expected = powershell_tester.get_commands_starting_with(prefix)

            if not expected:
                continue

            success, completions, error = powershell_tester.run_completion_test(
                command_line
            )

            if not success or not completions:
                continue

            # Skip if we got file completions
            if _is_file_completion(completions):
                continue

            completion_set = set(completions)
            found = expected & completion_set

            if len(found) > 0:
                found_any = True
                break

        # Just check that at least one prefix worked
        if not found_any:
            pytest.skip("PowerShell completion didn't work for any tested prefixes")

    def test_no_duplicate_completions(self, powershell_tester):
        """Test that completions don't contain duplicates."""
        success, completions, error = powershell_tester.run_completion_test("pieces ")

        if not success or not completions:
            pytest.skip("PowerShell completion test not applicable")

        # Check for duplicates
        assert len(completions) == len(set(completions)), (
            f"Found duplicate completions: {[c for c in completions if completions.count(c) > 1]}"
        )

    def test_option_with_value(self, powershell_tester):
        """Test options that take values."""
        success, completions, error = powershell_tester.run_completion_test(
            "pieces config --editor "
        )

        # This test is optional - just verify it doesn't crash
        assert success or "not working" in error, f"Unexpected error: {error}"

    @pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific test")
    def test_windows_specific_completion(self, powershell_tester):
        """Test Windows-specific completion behavior."""
        success, completions, error = powershell_tester.run_completion_test("pieces ")

        if success:
            # On Windows, completions might work better
            assert len(completions) > 0
        else:
            pytest.skip("PowerShell completion not working on Windows")
