"""
Shared utilities for manage commands.
"""

import json
import os
import shutil
import subprocess
import sys
import traceback
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable

from pieces.settings import Settings
from pieces._vendor.pieces_os_client.wrapper.version_compatibility import VersionChecker


def _safe_subprocess_run(
    cmd: List[str], **kwargs
) -> Optional[subprocess.CompletedProcess]:
    """Safely run subprocess with consistent error handling."""
    try:
        return subprocess.run(
            cmd, capture_output=True, text=True, check=False, **kwargs
        )
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return None


def _check_command_availability(command: str) -> bool:
    """Check if a command is available in PATH."""
    return shutil.which(command) is not None


def _get_executable_location() -> Optional[Path]:
    """Get the location of the current pieces executable."""
    try:
        # Method 1: Try sys.argv[0] if it looks like an executable path
        if sys.argv and sys.argv[0]:
            argv_path = Path(os.path.abspath(sys.argv[0]))
            # If it's a Python file, we're likely running via python -m pieces
            if argv_path.suffix in {".py", ".pyc"}:
                # Try to find 'pieces' in PATH instead
                pieces_exec = shutil.which("pieces")
                if pieces_exec:
                    return Path(pieces_exec)
            else:
                # Direct executable invocation
                return argv_path

        # Method 2: Try finding 'pieces' in PATH
        pieces_exec = shutil.which("pieces")
        if pieces_exec:
            return Path(pieces_exec)

        # Method 3: Check if we're in a known installation structure
        # This handles cases where we're running from a venv or specific install location
        current_file = Path(__file__).resolve()

        # Check for installer method structure: ~/.pieces-cli/venv/lib/python*/site-packages/pieces/...
        pieces_cli_dir = Path.home() / ".pieces-cli"
        if pieces_cli_dir in current_file.parents:
            wrapper_script = pieces_cli_dir / "pieces"
            if wrapper_script.exists():
                return wrapper_script

        # Method 4: Look for pieces executable relative to current Python
        python_dir = Path(sys.executable).parent
        for name in ["pieces", "pieces.exe", "pieces.cmd"]:
            candidate = python_dir / name
            if candidate.exists():
                return candidate

        return None
    except Exception:
        return None


def _detect_installer_method() -> bool:
    """Enhanced detection for installer script installation."""
    pieces_cli_dir = Path.home() / ".pieces-cli"

    # Primary indicator: our installer directory exists
    if pieces_cli_dir.exists() and (pieces_cli_dir / "venv").exists():
        return True

    # Secondary indicator: check if executable is in installer path
    exe_location = _get_executable_location()
    if exe_location and str(pieces_cli_dir) in str(exe_location):
        return True

    # Check environment variables that installer might set
    pieces_home = os.environ.get("PIECES_CLI_HOME")
    if pieces_home and Path(pieces_home) == pieces_cli_dir:
        return True

    return False


def _detect_homebrew_method() -> bool:
    """Enhanced detection for Homebrew installation."""
    if not _check_command_availability("brew"):
        return False

    # Check standard brew list command
    result = _safe_subprocess_run(["brew", "list", "pieces-cli"])
    if result and result.returncode == 0:
        return True

    # Check if executable is in homebrew paths
    exe_location = _get_executable_location()
    if exe_location:
        homebrew_paths = [
            "/opt/homebrew",  # Apple Silicon
            "/usr/local",  # Intel Macs
            "/home/linuxbrew/.linuxbrew",  # Linux
        ]

        # Add custom HOMEBREW_PREFIX if set
        if homebrew_prefix := os.environ.get("HOMEBREW_PREFIX"):
            homebrew_paths.append(homebrew_prefix)

        for path in homebrew_paths:
            if str(exe_location).startswith(path):
                return True

    # Check brew --prefix for custom installations
    result = _safe_subprocess_run(["brew", "--prefix", "pieces-cli"])
    if result and result.returncode == 0:
        return True

    return False


