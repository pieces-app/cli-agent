#!/usr/bin/env python3
"""Test Fish shell completions."""

import subprocess
import tempfile
import os
import re
from typing import List, Tuple
from pathlib import Path

from test_base import CompletionTester, run_test


class FishCompletionTester(CompletionTester):
    """Fish-specific completion tester."""

    def __init__(self):
        super().__init__("fish")

    def run_completion_test(self, command_line: str) -> Tuple[bool, List[str], str]:
        """Run Fish completion test using subprocess."""
        # Create a temporary script to run the completion
        with tempfile.NamedTemporaryFile(mode="w", suffix=".fish", delete=False) as f:
            f.write(f"""#!/usr/bin/env fish
source {self.completion_file}
set -l completions (complete -C "{command_line}" 2>&1)
for line in $completions
    echo $line
end
""")
            script_path = f.name

        try:
            # Run the Fish script
            result = subprocess.run(
                ["fish", script_path],
                capture_output=True,
                text=True,
                timeout=5,
                env={**os.environ, "TERM": "dumb"},  # Disable ANSI colors
            )

            if result.returncode != 0:
                return False, [], f"Fish error: {result.stderr}"

            # Parse completions (one per line)
            completions = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    # Remove ANSI escape sequences
                    clean_line = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", line)
                    clean_line = re.sub(r"\x1b\[[0-9]+ q", "", clean_line)

                    if clean_line.strip():
                        # Extract just the completion part (before any tab/description)
                        parts = clean_line.split("\t")
                        completions.append(parts[0].strip())

            return True, completions, ""

        except subprocess.TimeoutExpired:
            return False, [], "Completion timed out"
        except Exception as e:
            return False, [], f"Error running completion: {e}"
        finally:
            os.unlink(script_path)


def main():
    """Run Fish completion tests."""
    print("=" * 60)
    print("Testing Fish Shell Completions")
    print("=" * 60)

    tester = FishCompletionTester()
    passed = 0
    failed = 0

    # Test 1: Basic command completion
    expected_commands = tester.get_expected_commands()
    if run_test(
        "Basic command completion",
        tester,
        "pieces ",
        expected=expected_commands,
    ):
        passed += 1
    else:
        failed += 1

    # Test 2: MCP subcommand completion
    if run_test(
        "MCP subcommand completion",
        tester,
        "pieces mcp ",
        expected=tester.get_expected_subcommands("mcp"),
    ):
        passed += 1
    else:
        failed += 1

    # Test 3: MCP docs options
    if run_test(
        "MCP docs options",
        tester,
        "pieces mcp docs -",
        expected={"-i", "-o", "--integration", "--open", "-h", "--help"},
    ):
        passed += 1
    else:
        failed += 1

    # Test 4: No -iwrap completion (the reported bug)
    if run_test(
        "No -iwrap completion for 'pieces mcp -i'",
        tester,
        "pieces mcp -i",
        should_not_contain={"-iwrap"},
    ):
        passed += 1
    else:
        failed += 1

    # Test 5: Integration choices after -i with space
    expected_integrations = {
        "vscode",
        "goose",
        "cursor",
        "claude",
        "windsurf",
        "zed",
        "all",
        "current",
        "raycast",
        "wrap",
    }
    if run_test(
        "Integration choices after -i",
        tester,
        "pieces mcp docs -i ",
        expected=expected_integrations,
    ):
        passed += 1
    else:
        failed += 1

    # Test 6: No integration values for 'mcp docs<TAB>'
    if run_test(
        "No integration values shown for 'mcp docs'",
        tester,
        "pieces mcp docs ",
        should_not_contain=expected_integrations,
    ):
        passed += 1
    else:
        failed += 1

    # Test 7: Integration choices without space show with -i prefix (standard Fish behavior)
    expected_with_prefix = {f"-i{val}" for val in expected_integrations}
    if run_test(
        "Integration choices with -i prefix (standard Fish behavior)",
        tester,
        "pieces mcp docs -i",
        expected=expected_with_prefix,
    ):
        passed += 1
    else:
        failed += 1

    # Test 8: Options should not be grouped as a single "Available options" item
    if run_test(
        "No grouped 'Available options' item",
        tester,
        "pieces mcp docs -",
        should_not_contain={"(Available options)", "Available options"},
    ):
        passed += 1
    else:
        failed += 1

    # Summary
    print("\n" + "=" * 60)
    print(f"Fish Completion Tests: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    import sys

    sys.exit(0 if main() else 1)
