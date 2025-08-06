"""Zsh-specific completion tester."""

import subprocess
import tempfile
import os
from typing import List, Tuple

from .conftest import CompletionTester


class ZshCompletionTester(CompletionTester):
    """Zsh-specific completion tester."""

    def __init__(self):
        super().__init__("zsh")

    def run_completion_test(self, command_line: str) -> Tuple[bool, List[str], str]:
        """Run Zsh completion test using subprocess."""
        # Create a test script that sources completions and captures results
        with tempfile.NamedTemporaryFile(mode="w", suffix=".zsh", delete=False) as f:
            f.write(f"""#!/usr/bin/env zsh
# Set up completion system
autoload -U compinit
compinit -u

# Source the completion file
source {self.completion_file}

# Clear any existing completions
compadd_args=()

# Override compadd to capture completions
compadd() {{
    # Store all arguments after options
    local skip_next=0
    for arg in "$@"; do
        if [[ $skip_next -eq 1 ]]; then
            skip_next=0
            continue
        fi
        case "$arg" in
            -d|-V|-J|-X|-r|-R|-q|-Q|-U)
                skip_next=1
                ;;
            -*)
                # Skip other single-letter options
                ;;
            *)
                compadd_args+=("$arg")
                ;;
        esac
    done
}}

# Parse the command line
words=({command_line})
CURRENT=$#words

# If command line ends with space, we're completing a new word
if [[ "{command_line}" == *" " ]]; then
    words+=("")
    ((CURRENT++))
fi

# Set BUFFER for some completion functions
BUFFER="{command_line}"

# Call the completion function
_pieces

# Output captured completions
for completion in "${{compadd_args[@]}}"; do
    echo "$completion"
done
""")
            script_path = f.name

        try:
            # Make script executable
            os.chmod(script_path, 0o755)

            # Run the Zsh script
            result = subprocess.run(
                ["zsh", "-f", script_path],  # -f for no startup files
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                return False, [], f"Zsh error: {result.stderr}"

            # Parse completions
            completions = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    completions.append(line)

            return True, completions, ""

        except subprocess.TimeoutExpired:
            return False, [], "Completion timed out"
        except Exception as e:
            return False, [], f"Error running completion: {e}"
        finally:
            os.unlink(script_path)

