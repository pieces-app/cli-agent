"""TUI command class for proper command registration."""

import argparse
import subprocess
import sys
from pieces.base_command import BaseCommand
from pieces.help_structure import CommandHelp, HelpBuilder
from pieces.settings import Settings


class TUICommand(BaseCommand):
    """Command to launch the TUI (Text User Interface) for Pieces CLI."""

    support_headless = False

    def get_name(self) -> str:
        """Return the primary command name."""
        return "tui"

    def get_aliases(self) -> list[str]:
        """Return alternative names for this command."""
        return ["ui"]

    def get_help(self) -> str:
        """Return a short help message for the command."""
        return "Launch the TUI (Text User Interface) mode"

    def get_description(self) -> str:
        """Return a detailed description for the command."""
        import textwrap

        return textwrap.dedent("""
        Launch the Pieces CLI in TUI mode with a graphical interface.
        The TUI includes a main chat area, copilot panel on the right,
        and text input at the bottom for interactive conversations.
        """)

    def get_examples(self) -> CommandHelp:
        """Return a list of usage examples."""
        build = HelpBuilder()
        build.section(header="Open the TUI").example(
            "pieces tui", "Launch the TUI interface"
        ).example("pieces ui", "Same as pieces tui")
        build.section(header="Install TUI dependencies").example(
            "pieces tui install", "Install TUI dependencies if not already installed"
        )
        return build.build()

    def add_arguments(self, parser: argparse.ArgumentParser):
        """Add command-specific arguments to the parser."""
        parser.add_argument(
            "install",
            nargs="?",
            const="install",
            help="Install the TUI dependencies if not already installed",
        )

    def install_tui(self) -> int:
        import importlib.util

        if importlib.util.find_spec("textual"):
            Settings.logger.print("TUI dependencies already installed.")
            return 0

        if self._is_frozen():
            Settings.logger.print(
                "[bold red]✗ Cannot install TUI dependencies in standalone executable[/bold red]\n"
            )
            return 1

        Settings.logger.print("Installing TUI dependencies...")
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "textual[syntax]",
            ],
            capture_output=True,
        )
        Settings.logger.print(
            "[green]TUI dependencies installed successfully![/green]"
            if result.returncode == 0
            else "[red]Failed to install TUI dependencies.[/red]"
        )
        if result.stderr:
            Settings.logger.error(
                f"stdout: {result.stdout.decode().strip()}\nstderr: {result.stderr.decode().strip()}"
            )
        return result.returncode

    def _is_frozen(self) -> bool:
        """Check if running from PyInstaller bundle."""
        return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")

    def execute(self, **kwargs) -> int:
        """Execute the TUI command."""
        if kwargs.get("install") == "install":
            return self.install_tui()

        try:
            from pieces.tui.app import run_tui

            run_tui()

        except ImportError:
            Settings.logger.print(
                "[bold yellow]⚠️ Pieces TUI is in beta[/bold yellow] and requires you to install: "
                "[bold green]pieces tui install[/bold green]"
            )
            return 1
        except KeyboardInterrupt:
            return 0
        except Exception as e:
            Settings.logger.error(f"TUI error: {e}")
            Settings.show_error(
                "TUI Error", f"An error occurred while running the TUI: {e}"
            )
            return 1

        return 0
