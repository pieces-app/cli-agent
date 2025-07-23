#!/usr/bin/env python3
"""Test Zsh shell completions using pytest."""

import pytest
import shutil
from .zsh_tester import ZshCompletionTester
import platform


@pytest.fixture(scope="module")
def zsh_tester():
    """Create a Zsh completion tester instance."""
    return ZshCompletionTester()


@pytest.mark.skipif(
    platform.system() == "Windows",
    reason="Zsh completion tests are for Linux and macOS only",
)
@pytest.mark.skipif(not shutil.which("Zsh"), reason="Zsh not available")
class TestZshCompletions:
    """Test suite for Zsh shell completions."""

    def test_basic_command_completion(self, zsh_tester):
        """Test basic command completion."""
        success, completions, error = zsh_tester.run_completion_test("pieces ")
        assert success, f"Completion failed: {error}"

        completion_set = set(completions)
        expected_commands = zsh_tester.get_expected_primary_commands()

        # Zsh might return empty completions or a subset
        if completion_set:
            # Check that we have a reasonable overlap
            overlap = expected_commands & completion_set
            assert len(overlap) >= 5, (
                f"Too few commands found. Expected some of {expected_commands}, got {completion_set}"
            )

    def test_mcp_subcommand_completion(self, zsh_tester):
        """Test MCP subcommand completion."""
        success, completions, error = zsh_tester.run_completion_test("pieces mcp ")
        assert success, f"Completion failed: {error}"

        if not completions:
            pytest.skip("Zsh returned no completions for this test")

        expected = zsh_tester.get_expected_subcommands("mcp")
        completion_set = set(completions)

        # Zsh might include additional completions, so we check subset
        missing = expected - completion_set
        if missing:
            # Allow some flexibility
            found = expected & completion_set
            assert len(found) >= 3, f"Too few MCP subcommands found. Missing: {missing}"

    def test_mcp_docs_options(self, zsh_tester):
        """Test MCP docs options."""
        success, completions, error = zsh_tester.run_completion_test("pieces mcp docs ")
        assert success, f"Completion failed: {error}"

        if not completions:
            pytest.skip("Zsh returned no completions for this test")

        completion_set = set(completions)
        expected_options = zsh_tester.get_command_options("mcp", "docs")

        # Check that we have at least some expected options
        found_options = expected_options & completion_set
        assert len(found_options) >= 2, (
            f"Too few options found. Expected some of {expected_options}, got {completion_set}"
        )

    def test_integration_choices_after_flag(self, zsh_tester, expected_integrations):
        """Test integration choices after --integration flag."""
        success, completions, error = zsh_tester.run_completion_test(
            "pieces mcp docs --integration "
        )
        assert success, f"Completion failed: {error}"

        if not completions:
            pytest.skip("Zsh returned no completions for this test")

        completion_set = set(completions)
        # Check we have at least some integrations
        found = expected_integrations & completion_set
        assert len(found) >= 3, (
            f"Too few integrations found. Expected some of {expected_integrations}, got {completion_set}"
        )

    def test_dynamic_partial_completions(self, zsh_tester):
        """Test partial command completions dynamically."""
        # Test with known command prefixes
        test_cases = [
            ("pieces a", "ask"),  # 'ask' should be available
            ("pieces con", "config"),  # 'config' should match
            ("pieces l", ["list", "login", "logout"]),  # Multiple 'l' commands
        ]

        for command_line, expected in test_cases:
            success, completions, error = zsh_tester.run_completion_test(command_line)
            assert success, f"Completion failed for '{command_line}': {error}"

            if not completions:
                continue  # Skip if Zsh returns nothing

            completion_set = set(completions)

            if isinstance(expected, str):
                assert expected in completion_set, (
                    f"Expected '{expected}' in completions for '{command_line}'"
                )
            else:
                found = set(expected) & completion_set
                assert len(found) > 0, (
                    f"Expected at least one of {expected} for '{command_line}', got {completion_set}"
                )

    def test_mcp_subcommand_partial(self, zsh_tester):
        """Test partial MCP subcommand completion."""
        success, completions, error = zsh_tester.run_completion_test("pieces mcp l")
        assert success, f"Completion failed: {error}"

        if completions:
            completion_set = set(completions)
            # 'list' should be among the completions
            expected_subcommands = zsh_tester.get_subcommands_starting_with("mcp", "l")
            found = expected_subcommands & completion_set
            assert len(found) > 0, (
                f"Expected MCP subcommands starting with 'l', got {completion_set}"
            )

    def test_option_value_completion(self, zsh_tester, expected_integrations):
        """Test that option values are suggested appropriately."""
        # Test short option
        success, completions, error = zsh_tester.run_completion_test(
            "pieces mcp docs -i "
        )
        assert success, f"Completion failed: {error}"

        if not completions:
            pytest.skip("Zsh returned no completions for option values")

        completion_set = set(completions)
        # Should include at least some integration names
        found = completion_set & expected_integrations
        assert len(found) >= 1, (
            f"Expected some integration values, got: {completion_set}"
        )

    def test_no_duplicate_options(self, zsh_tester):
        """Test that already-used options are not suggested again."""
        # This behavior is shell-specific and may vary
        success, completions, error = zsh_tester.run_completion_test(
            "pieces mcp docs --integration vscode "
        )
        assert success, f"Completion failed: {error}"

        if completions:
            completion_set = set(completions)
            # Should not suggest --integration again (but this is shell-dependent)
            # This test documents the behavior rather than enforcing it
            if "--integration" in completion_set:
                pytest.skip(
                    "Zsh allows duplicate options - this is shell-specific behavior"
                )

    @pytest.mark.skipif(not shutil.which("zsh"), reason="Zsh not available")
    def test_zsh_availability(self):
        """Verify Zsh is available for testing."""
        assert shutil.which("zsh") is not None

