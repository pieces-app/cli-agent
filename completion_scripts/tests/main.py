#!/usr/bin/env python3
"""Run all shell completion tests."""

import sys
import subprocess
import argparse
from pathlib import Path


def run_shell_test(shell: str) -> bool:
    """Run tests for a specific shell."""
    test_file = Path(__file__).parent / f"test_{shell}.py"

    if not test_file.exists():
        print(f"⚠️  Test file for {shell} not found: {test_file}")
        return True

    print(f"\n{'=' * 60}")
    print(f"Running {shell.upper()} completion tests...")
    print(f"{'=' * 60}\n")

    try:
        result = subprocess.run(
            [sys.executable, str(test_file)],
            capture_output=False,  # Let output go to console
            text=True,
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running {shell} tests: {e}")
        return False


def main():
    """Run all shell completion tests."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run shell completion tests")
    parser.add_argument(
        "shells",
        nargs="*",
        choices=["fish", "bash", "zsh"],
        help="Specific shell(s) to test. If not specified, all shells are tested.",
    )
    parser.add_argument(
        "--fish", action="store_true", help="Test Fish shell completions"
    )
    parser.add_argument(
        "--bash", action="store_true", help="Test Bash shell completions"
    )
    parser.add_argument("--zsh", action="store_true", help="Test Zsh shell completions")

    args = parser.parse_args()

    shells_to_test = []

    if args.shells:
        shells_to_test = args.shells
    elif args.fish or args.bash or args.zsh:
        if args.fish:
            shells_to_test.append("fish")
        if args.bash:
            shells_to_test.append("bash")
        if args.zsh:
            shells_to_test.append("zsh")
    else:
        shells_to_test = ["fish", "bash", "zsh"]

    print("╔" + "═" * 58 + "╗")
    print("║" + " Shell Completion Test Suite ".center(58) + "║")
    print("╚" + "═" * 58 + "╝")

    results = {}

    for shell in shells_to_test:
        results[shell] = run_shell_test(shell)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    all_passed = True
    for shell, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{shell.upper():10} {status}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
