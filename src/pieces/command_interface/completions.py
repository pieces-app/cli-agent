import argparse
from importlib.resources import files
from pieces.base_command import BaseCommand, CommandGroup
from pieces.settings import Settings
from pieces.urls import URLs
from pieces import __version__
import os
from pathlib import Path
from rich.markdown import Markdown
import json
from datetime import datetime
from typing import Literal, List, get_args


supported_shells_type = Literal["bash", "zsh", "fish"]
supported_shells: List[supported_shells_type] = list(get_args(supported_shells_type))


def _get_completion_versions_file() -> Path:
    """Get the path to the completion versions file."""
    return Path(Settings.pieces_data_dir) / "completion_versions.json"


def _load_completion_data() -> dict:
    """Load completion version data from JSON file."""
    file_path = _get_completion_versions_file()
    if file_path.exists():
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def _save_completion_data(data: dict):
    """Save completion version data to JSON file."""
    file_path = _get_completion_versions_file()
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)


class CompletionInstallCommand(BaseCommand):
    """Subcommand to install shell completion scripts."""

    _is_command_group = True

    def get_name(self) -> str:
        return "install"

    def get_help(self) -> str:
        return "Install completion script to your shell configuration"

    def get_description(self) -> str:
        return "Install shell completion scripts for bash, zsh, or fish"

    def get_examples(self) -> list[str]:
        return [
            "pieces completion install bash",
            "pieces completion install zsh",
            "pieces completion install fish",
            "pieces completion install bash --force",
        ]

    def get_docs(self) -> str:
        return URLs.CLI_COMPLETION_INSTALL_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "shell",
            choices=supported_shells,
            help="Shell to install the completion script for",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force reinstall even if already installed",
        )

    def execute(self, **kwargs) -> int:
        """Execute the install command."""
        shell = kwargs["shell"]
        force = kwargs.get("force", False)

        if __version__ == "dev":
            Settings.logger.print(
                Markdown(
                    f"Please use `python completion_scripts/autocomplete_generator.py --{shell}` to generate the completion"
                )
            )
            return 3

        return self._install_completion(shell, force)

    def _check_installed_version(self, shell: str) -> tuple[bool, str]:
        """Check if completion is installed and return (is_installed, installed_version)."""
        data = _load_completion_data()
        shell_data = data.get(shell, {})

        if shell_data and "version" in shell_data:
            return True, shell_data["version"]
        return False, ""

    def _save_installed_version(self, shell: supported_shells_type):
        """Save the current version as the installed version."""
        data = _load_completion_data()

        # Update the data for this shell
        data[shell] = {
            "version": __version__,
            "installed_at": datetime.now().isoformat(),
            "install_path": str(self._find_and_prepare_completion_path(shell)),
        }

        # Save to file
        _save_completion_data(data)

    def _find_and_prepare_completion_path(self, shell: supported_shells_type) -> Path:
        """Find the best directory to install completion and prepare the path.

        Returns the full path where the completion file should be written.
        """
        home = Path.home()

        shell_config = {
            "bash": {
                "dirs": [
                    Path("/etc/bash_completion.d"),
                    Path("/usr/local/etc/bash_completion.d"),
                    home / ".bash_completion.d",
                ],
                "filename": "pieces",
            },
            "zsh": {
                "dirs": [
                    Path("/usr/local/share/zsh/site-functions"),
                    Path("/usr/share/zsh/site-functions"),
                    home / ".zsh/completions",
                ],
                "filename": "_pieces",
            },
            "fish": {
                "dirs": [home / ".config/fish/completions"],
                "filename": "pieces.fish",
            },
        }

        config = shell_config.get(shell)
        if not config:
            raise NotImplementedError(f"Shell '{shell}' is not supported")

        completion_dir = None
        for dir_path in config["dirs"]:
            if dir_path.exists() and os.access(dir_path, os.W_OK):
                completion_dir = dir_path
                break

        if not completion_dir:
            completion_dir = config["dirs"][-1]
            completion_dir.mkdir(parents=True, exist_ok=True)

        return completion_dir / config["filename"]

    def _print_shell_instructions(
        self, shell: supported_shells_type, completion_file: Path
    ):
        """Print shell-specific instructions for enabling completions."""
        console = Settings.logger.console

        if shell == "bash":
            console.print(
                "\nTo enable completions, add the following to your ~/.bashrc:"
            )
            console.print(f"[yellow]source {completion_file}[/yellow]")
            console.print("\nThen reload your shell or run:")
            console.print("[yellow]source ~/.bashrc[/yellow]")

        elif shell == "zsh":
            console.print("\nTo enable completions, ensure your ~/.zshrc includes:")
            console.print(f"[yellow]fpath=({completion_file.parent} $fpath)[/yellow]")
            console.print("[yellow]autoload -Uz compinit && compinit[/yellow]")
            console.print("\nThen reload your shell or run:")
            console.print("[yellow]source ~/.zshrc[/yellow]")

        elif shell == "fish":
            console.print(
                "\nCompletions will be available immediately in new fish shells."
            )
            console.print("To reload in current shell, run:")
            console.print("[yellow]source ~/.config/fish/config.fish[/yellow]")

    def _install_completion(
        self, shell: supported_shells_type, force: bool = False
    ) -> int:
        """Install the completion script to the appropriate location."""
        console = Settings.logger.console

        is_installed, installed_version = self._check_installed_version(shell)
        if is_installed and not force:
            if installed_version == __version__:
                console.print(
                    f"[yellow]ℹ[/yellow] Completion for {shell} is already installed (version {installed_version})."
                )
                console.print("Use --force to reinstall.")
                return 0
            else:
                console.print(
                    f"[yellow]ℹ[/yellow] Found existing completion for {shell} (version {installed_version})."
                )
                console.print(f"Updating to version {__version__}...")

        try:
            path = files("pieces.completions").joinpath(shell)
            content = path.read_text(encoding="utf-8")
            completion_file = self._find_and_prepare_completion_path(shell)
            completion_file.write_text(content)
            console.print(
                f"[green]✓[/green] {shell.capitalize()} completion installed to: {completion_file}"
            )
            self._print_shell_instructions(shell, completion_file)
            self._save_installed_version(shell)
            if is_installed and installed_version != __version__:
                console.print(
                    f"\n[green]✓[/green] Successfully updated from version {installed_version} to {__version__}"
                )

            return 0

        except FileNotFoundError:
            Settings.logger.console_error.print(
                f"[red]Error:[/red] No completion script found for '{shell}'"
            )
            return 1


