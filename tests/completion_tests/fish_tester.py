"""Fish-specific completion tester."""

import subprocess
import tempfile
import os
import re
from typing import List, Tuple

from .conftest import CompletionTester


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

