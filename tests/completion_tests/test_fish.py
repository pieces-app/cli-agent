#!/usr/bin/env python3
"""Test Fish shell completions using pytest."""

import pytest
import shutil
from .fish_tester import FishCompletionTester
import platform


@pytest.fixture(scope="module")
def fish_tester():
    """Create a Fish completion tester instance."""
    return FishCompletionTester()


@pytest.mark.skipif(
    platform.system() == "Windows",
    reason="Fish completion tests are for Linux and macOS only",
)
@pytest.mark.skipif(not shutil.which("fish"), reason="Fish not available")
class TestFishCompletions:
    """Test suite for Fish shell completions."""

    def test_basic_command_completion(self, fish_tester):
        """Test basic command completion."""
        success, completions, error = fish_tester.run_completion_test("pieces ")
        assert success, f"Completion failed: {error}"

        expected = fish_tester.get_expected_commands()
        completion_set = set(completions)

        assert completion_set == expected, f"Expected {expected}, got {completion_set}"

    def test_mcp_subcommand_completion(self, fish_tester):
        """Test MCP subcommand completion."""
        success, completions, error = fish_tester.run_completion_test("pieces mcp ")
        assert success, f"Completion failed: {error}"

        expected = fish_tester.get_expected_subcommands("mcp")
        completion_set = set(completions)

        assert completion_set == expected, f"Expected {expected}, got {completion_set}"

    def test_mcp_docs_options(self, fish_tester):
        """Test MCP docs options."""
        success, completions, error = fish_tester.run_completion_test(
            "pieces mcp docs -"
        )
        assert success, f"Completion failed: {error}"

        expected = fish_tester.get_command_options("mcp", "docs")
        completion_set = set(completions)

        # Fish typically includes help options
        assert expected.issubset(completion_set), (
            f"Missing options: {expected - completion_set}"
        )

    def test_no_iwrap_completion(self, fish_tester):
        """Test that -iwrap is not suggested for 'pieces mcp -i' (the reported bug)."""
        success, completions, error = fish_tester.run_completion_test("pieces mcp -i")
        assert success, f"Completion failed: {error}"

        completion_set = set(completions)

        # Check for the specific bug - -iwrap should not appear
        assert "-iwrap" not in completion_set, "Found unwanted -iwrap completion"

        # In Fish, -i<value> completions are expected
        # But -iwrap specifically should not be there if 'wrap' is not a valid MCP subcommand
        mcp_subcommands = fish_tester.get_expected_subcommands("mcp")
        if "wrap" not in mcp_subcommands:
            assert "-iwrap" not in completion_set

    def test_integration_choices_with_space(
        self, fish_tester, expected_integrations_with_meta
    ):
        """Test integration choices after -i with space."""
        success, completions, error = fish_tester.run_completion_test(
            "pieces mcp docs -i "
        )
        assert success, f"Completion failed: {error}"

        completion_set = set(completions)
        assert completion_set == expected_integrations_with_meta, (
            f"Expected {expected_integrations_with_meta}, got {completion_set}"
        )

    def test_no_integration_values_for_docs_tab(
        self, fish_tester, expected_integrations_with_meta
    ):
        """Test that integration values are not shown for 'mcp docs<TAB>'."""
        success, completions, error = fish_tester.run_completion_test(
            "pieces mcp docs "
        )
        assert success, f"Completion failed: {error}"

        completion_set = set(completions)
        found_integrations = completion_set.intersection(
            expected_integrations_with_meta
        )
        assert not found_integrations, (
            f"Found unexpected integration values: {found_integrations}"
        )

    def test_integration_choices_without_space(
        self, fish_tester, expected_integrations_with_meta
    ):
        """Test integration choices without space show with -i prefix (standard Fish behavior)."""
        success, completions, error = fish_tester.run_completion_test(
            "pieces mcp docs -i"
        )
        assert success, f"Completion failed: {error}"

        expected_with_prefix = {f"-i{val}" for val in expected_integrations_with_meta}
        completion_set = set(completions)

        assert completion_set == expected_with_prefix, (
            f"Expected {expected_with_prefix}, got {completion_set}"
        )

    def test_no_grouped_options(self, fish_tester):
        """Test that options are not grouped as a single 'Available options' item."""
        success, completions, error = fish_tester.run_completion_test(
            "pieces mcp docs -"
        )
        assert success, f"Completion failed: {error}"

        completion_set = set(completions)
        grouped_items = {"(Available options)", "Available options"}
        found_grouped = completion_set.intersection(grouped_items)
        assert not found_grouped, f"Found grouped option items: {found_grouped}"

    def test_dynamic_partial_completions(self, fish_tester):
        """Test completions for partial commands dynamically."""
        # Test some common prefixes
        test_prefixes = [
            ("a", 1),  # At least 'ask' should be there
            ("c", 3),  # Multiple commands start with 'c'
            ("l", 2),  # 'list', 'login', 'logout'
        ]

        for prefix, min_expected in test_prefixes:
            command_line = f"pieces {prefix}"
            expected = fish_tester.get_commands_starting_with(prefix)

            if not expected:
                continue

            success, completions, error = fish_tester.run_completion_test(command_line)
            assert success, f"Completion failed for prefix '{prefix}': {error}"

            completion_set = set(completions)
            matching = expected & completion_set

            assert len(matching) >= min_expected, (
                f"Expected at least {min_expected} completions for '{prefix}', got {matching}"
            )

    def test_mcp_subcommand_partial(self, fish_tester):
        """Test partial MCP subcommand completion."""
        # Test common MCP subcommand prefixes
        prefixes = ["s", "d", "l", "r"]

        for prefix in prefixes:
            expected = fish_tester.get_subcommands_starting_with("mcp", prefix)
            if not expected:
                continue

            success, completions, error = fish_tester.run_completion_test(
                f"pieces mcp {prefix}"
            )
            assert success, f"Completion failed: {error}"

            completion_set = set(completions)
            found = expected & completion_set
            assert len(found) > 0, f"No MCP subcommands found for prefix '{prefix}'"

    def test_command_descriptions(self, fish_tester):
        """Test that commands have descriptions in Fish (part of Fish's rich completion)."""
        # Fish shows descriptions alongside completions
        # This test would check if the format includes descriptions
        # For now, we just verify completions work
        success, completions, error = fish_tester.run_completion_test("pieces ")
        assert success, f"Completion failed: {error}"
        assert len(completions) > 0, "No completions returned"

    @pytest.mark.skipif(not shutil.which("fish"), reason="Fish not available")
    def test_fish_availability(self):
        """Verify Fish is available for testing."""
        assert shutil.which("fish") is not None