class CompletionShowCommand(BaseCommand):
    """Subcommand to show shell completion scripts."""

    _is_command_group = True

    def get_name(self) -> str:
        return "show"

    def get_help(self) -> str:
        return "Display the completion script source"

    def get_description(self) -> str:
        return "Display the raw completion script for a specific shell"

    def get_examples(self) -> list[str]:
        return [
            "pieces completion show bash",
            "pieces completion show zsh",
            "pieces completion show fish",
        ]

    def get_docs(self) -> str:
        return URLs.CLI_COMPLETION_SHOW_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "shell",
            choices=supported_shells,
            help="Shell to show the completion script for",
        )

    def execute(self, **kwargs) -> int:
        """Execute the show command."""
        shell = kwargs["shell"]

        if __version__ == "dev":
            Settings.logger.print(
                Markdown(
                    f"Please use `python completion_scripts/autocomplete_generator.py --{shell}` to generate the completion"
                )
            )
            return 3

        return self._show_completion(shell)

    def _show_completion(self, shell: str) -> int:
        """Display the completion script source."""
        try:
            path = files("pieces.completions").joinpath(shell)
            content = path.read_text(encoding="utf-8")
            print(content)  # Leave it as print to avoid any formatting issues
            return 0
        except FileNotFoundError:
            Settings.logger.console_error.print(
                f"Error: No completion script found for '{shell}'"
            )
            return 1


