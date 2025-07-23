#!/usr/bin/env python3
"""Run all completion tests with a summary."""

import sys
import subprocess
from pathlib import Path


def main():
    """Run all completion tests and provide a summary."""
    test_dir = Path(__file__).parent

    print("Running Shell Completion Tests")
    print("=" * 60)

    # Run pytest with coverage and verbose output
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(test_dir),
        "-v",
        "--tb=short",
    ]

    # Add markers to run tests even if shells are not available
    # (they'll be skipped with appropriate messages)
    result = subprocess.run(cmd)

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())