def _detect_pip_method() -> Dict[str, Any]:
    """Enhanced detection for pip installation with details."""
    pip_info = {
        "detected": False,
        "user_install": False,
        "venv": False,
        "editable": False,
    }

    # Try multiple pip commands
    pip_commands = [
        [sys.executable, "-m", "pip", "show", "pieces-cli"],
        ["pip", "show", "pieces-cli"],
        ["pip3", "show", "pieces-cli"],
    ]

    for cmd in pip_commands:
        if not _check_command_availability(cmd[0]):
            continue

        result = _safe_subprocess_run(cmd)
        if result and result.returncode == 0:
            pip_info["detected"] = True

            # Parse pip show output for additional details
            for line in result.stdout.split("\n"):
                if line.startswith("Location:"):
                    location = line.split(":", 1)[1].strip()

                    # Check if it's a user installation (in user's home directory)
                    if "site-packages" in location and (
                        "/.local/" in location or "\\.local\\" in location
                    ):
                        pip_info["user_install"] = True

                    # Check if it's in a virtual environment
                    if any(
                        venv_indicator in location
                        for venv_indicator in ["venv", "virtualenv", "conda", "pyenv"]
                    ):
                        pip_info["venv"] = True

                elif line.startswith("Editable project location:"):
                    pip_info["editable"] = True

            break

    return pip_info


def _detect_chocolatey_method() -> bool:
    """Enhanced detection for Chocolatey installation."""
    if not _check_command_availability("choco"):
        return False

    result = _safe_subprocess_run(["choco", "list", "--local-only", "pieces-cli"])
    if result and result.returncode == 0 and "pieces-cli" in result.stdout:
        return True

    # Check alternative chocolatey locations
    choco_paths = [
        Path("C:/ProgramData/chocolatey/lib/pieces-cli"),
        Path("C:/tools/chocolatey/lib/pieces-cli"),
    ]

    return any(path.exists() for path in choco_paths)


def _detect_winget_method() -> bool:
    """Enhanced detection for WinGet installation."""
    if not _check_command_availability("winget"):
        return False

    result = _safe_subprocess_run(
        ["winget", "list", "--id", "MeshIntelligentTechnologies.PiecesCLI"]
    )

    return bool(
        result
        and result.returncode == 0
        and "MeshIntelligentTechnologies.PiecesCLI" in result.stdout
    )


def detect_installation_type() -> str:
    """
    Robustly detect how Pieces CLI was installed.

    Returns:
        Installation type: installer, homebrew, pip, chocolatey, winget, or unknown
    """
    # Allow manual override via environment variable
    override = os.environ.get("PIECES_CLI_INSTALLATION_TYPE")
    if override:
        Settings.logger.debug(f"Using manual override: {override}")
        return override.lower()

    Settings.logger.debug("Starting installation type detection...")

    # Check installer method first (most specific)
    if _detect_installer_method():
        Settings.logger.debug("Detected: installer script")
        return "installer"

    # Check Homebrew (with enhanced detection)
    if _detect_homebrew_method():
        Settings.logger.debug("Detected: homebrew")
        return "homebrew"

    # Check Windows package managers
    if _detect_chocolatey_method():
        Settings.logger.debug("Detected: chocolatey")
        return "chocolatey"

    if _detect_winget_method():
        Settings.logger.debug("Detected: winget")
        return "winget"

    # Check pip installation (with detailed analysis)
    pip_info = _detect_pip_method()
    if pip_info["detected"]:
        Settings.logger.debug(f"Detected: pip (details: {pip_info})")
        return "pip"

    Settings.logger.debug("Could not detect installation method")
    return "unknown"


def _get_fallback_method(
    installation_type: str, operation_map: dict[str, Callable]
) -> Optional[str]:
    """Get a fallback method for unsupported installation types."""
    fallback_map = {
        "unknown": "pip",  # Default fallback to pip
    }

    fallback = fallback_map.get(installation_type)
    if fallback and fallback in operation_map:
        return fallback
    return None