class CompletionStatusCommand(BaseCommand):
    """Subcommand to check completion installation status."""

    _is_command_group = True

    def get_name(self) -> str:
        return "status"

    def get_help(self) -> str:
        return "Check completion installation status"

    def get_description(self) -> str:
        return "Display the current installation status of shell completions"

    def get_examples(self) -> list[str]:
        return ["pieces completion status"]

    def get_docs(self) -> str:
        return URLs.CLI_COMPLETION_STATUS_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        pass

    def execute(self, **kwargs) -> int:
        """Execute the status command."""
        return self._show_status()

    def _show_status(self) -> int:
        """Show the status of completion installations."""
        console = Settings.logger.console

        console.print("\n[bold underline]Pieces CLI Completion Status[/bold underline]")
        console.print(
            f"[dim]Current CLI version:[/dim] [yellow]{__version__}[/yellow]\n"
        )

        shells = supported_shells
        data = _load_completion_data()

        for shell in shells:
            shell_data = data.get(shell, {})
            is_installed = bool(shell_data)

            if is_installed:
                installed_version = shell_data.get("version", "Unknown")
                if installed_version == __version__:
                    status = "[green]✓ Up to date[/green]"
                else:
                    status = f"[yellow]⚠ Outdated (v{installed_version})[/yellow]"

                # Show installation details
                console.print(f"[bold cyan]{shell.capitalize()}:[/bold cyan] {status}")
                console.print(
                    f"  [dim]Version:[/dim] [white]{installed_version}[/white]"
                )
                if "install_path" in shell_data:
                    console.print(
                        f"  [dim]Path:[/dim] [blue]{shell_data['install_path']}[/blue]"
                    )
                if "installed_at" in shell_data:
                    try:
                        installed_time = datetime.fromisoformat(
                            shell_data["installed_at"]
                        )
                        formatted_time = installed_time.strftime(
                            "%B %d, %Y at %I:%M %p"
                        )
                        console.print(
                            f"  [dim]Installed:[/dim] [magenta]{formatted_time}[/magenta]"
                        )
                    except Exception as e:
                        Settings.logger.error("couldn't parse date", e)
                        console.print(
                            f"  [dim]Installed:[/dim] [magenta]{shell_data['installed_at']}[/magenta]"
                        )
            else:
                console.print(
                    f"[bold cyan]{shell.capitalize()}:[/bold cyan] [red]✗ Not installed[/red]"
                )

        console.print()
        console.print("[dim]To install or update completions, run:[/dim]")
        console.print("  [yellow]pieces completion install <shell>[/yellow]")

        return 0


class CompletionCommandGroup(CommandGroup):
    """Completion command group for managing shell completions."""

    def get_name(self) -> str:
        return "completion"

    def get_help(self) -> str:
        return "Manage shell completion scripts"

    def get_description(self) -> str:
        return "Install, show, or check status of shell completion scripts for bash, zsh, or fish"

    def get_examples(self) -> list[str]:
        return [
            "pieces completion",
            "pieces completion install bash",
            "pieces completion show zsh",
            "pieces completion status",
        ]

    def get_docs(self) -> str:
        return URLs.CLI_COMPLETION_DOCS.value

    def _register_subcommands(self):
        """Register all completion subcommands."""
        self.add_subcommand(CompletionInstallCommand())
        self.add_subcommand(CompletionShowCommand())
        self.add_subcommand(CompletionStatusCommand())

    @classmethod
    def check_for_updates(cls) -> None:
        """Check if any installed completions need updating (called on CLI startup)."""
        if __version__ == "dev":
            return

        outdated_shells = []

        data = _load_completion_data()
        for shell in supported_shells:
            shell_data = data.get(shell, {})
            if shell_data and shell_data.get("version", "") != __version__:
                outdated_shells.append(shell)

        if outdated_shells:
            console = Settings.logger.console
            console.print(
                f"\n[yellow]ℹ[/yellow] Shell completions for {', '.join(outdated_shells)} are outdated."
            )
            console.print("Run [yellow]pieces completion status[/yellow] for details.")
            console.print(
                "Run [yellow]pieces completion install <shell>[/yellow] to update.\n"
            )
