"""
Uninstall command for removing Pieces CLI from the system.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

from pieces.base_command import BaseCommand
from pieces.urls import URLs
from pieces.settings import Settings

from .utils import (
    _execute_operation_by_type,
    _handle_subprocess_error,
    remove_completion_scripts,
    remove_config_dir,
)


class ManageUninstallCommand(BaseCommand):
    """Subcommand to uninstall Pieces CLI."""

    _is_command_group = True

    def get_name(self) -> str:
        return "uninstall"

    def get_help(self) -> str:
        return "Uninstall Pieces CLI"

    def get_description(self) -> str:
        return "Uninstall the Pieces CLI from your system. Automatically detects installation method and performs clean removal including configuration files."

    def get_examples(self) -> list[str]:
        return [
            "pieces manage uninstall",
            "pieces manage uninstall --remove-config",
        ]

    def get_docs(self) -> str:
        return URLs.CLI_MANAGE_UNINSTALL_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "--remove-config",
            action="store_true",
            help="Remove configuration files including shell completion scripts",
        )

    def _confirm_uninstall(self, installation_path: Optional[str] = None) -> bool:
        """Confirm uninstallation with user."""
        Settings.logger.print(
            "[yellow]This will completely remove Pieces CLI from your system."
        )
        if installation_path:
            Settings.logger.print(
                f"[yellow]Installation directory: {installation_path}"
            )

        response = input("Are you sure you want to proceed? [y/N]: ")
        return response.lower() in ["y", "yes"]

    def _post_uninstall_cleanup(self, remove_config: bool):
        """Perform common post-uninstall cleanup."""
        remove_completion_scripts()

        if remove_config:
            remove_config_dir()
        else:
            Settings.logger.print(
                "[yellow]Keeping other configuration files (preserving user settings)"
            )

    def _uninstall_installer_version(self, remove_config: bool = False) -> int:
        """Uninstall Pieces CLI installed via installer script."""
        pieces_cli_dir = Path.home() / ".pieces-cli"

        if not pieces_cli_dir.exists():
            Settings.logger.print("[yellow]Pieces CLI installation directory not found")
            return 0

        if not self._confirm_uninstall(str(pieces_cli_dir)):
            Settings.logger.print("[blue]Uninstallation cancelled.")
            return 0

        try:
            shutil.rmtree(pieces_cli_dir)
            Settings.logger.print(
                f"[green]✓ Removed installation directory: {pieces_cli_dir}"
            )

            Settings.logger.print(
                "[yellow]Please remove the following from your shell configuration:"
            )
            Settings.logger.print(f'  export PATH="{pieces_cli_dir}:$PATH"')
            Settings.logger.print("[yellow]Shell configuration files to check:")
            Settings.logger.print(
                "  - ~/.bashrc\n  - ~/.zshrc\n  - ~/.config/fish/config.fish"
            )

            self._post_uninstall_cleanup(remove_config)
            Settings.logger.print("[green]✓ Pieces CLI uninstalled successfully!")
            Settings.logger.print(
                "[yellow]Please restart your terminal to complete the removal."
            )
            return 0

        except Exception as e:
            Settings.logger.print(f"[red]Error during uninstallation: {e}")
            return 1

    def _uninstall_homebrew_version(self, remove_config: bool = False) -> int:
        """Uninstall Pieces CLI installed via homebrew."""
        try:
            Settings.logger.print("[blue]Uninstalling Pieces CLI via homebrew...")
            subprocess.run(["brew", "uninstall", "pieces-cli"], check=True)
            try:
                self._post_uninstall_cleanup(remove_config)
            except Exception as cleanup_error:
                Settings.logger.print(
                    f"[yellow]Warning: Cleanup failed: {cleanup_error}"
                )
            Settings.logger.print("[green]✓ Pieces CLI uninstalled successfully!")
            return 0

        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            return _handle_subprocess_error("uninstalling", "homebrew", e)

    def _uninstall_pip_version(self, remove_config: bool = False) -> int:
        """Uninstall Pieces CLI installed via pip."""
        try:
            Settings.logger.print("[blue]Uninstalling Pieces CLI via pip...")
            subprocess.run(
                [sys.executable, "-m", "pip", "uninstall", "pieces-cli", "-y"],
                check=True,
            )
            try:
                self._post_uninstall_cleanup(remove_config)
            except Exception as cleanup_error:
                Settings.logger.print(
                    f"[yellow]Warning: Cleanup failed: {cleanup_error}"
                )
            Settings.logger.print("[green]✓ Pieces CLI uninstalled successfully!")
            return 0

        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            return _handle_subprocess_error("uninstalling", "pip", e)

    def _uninstall_chocolatey_version(self, remove_config: bool = False) -> int:
        """Uninstall Pieces CLI installed via chocolatey."""
        try:
            Settings.logger.print("[blue]Uninstalling Pieces CLI via chocolatey...")
            subprocess.run(["choco", "uninstall", "pieces-cli", "-y"], check=True)
            try:
                self._post_uninstall_cleanup(remove_config)
            except Exception as cleanup_error:
                Settings.logger.print(
                    f"[yellow]Warning: Cleanup failed: {cleanup_error}"
                )
            Settings.logger.print("[green]✓ Pieces CLI uninstalled successfully!")
            return 0

        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            return _handle_subprocess_error("uninstalling", "chocolatey", e)

    def _uninstall_winget_version(self, remove_config: bool = False) -> int:
        """Uninstall Pieces CLI installed via winget."""
        try:
            Settings.logger.print("[blue]Uninstalling Pieces CLI via winget...")
            subprocess.run(
                [
                    "winget",
                    "uninstall",
                    "MeshIntelligentTechnologies.PiecesCLI",
                    "--silent",
                ],
                check=True,
            )
            try:
                self._post_uninstall_cleanup(remove_config)
            except Exception as cleanup_error:
                Settings.logger.print(
                    f"[yellow]Warning: Cleanup failed: {cleanup_error}"
                )
            Settings.logger.print("[green]✓ Pieces CLI uninstalled successfully!")
            return 0

        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            return _handle_subprocess_error("uninstalling", "winget", e)

    def execute(self, **kwargs) -> int:
        remove_config = kwargs.get("remove_config", False)

        operation_map = {
            "installer": lambda **kw: self._uninstall_installer_version(
                remove_config=kw.get("remove_config", False)
            ),
            "homebrew": lambda **kw: self._uninstall_homebrew_version(
                remove_config=kw.get("remove_config", False)
            ),
            "pip": lambda **kw: self._uninstall_pip_version(
                remove_config=kw.get("remove_config", False)
            ),
            "chocolatey": lambda **kw: self._uninstall_chocolatey_version(
                remove_config=kw.get("remove_config", False)
            ),
            "winget": lambda **kw: self._uninstall_winget_version(
                remove_config=kw.get("remove_config", False)
            ),
        }

        return _execute_operation_by_type(operation_map, remove_config=remove_config)
