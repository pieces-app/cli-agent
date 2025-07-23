"""PowerShell-specific completion tester."""

import subprocess
import tempfile
import os
import json
from typing import List, Tuple

from .conftest import CompletionTester


class PowerShellCompletionTester(CompletionTester):
    """PowerShell-specific completion tester."""

    def __init__(self):
        super().__init__("powershell")

    def run_completion_test(self, command_line: str) -> Tuple[bool, List[str], str]:
        """Run PowerShell completion test using subprocess."""
        # Create a test script that sources completions and captures results
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ps1", delete=False) as f:
            f.write(f"""
# Source the completion file
. {self.completion_file}

# Set up the command line
$commandLine = "{command_line}"
$cursorPosition = $commandLine.Length

# Call the completion function
$result = TabExpansion2 -inputScript $commandLine -cursorColumn $cursorPosition

# Output the completions as JSON for easy parsing
if ($result.CompletionMatches) {{
    $completions = @()
    foreach ($match in $result.CompletionMatches) {{
        $completions += $match.CompletionText
    }}
    ConvertTo-Json -InputObject $completions -Compress
}} else {{
    ConvertTo-Json -InputObject @() -Compress
}}
""")
            script_path = f.name

        try:
            # Determine the PowerShell executable
            # Try PowerShell Core first, then Windows PowerShell
            powershell_exe = None
            for exe in ["pwsh", "powershell"]:
                try:
                    subprocess.run([exe, "-Version"], capture_output=True, check=True)
                    powershell_exe = exe
                    break
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue

            if not powershell_exe:
                return False, [], "PowerShell not found"

            # Run the PowerShell script
            result = subprocess.run(
                [powershell_exe, "-NoProfile", "-NonInteractive", "-File", script_path],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                return False, [], f"PowerShell error: {result.stderr}"

            # Parse JSON output
            try:
                completions = json.loads(result.stdout.strip())
                if not isinstance(completions, list):
                    completions = []
            except json.JSONDecodeError:
                # Fallback to line-based parsing if JSON fails
                completions = []
                for line in result.stdout.strip().split("\n"):
                    if line and not line.startswith("#"):
                        completions.append(line)

            return True, completions, ""

        except subprocess.TimeoutExpired:
            return False, [], "Completion timed out"
        except Exception as e:
            return False, [], f"Error running completion: {e}"
        finally:
            try:
                os.unlink(script_path)
            except:
                pass

