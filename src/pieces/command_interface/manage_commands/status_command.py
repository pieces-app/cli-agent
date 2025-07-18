"""
Status command for showing Pieces CLI status and checking for updates.
"""

import argparse
import subprocess
from typing import Optional, cast

from pieces import __version__
from pieces.base_command import BaseCommand
from pieces.urls import URLs
from pieces.settings import Settings
from pieces.core.update_pieces_os import PiecesUpdater
from pieces._vendor.pieces_os_client.models.unchecked_os_server_update import (
    UncheckedOSServerUpdate,
)
from pieces._vendor.pieces_os_client.models.updating_status_enum import (
    UpdatingStatusEnum,
)

from .utils import (
    detect_installation_type,
    get_latest_pypi_version,
    get_latest_homebrew_version,
    check_updates_with_version_checker,
    print_installation_detection_help,
)


class ManageStatusCommand(BaseCommand):
    """Subcommand to show Pieces CLI status and check for updates."""

    _is_command_group = True

    def get_name(self) -> str:
        return "status"

    def get_help(self) -> str:
        return "Show Pieces CLI status"

    def get_description(self) -> str:
        return "Show the current version of Pieces CLI and check for available updates. Automatically detects installation method and queries the appropriate package repository."

    def get_examples(self) -> list[str]:
        return [
            "pieces manage status",
        ]

    def get_docs(self) -> str:
        return URLs.CLI_MANAGE_STATUS_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        pass

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
                # The output format varies, but we need to find the version
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

    def execute(self, **kwargs) -> int:
        """Execute the status command."""
        Settings.logger.print("[blue]Pieces CLI Status")
        Settings.logger.print("=" * 18)

        # Show current version
        Settings.logger.print(f"[cyan]Current Version: [white]{__version__}")
        installation_type = detect_installation_type()
        Settings.logger.print(
            f"[cyan]Installation Method: [white]{installation_type.title()}"
        )
        Settings.logger.print("[blue]Checking for updates...")

        # Determine update source based on installation type
        latest_version = None
        source = None
        should_show_help = False

        if installation_type == "homebrew":
            latest_version = get_latest_homebrew_version()
            source = "Homebrew"
        elif installation_type == "pip":
            latest_version = get_latest_pypi_version()
            source = "PyPI"
        elif installation_type == "installer":
            latest_version = get_latest_pypi_version()
            source = "Installer Script (PyPI)"
        elif installation_type == "chocolatey":
            latest_version = self._get_latest_chocolatey_version()
            source = "Chocolatey"
        elif installation_type == "winget":
            latest_version = self._get_latest_winget_version()
            source = "WinGet"
        elif installation_type == "unknown":
            Settings.logger.print("[yellow]Could not determine installation method.")
            latest_version = get_latest_pypi_version()
            source = "PyPI (fallback)"
            # Show help after status information
            should_show_help = True
        else:
            Settings.logger.print(
                f"[yellow]Unsupported installation method: {installation_type}\n"
                "[blue]Using PyPI for version checking"
            )
            latest_version = get_latest_pypi_version()
            source = "PyPI (fallback)"

        if not latest_version:
            Settings.logger.print(
                f"[yellow]Could not fetch latest version from {source}"
            )
            return 0

        Settings.logger.print(
            f"[cyan]Latest Version ({source}): [white]{latest_version}"
        )

        try:
            has_updates = check_updates_with_version_checker(
                __version__, latest_version
            )
        except Exception as e:
            Settings.logger.print(f"[yellow]Warning: Could not check for updates: {e}")
            has_updates = False

        if has_updates:
            Settings.logger.print(
                f"[yellow]✓ Update available: v{__version__} → v{latest_version}"
            )
            Settings.logger.print("[blue]Run 'pieces manage update' to update")
        else:
            Settings.logger.print("[green]✓ You are using the latest version!")

        Settings.logger.print("\n\n[blue]Pieces OS Status")
        Settings.logger.print("=" * 17)
        if Settings.pieces_client.is_pieces_running():
            Settings.startup()
            status = cast(
                UpdatingStatusEnum,
                Settings.pieces_client.os_api.os_update_check(
                    unchecked_os_server_update=UncheckedOSServerUpdate()
                ).status,
            )
        else:
            status = UpdatingStatusEnum.UNKNOWN
        pieces_os_version = getattr(Settings, "pieces_os_version", "Unknown")
        Settings.logger.print(f"[cyan]Pieces OS Version: [white]{pieces_os_version}")
        color = "white"
        if status == UpdatingStatusEnum.UP_TO_DATE:
            color = "green"
        elif status in [UpdatingStatusEnum.DOWNLOADING, UpdatingStatusEnum.AVAILABLE]:
            color = "yellow"
        elif status == UpdatingStatusEnum.READY_TO_RESTART:
            color = "blue"
        elif status in [
            UpdatingStatusEnum.CONTACT_SUPPORT,
            UpdatingStatusEnum.REINSTALL_REQUIRED,
        ]:
            color = "red"
        Settings.logger.print(
            f"[cyan]Pieces OS Update Status: [{color}]{PiecesUpdater.get_status_message(status)}"
        )

        # Show help if installation detection failed
        if should_show_help:
            print_installation_detection_help()

        return 0
