import argparse
from pieces.core.update_pieces_os import PiecesUpdater
import json
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Literal, Optional, Callable, cast
from pieces import __version__
from pieces.base_command import BaseCommand, CommandGroup
from pieces.urls import URLs
from pieces.settings import Settings
from pieces._vendor.pieces_os_client.wrapper.version_compatibility import VersionChecker
from pieces._vendor.pieces_os_client.models.unchecked_os_server_update import (
    UncheckedOSServerUpdate,
)
from pieces._vendor.pieces_os_client.models.updating_status_enum import (
    UpdatingStatusEnum,
)


def _execute_operation_by_type(operation_map: dict[str, Callable], **kwargs) -> int:
    """Execute operation based on detected installation type."""
    Settings.logger.print("[blue]Detecting installation method...")
    installation_type = detect_installation_type()

    if installation_type in operation_map:
        Settings.logger.print(
            f"[cyan]Detected: {installation_type.title()} installation"
        )
        return operation_map[installation_type](**kwargs)
    else:
        Settings.logger.print("[red]Error: Could not detect installation method")
        return 1


def _handle_subprocess_error(
    operation: str, method: str, error: subprocess.CalledProcessError
) -> int:
    """Handle subprocess errors with consistent messaging."""
    Settings.logger.print(f"[red]Error {operation} Pieces CLI via {method}: {error}")
    return 1