def _execute_operation_by_type(operation_map: dict[str, Callable], **kwargs) -> int:
    """Execute operation based on detected installation type with fallback support."""
    try:
        Settings.logger.print("[blue]Detecting installation method...")
        installation_type = detect_installation_type()

        # Try primary installation method
        if installation_type in operation_map:
            Settings.logger.print(
                f"[cyan]Detected: {installation_type.title()} installation"
            )
            return operation_map[installation_type](**kwargs)

        # Try fallback method
        fallback_method = _get_fallback_method(installation_type, operation_map)
        if fallback_method:
            Settings.logger.print(
                f"[yellow]Detected: {installation_type.title()} installation\n"
                f"[blue]Using fallback method: {fallback_method}"
            )
            return operation_map[fallback_method](**kwargs)

        # No supported method found
        Settings.logger.print(
            f"[red]Error: Unsupported installation method '{installation_type}'\n"
            f"[yellow]Supported methods: {', '.join(operation_map.keys())}\n"
            f"[blue]Tip: Set PIECES_CLI_INSTALLATION_TYPE environment variable to override detection"
        )
        return 1

    except Exception as e:
        Settings.logger.print(f"[red]Error during operation: {type(e).__name__}: {e}")
        Settings.logger.debug(f"Full traceback: {traceback.format_exc()}")
        return 1


def _handle_subprocess_error(operation: str, method: str, error: Exception) -> int:
    """Handle subprocess errors with consistent messaging."""
    Settings.logger.print(f"[red]Error {operation} Pieces CLI via {method}: {error}")
    return 1


def get_latest_pypi_version() -> Optional[str]:
    """Get the latest version of pieces-cli from PyPI."""
    try:
        import urllib.request

        url = "https://pypi.org/pypi/pieces-cli/json"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read())
            return data["info"]["version"]
    except Exception as e:
        Settings.logger.error(e)
        return None


def get_latest_homebrew_version() -> Optional[str]:
    """Get the latest version of pieces-cli from Homebrew formula."""
    try:
        result = subprocess.run(
            ["brew", "info", "pieces-cli", "--json"],
            capture_output=True,
            text=True,
            check=True,
        )
        formula_data = json.loads(result.stdout)[0]
        return formula_data["versions"]["stable"]
    except Exception:
        return None


def check_updates_with_version_checker(
    current_version: str, latest_version: str
) -> bool:
    """Use VersionChecker to compare versions."""
    if current_version == "unknown" or latest_version == "unknown":
        return False
    try:
        comparison = VersionChecker.compare(current_version, latest_version)
        return comparison < 0
    except Exception:
        return False


def remove_completion_scripts():
    """Remove completion scripts from shell configuration files."""
    config_files = [
        Path.home() / ".bashrc",
        Path.home() / ".zshrc",
        Path.home() / ".config" / "fish" / "config.fish",
    ]

    Settings.logger.print(
        "[blue]Removing completion scripts from shell configuration..."
    )
    for config_file in config_files:
        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    lines = f.readlines()

                filtered_lines = [
                    line for line in lines if "pieces completion" not in line
                ]

                if len(filtered_lines) != len(lines):
                    with open(config_file, "w") as f:
                        f.writelines(filtered_lines)
                    Settings.logger.print(
                        f"[green]✓ Removed completion from {config_file}"
                    )

            except Exception as e:
                Settings.logger.print(
                    f"[yellow]Warning: Could not remove completion from {config_file}: {e}"
                )


def remove_config_dir():
    """Remove configuration directory."""
    Settings.logger.print(
        f"[blue]Also removing other configuration files {Settings.pieces_data_dir}..."
    )
    shutil.rmtree(Settings.pieces_data_dir, ignore_errors=True)


def print_installation_detection_help():
    """Print help information about installation detection and manual override."""
    Settings.logger.print("\n[blue]Installation Detection Help:")
    Settings.logger.print("=" * 30)
    Settings.logger.print(
        "[cyan]Supported Installation Methods:[/cyan]\n"
        "• installer    - Official installer script\n"
        "• homebrew     - macOS/Linux Homebrew\n"
        "• pip          - Python Package Index\n"
        "• chocolatey   - Windows Chocolatey\n"
        "• winget       - Windows Package Manager\n"
    )
    Settings.logger.print(
        "\n[cyan]Manual Override:[/cyan]\n"
        "Set environment variable to force specific method:\n"
        "[yellow]export PIECES_CLI_INSTALLATION_TYPE=pip[/yellow]\n"
        "[yellow]export PIECES_CLI_INSTALLATION_TYPE=homebrew[/yellow]\n"
    )
    Settings.logger.print(
        "\n[cyan]Troubleshooting:[/cyan]\n"
        "• Run with debug logging: [yellow]pieces manage status[/yellow]\n"
        "• Check detection details: [yellow]pieces manage status[/yellow]\n"
        "• Report issues with your installation details\n"
    )
