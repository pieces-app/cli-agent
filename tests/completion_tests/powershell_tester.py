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
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".ps1", delete=False, encoding="utf-8"
        ) as f:
            # PowerShell script that uses TabExpansion2
            f.write(f"""
# Source the completion file to register the completer
. '{self.completion_file}'

# Test completion using TabExpansion2
$commandLine = "{command_line}"
$cursorPosition = $commandLine.Length

try {{
    $result = TabExpansion2 -inputScript $commandLine -cursorColumn $cursorPosition
    
    $completions = @()
    if ($result -and $result.CompletionMatches) {{
        foreach ($match in $result.CompletionMatches) {{
            $completions += $match.CompletionText
        }}
    }}
    
    # Output as JSON
    ConvertTo-Json -InputObject $completions -Compress
}} catch {{
    # If TabExpansion2 fails, try to get completions directly
    Write-Error "TabExpansion2 failed: $_"
    ConvertTo-Json -InputObject @() -Compress
}}
""")
            script_path = f.name

        try:
            # Determine the PowerShell executable
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
                [
                    powershell_exe,
                    "-NoProfile",
                    "-NonInteractive",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    script_path,
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                return False, [], f"PowerShell error: {result.stderr}"

            # Parse JSON output
            try:
                output = result.stdout.strip()
                if output:
                    # Extract just the JSON part (ignore any other output)
                    lines = output.split("\n")
                    json_line = None
                    for line in lines:
                        line = line.strip()
                        if line.startswith("[") or line.startswith('"'):
                            json_line = line
                            break

                    if json_line:
                        completions = json.loads(json_line)
                        if not isinstance(completions, list):
                            completions = []
                    else:
                        completions = []
                else:
                    completions = []
            except json.JSONDecodeError as e:
                # If JSON parsing fails, check if we got file completions (which means our completer didn't work)
                if "file:" in result.stdout or "./" in result.stdout:
                    return (
                        False,
                        [],
                        "PowerShell defaulted to file completion - custom completer not working",
                    )
                return (
                    False,
                    [],
                    f"Failed to parse JSON output: {e}\nOutput: {result.stdout}",
                )

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