def detect_installation_type():
    """Detect how Pieces CLI was installed."""
    # Check if we're in a virtual environment created by our installer
    pieces_cli_dir = Path.home() / ".pieces-cli"
    if pieces_cli_dir.exists() and (pieces_cli_dir / "venv").exists():
        return "installer"

    # Check if installed via chocolatey
    try:
        result = subprocess.run(
            ["choco", "list", "--local-only", "pieces-cli"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0 and "pieces-cli" in result.stdout:
            return "chocolatey"
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Check if installed via winget
    try:
        result = subprocess.run(
            ["winget", "list", "--id", "MeshIntelligentTechnologies.PiecesCLI"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0 and "MeshIntelligentTechnologies.PiecesCLI" in result.stdout:
            return "winget"
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Check if installed via homebrew
    try:
        result = subprocess.run(
            ["brew", "list", "pieces-cli"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return "homebrew"
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Check if installed via pip globally
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", "pieces-cli"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return "pip"
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    return "unknown"


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

    def _check_updates(self, source: Literal["pip", "homebrew", "chocolatey", "winget"]) -> bool:
        """Check if updates are available."""
        Settings.logger.print("[blue]Checking for updates...")

        if source == "pip":
            latest_version = get_latest_pypi_version()
        elif source == "homebrew":
            latest_version = get_latest_homebrew_version()
        elif source == "chocolatey":
            latest_version = self._get_latest_chocolatey_version()
        elif source == "winget":
            latest_version = self._get_latest_winget_version()
        else:
            Settings.logger.print("[yellow]Could not determine update status")
            return False

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

    def _update_installer_version(self, force: bool = False) -> int:
        """Update Pieces CLI installed via installer script."""
        pieces_cli_dir = Path.home() / ".pieces-cli"
        venv_dir = pieces_cli_dir / "venv"

        if not venv_dir.exists():
            Settings.logger.print(
                "[red]Error: Virtual environment not found at ~/.pieces-cli/venv"
            )
            Settings.logger.print(
                "[yellow]Please reinstall Pieces CLI using the installer script"
            )
            return 1

        pip_executable = venv_dir / (
            "Scripts/pip.exe" if sys.platform == "win32" else "bin/pip"
        )
        if not pip_executable.exists():
            Settings.logger.print("[red]Error: pip not found in virtual environment")
            return 1

        if not force and not self._check_updates("pip"):
            return 1

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

            Settings.logger.print("[green]✓ Pieces CLI updated successfully!")
            return 0

        except subprocess.CalledProcessError as e:
            return _handle_subprocess_error("updating", "pip", e)

    def _update_homebrew_version(self, force: bool = False) -> int:
        """Update Pieces CLI installed via homebrew."""
        if not force and not self._check_updates("homebrew"):
            return 1

        try:
            Settings.logger.print("[blue]Updating Pieces CLI via homebrew...")
            cmd = ["brew", "reinstall" if force else "upgrade", "pieces-cli"]
            subprocess.run(cmd, check=True)
            Settings.logger.print("[green]✓ Pieces CLI updated successfully!")
            return 0

        except subprocess.CalledProcessError as e:
            return _handle_subprocess_error("updating", "homebrew", e)

    def _update_pip_version(self, force: bool = False) -> int:
        """Update Pieces CLI installed via pip."""
        if not force and not self._check_updates("pip"):
            return 1

        try:
            Settings.logger.print("[blue]Updating Pieces CLI via pip...")
            cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "pieces-cli"]
            if force:
                cmd.append("--force-reinstall")
            subprocess.run(cmd, check=True)
            Settings.logger.print("[green]✓ Pieces CLI updated successfully!")
            return 0

        except subprocess.CalledProcessError as e:
            return _handle_subprocess_error("updating", "pip", e)

    def _update_chocolatey_version(self, force: bool = False) -> int:
        """Update Pieces CLI installed via chocolatey."""
        if not force and not self._check_updates("chocolatey"):
            return 1

        try:
            Settings.logger.print("[blue]Updating Pieces CLI via chocolatey...")
            if force:
                # For chocolatey, we can use reinstall to force update
                cmd = ["choco", "upgrade", "pieces-cli", "--force", "-y"]
            else:
                cmd = ["choco", "upgrade", "pieces-cli", "-y"]
            subprocess.run(cmd, check=True)
            Settings.logger.print("[green]✓ Pieces CLI updated successfully!")
            return 0

        except subprocess.CalledProcessError as e:
            return _handle_subprocess_error("updating", "chocolatey", e)

    def _update_winget_version(self, force: bool = False) -> int:
        """Update Pieces CLI installed via winget."""
        if not force and not self._check_updates("winget"):
            return 1

        try:
            Settings.logger.print("[blue]Updating Pieces CLI via winget...")
            if force:
                # For winget, we can uninstall and then install to force update
                subprocess.run(["winget", "uninstall", "MeshIntelligentTechnologies.PiecesCLI", "--silent"], check=True)
                cmd = ["winget", "install", "MeshIntelligentTechnologies.PiecesCLI", "--silent"]
            else:
                cmd = ["winget", "upgrade", "MeshIntelligentTechnologies.PiecesCLI", "--silent"]
            subprocess.run(cmd, check=True)
            Settings.logger.print("[green]✓ Pieces CLI updated successfully!")
            return 0

        except subprocess.CalledProcessError as e:
            return _handle_subprocess_error("updating", "winget", e)

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
            "chocolatey": lambda **kw: self._update_chocolatey_version(kw.get("force", False)),
            "winget": lambda **kw: self._update_winget_version(kw.get("force", False)),
        }

        return _execute_operation_by_type(operation_map, force=force)


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
                ["winget", "search", "MeshIntelligentTechnologies.PiecesCLI", "--exact"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0 and "MeshIntelligentTechnologies.PiecesCLI" in result.stdout:
                # Extract version from the search output
                # The output format varies, but we need to find the version
                lines = result.stdout.splitlines()
                for line in lines:
                    if "MeshIntelligentTechnologies.PiecesCLI" in line:
                        # Try to extract version from the line
                        parts = line.split()
                        if len(parts) >= 3:
                            # Usually the version is in the 3rd column
                            version = parts[2]
                            # Basic version validation
                            if version and "." in version:
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

        if installation_type == "homebrew":
            latest_version = get_latest_homebrew_version()
            source = "Homebrew"
        elif installation_type == "pip":
            latest_version = get_latest_pypi_version()
            source = "PyPI"
        elif installation_type == "installer":
            latest_version = get_latest_pypi_version()
            source = "Installer Script"
        elif installation_type == "chocolatey":
            latest_version = self._get_latest_chocolatey_version()
            source = "Chocolatey"
        elif installation_type == "winget":
            latest_version = self._get_latest_winget_version()
            source = "WinGet"
        else:
            Settings.logger.print(
                "[yellow]Could not determine update source for unknown installation method"
            )
            return 0

        if not latest_version:
            Settings.logger.print(
                f"[yellow]Could not fetch latest version from {source}"
            )
            return 0

        Settings.logger.print(
            f"[cyan]Latest Version ({source}): [white]{latest_version}"
        )
        has_updates = check_updates_with_version_checker(__version__, latest_version)

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
        elif status == [UpdatingStatusEnum.DOWNLOADING, UpdatingStatusEnum.AVAILABLE]:
            color = "yellow"
        elif status in [
            UpdatingStatusEnum.READY_TO_RESTART,
        ]:
            color = "blue"
        elif status in [
            UpdatingStatusEnum.CONTACT_SUPPORT,
            UpdatingStatusEnum.REINSTALL_REQUIRED,
        ]:
            color = "red"
        Settings.logger.print(
            f"[cyan]Pieces OS Update Status: [{color}]{PiecesUpdater.get_status_message(status)}"
        )
        return 0


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
            self._post_uninstall_cleanup(remove_config)
            Settings.logger.print("[green]✓ Pieces CLI uninstalled successfully!")
            return 0

        except subprocess.CalledProcessError as e:
            return _handle_subprocess_error("uninstalling", "homebrew", e)

    def _uninstall_pip_version(self, remove_config: bool = False) -> int:
        """Uninstall Pieces CLI installed via pip."""
        try:
            Settings.logger.print("[blue]Uninstalling Pieces CLI via pip...")
            subprocess.run(
                [sys.executable, "-m", "pip", "uninstall", "pieces-cli", "-y"],
                check=True,
            )
            self._post_uninstall_cleanup(remove_config)
            Settings.logger.print("[green]✓ Pieces CLI uninstalled successfully!")
            return 0

        except subprocess.CalledProcessError as e:
            return _handle_subprocess_error("uninstalling", "pip", e)

    def _uninstall_chocolatey_version(self, remove_config: bool = False) -> int:
        """Uninstall Pieces CLI installed via chocolatey."""
        try:
            Settings.logger.print("[blue]Uninstalling Pieces CLI via chocolatey...")
            subprocess.run(["choco", "uninstall", "pieces-cli", "-y"], check=True)
            self._post_uninstall_cleanup(remove_config)
            Settings.logger.print("[green]✓ Pieces CLI uninstalled successfully!")
            return 0

        except subprocess.CalledProcessError as e:
            return _handle_subprocess_error("uninstalling", "chocolatey", e)

    def _uninstall_winget_version(self, remove_config: bool = False) -> int:
        """Uninstall Pieces CLI installed via winget."""
        try:
            Settings.logger.print("[blue]Uninstalling Pieces CLI via winget...")
            subprocess.run(
                ["winget", "uninstall", "MeshIntelligentTechnologies.PiecesCLI", "--silent"],
                check=True,
            )
            self._post_uninstall_cleanup(remove_config)
            Settings.logger.print("[green]✓ Pieces CLI uninstalled successfully!")
            return 0

        except subprocess.CalledProcessError as e:
            return _handle_subprocess_error("uninstalling", "winget", e)

    def execute(self, **kwargs) -> int:
        remove_config = kwargs.get("remove_config", False)

        operation_map = {
            "installer": lambda **kw: self._uninstall_installer_version(
                kw.get("remove_config", False)
            ),
            "homebrew": lambda **kw: self._uninstall_homebrew_version(
                kw.get("remove_config", False)
            ),
            "pip": lambda **kw: self._uninstall_pip_version(
                kw.get("remove_config", False)
            ),
            "chocolatey": lambda **kw: self._uninstall_chocolatey_version(
                kw.get("remove_config", False)
            ),
            "winget": lambda **kw: self._uninstall_winget_version(
                kw.get("remove_config", False)
            ),
        }

        return _execute_operation_by_type(operation_map, remove_config=remove_config)


class ManageCommandGroup(CommandGroup):
    """Manage command group for CLI maintenance operations."""

    def get_name(self) -> str:
        return "manage"

    def get_help(self) -> str:
        return "Manage Pieces CLI installation"

    def get_description(self) -> str:
        return "Manage the Pieces CLI installation including updating to the latest version and uninstalling the tool. Automatically detects installation method (pip, homebrew, chocolatey, winget, or installer script) and uses appropriate tools."

    def get_examples(self) -> list[str]:
        return [
            "pieces manage update",
            "pieces manage uninstall",
            "pieces manage update --force",
            "pieces manage uninstall --remove-config",
        ]

    def get_docs(self) -> str:
        return URLs.CLI_MANAGE_DOCS.value

    def _register_subcommands(self):
        """Register all manage subcommands."""
        self.add_subcommand(ManageUpdateCommand())
        self.add_subcommand(ManageStatusCommand())
        self.add_subcommand(ManageUninstallCommand())
