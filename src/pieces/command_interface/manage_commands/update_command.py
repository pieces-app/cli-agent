"""
Update command for managing Pieces CLI updates.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Optional

from pieces import __version__
from pieces.base_command import BaseCommand
from pieces.urls import URLs
from pieces.settings import Settings

from .utils import (
    _execute_operation_by_type,
    _handle_subprocess_error,
    get_latest_pypi_version,
    get_latest_homebrew_version,
    check_updates_with_version_checker,
)


class ManageUpdateCommand(BaseCommand):
    """Subcommand to update Pieces CLI."""

    _is_command_group = True

    def get_name(self) -> str:
        return "update"

    def get_help(self) -> str:
        return "Update Pieces CLI"

    def get_description(self) -> str:
        return "Update the Pieces CLI to the latest version. Automatically detects installation method (pip, homebrew, chocolatey, winget, or installer script) and uses the appropriate update method."

    def get_examples(self) -> list[str]:
        return [
            "pieces manage update",
            "pieces manage update --force",
        ]

    def get_docs(self) -> str:
        return URLs.CLI_MANAGE_UPDATE_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force update even if already up to date",
        )

    def _check_updates(self, source: str) -> bool:
        """Check if updates are available for any installation type."""
        Settings.logger.print("[blue]Checking for updates...")

        latest_version = None

        if source == "pip" or source == "installer":
            latest_version = get_latest_pypi_version()
        elif source == "homebrew":
            latest_version = get_latest_homebrew_version()
        elif source == "chocolatey":
            latest_version = self._get_latest_chocolatey_version()
        elif source == "winget":
            latest_version = self._get_latest_winget_version()
        else:
            Settings.logger.print(
                f"[yellow]Unknown source '{source}', using PyPI fallback"
            )
            latest_version = get_latest_pypi_version()

        if not latest_version:
            Settings.logger.print("[yellow]Could not determine update status")
            return False

        has_updates = check_updates_with_version_checker(__version__, latest_version)

        if not has_updates:
            Settings.logger.print(
                f"[green]✓ Pieces CLI is already up to date (v{__version__})"
            )
            return False
        else:
            Settings.logger.print(
                f"[yellow]Update available: v{__version__} → v{latest_version}"
            )
            return True

    def _get_latest_chocolatey_version(self) -> Optional[str]:
        """Get the latest version of pieces-cli from Chocolatey."""
        try:
            result = subprocess.run(
                ["choco", "search", "pieces-cli", "--exact", "--limit-output"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0 and "pieces-cli" in result.stdout:
                # Extract version from the search output
                # The output format is like: pieces-cli|1.2.3
                for line in result.stdout.splitlines():
                    if line.startswith("pieces-cli|"):
                        return line.split("|")[1]
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        return None

    def _get_latest_winget_version(self) -> Optional[str]:
        """Get the latest version of pieces-cli from WinGet."""
        try:
            result = subprocess.run(
                [
                    "winget",
                    "search",
                    "MeshIntelligentTechnologies.PiecesCLI",
                    "--exact",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            if (
                result.returncode == 0
                and "MeshIntelligentTechnologies.PiecesCLI" in result.stdout
            ):
                # Extract version from the search output
                lines = result.stdout.splitlines()
                for line in lines:
                    if "MeshIntelligentTechnologies.PiecesCLI" in line:
                        # Try to extract version from the line
                        parts = line.split()
                        if len(parts) >= 3:
                            # Version is typically the last column
                            version = parts[-1]
                            # Basic version validation
                            if (
                                version
                                and "." in version
                                and not "MeshIntelligentTechnologies" in version
                            ):
                                return version
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        return None

    def _should_update(self, source: str, force: bool) -> bool:
        """Determine if update should proceed based on force flag and availability."""
        if force:
            return True
        return self._check_updates(source)

    def _validate_installer_environment(self) -> tuple[int, Optional[Path]]:
        """Validate installer environment and return pip executable path."""
        pieces_cli_dir = Path.home() / ".pieces-cli"
        venv_dir = pieces_cli_dir / "venv"

        if not venv_dir.exists():
            Settings.logger.print(
                "[red]Error: Virtual environment not found at ~/.pieces-cli/venv"
            )
            Settings.logger.print(
                "[yellow]Please reinstall Pieces CLI using the installer script"
            )
            return 1, None

        pip_executable = venv_dir / (
            "Scripts/pip.exe" if sys.platform == "win32" else "bin/pip"
        )
        if not pip_executable.exists():
            Settings.logger.print("[red]Error: pip not found in virtual environment")
            return 1, None

        return 0, pip_executable

    def _perform_update(self, pip_executable: Path, force: bool) -> int:
        """Perform the actual update operation."""
        try:
            Settings.logger.print(
                "[blue]Updating Pieces CLI via pip in virtual environment..."
            )

            # Upgrade pip first
            subprocess.run(
                [str(pip_executable), "install", "--upgrade", "pip"], check=True
            )

            # Upgrade pieces-cli
            cmd = [str(pip_executable), "install", "--upgrade", "pieces-cli"]
            if force:
                cmd.append("--force-reinstall")
            subprocess.run(cmd, check=True)

            return 0

        except subprocess.CalledProcessError as e:
            return _handle_subprocess_error("updating", "pip", e)

    def _verify_update_success(self, result: int) -> int:
        """Verify update success and display appropriate message."""
        if result == 0:
            Settings.logger.print("[green]✓ Pieces CLI updated successfully!")
        return result

    def _update_installer_version(self, force: bool = False) -> int:
        """Update Pieces CLI installed via installer script."""
        # Validate environment
        validation_result, pip_executable = self._validate_installer_environment()
        if validation_result != 0 or pip_executable is None:
            return validation_result

        # Check if updates are needed
        if not self._should_update("pip", force):
            return 1

        # Perform update
        update_result = self._perform_update(pip_executable, force)

        # Verify and report success
        return self._verify_update_success(update_result)

    def _perform_homebrew_update(self, force: bool) -> int:
        """Perform homebrew update operation."""
        try:
            Settings.logger.print("[blue]Updating Pieces CLI via homebrew...")
            cmd = ["brew", "reinstall" if force else "upgrade", "pieces-cli"]
            subprocess.run(cmd, check=True)
            return 0

        except subprocess.CalledProcessError as e:
            return _handle_subprocess_error("updating", "homebrew", e)

    def _update_homebrew_version(self, force: bool = False) -> int:
        """Update Pieces CLI installed via homebrew."""
        # Check if updates are needed
        if not self._should_update("homebrew", force):
            return 1

        # Perform update
        update_result = self._perform_homebrew_update(force)

        # Verify and report success
        return self._verify_update_success(update_result)

    def _perform_pip_update(self, force: bool) -> int:
        """Perform pip update operation."""
        try:
            Settings.logger.print("[blue]Updating Pieces CLI via pip...")
            cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "pieces-cli"]
            if force:
                cmd.append("--force-reinstall")
            subprocess.run(cmd, check=True)
            return 0

        except subprocess.CalledProcessError as e:
            return _handle_subprocess_error("updating", "pip", e)

    def _update_pip_version(self, force: bool = False) -> int:
        """Update Pieces CLI installed via pip."""
        # Check if updates are needed
        if not self._should_update("pip", force):
            return 1

        # Perform update
        update_result = self._perform_pip_update(force)

        # Verify and report success
        return self._verify_update_success(update_result)

    def _perform_chocolatey_update(self, force: bool) -> int:
        """Perform chocolatey update operation."""
        try:
            Settings.logger.print("[blue]Updating Pieces CLI via chocolatey...")
            if force:
                # For chocolatey, we can use reinstall to force update
                cmd = ["choco", "upgrade", "pieces-cli", "--force", "-y"]
            else:
                cmd = ["choco", "upgrade", "pieces-cli", "-y"]
            subprocess.run(cmd, check=True)
            return 0

        except subprocess.CalledProcessError as e:
            return _handle_subprocess_error("updating", "chocolatey", e)

    def _update_chocolatey_version(self, force: bool = False) -> int:
        """Update Pieces CLI installed via chocolatey."""
        # Check if updates are needed
        if not self._should_update("chocolatey", force):
            return 1

        # Perform update
        update_result = self._perform_chocolatey_update(force)

        # Verify and report success
        return self._verify_update_success(update_result)

    def _perform_winget_update(self, force: bool) -> int:
        """Perform winget update operation."""
        try:
            Settings.logger.print("[blue]Updating Pieces CLI via winget...")
            if force:
                # For winget, we can uninstall and then install to force update
                subprocess.run(
                    [
                        "winget",
                        "uninstall",
                        "MeshIntelligentTechnologies.PiecesCLI",
                        "--silent",
                    ],
                    check=True,
                )
                cmd = [
                    "winget",
                    "install",
                    "MeshIntelligentTechnologies.PiecesCLI",
                    "--silent",
                ]
            else:
                cmd = [
                    "winget",
                    "upgrade",
                    "MeshIntelligentTechnologies.PiecesCLI",
                    "--silent",
                ]
            subprocess.run(cmd, check=True)
            return 0

        except subprocess.CalledProcessError as e:
            return _handle_subprocess_error("updating", "winget", e)

    def _update_winget_version(self, force: bool = False) -> int:
        """Update Pieces CLI installed via winget."""
        # Check if updates are needed
        if not self._should_update("winget", force):
            return 1

        # Perform update
        update_result = self._perform_winget_update(force)

        # Verify and report success
        return self._verify_update_success(update_result)

    def execute(self, **kwargs) -> int:
        force = kwargs.get("force", False)

        operation_map = {
            "installer": lambda **kw: self._update_installer_version(
                kw.get("force", False)
            ),
            "homebrew": lambda **kw: self._update_homebrew_version(
                kw.get("force", False)
            ),
            "pip": lambda **kw: self._update_pip_version(kw.get("force", False)),
            "chocolatey": lambda **kw: self._update_chocolatey_version(
                kw.get("force", False)
            ),
            "winget": lambda **kw: self._update_winget_version(kw.get("force", False)),
        }

        return _execute_operation_by_type(operation_map, force=force)
