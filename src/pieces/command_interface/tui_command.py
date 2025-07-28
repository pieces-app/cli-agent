"""TUI command class for proper command registration."""

import argparse
from pieces.base_command import BaseCommand
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
        return """
        Launch the Pieces CLI in TUI mode with a graphical interface.
        The TUI includes a main chat area, copilot panel on the right,
        and text input at the bottom for interactive conversations.
        """

    def get_examples(self) -> list[str]:
        """Return a list of usage examples."""
        return [
            "pieces tui                    # Launch the TUI interface",
            "pieces ui                     # Same as above (alias)",
            "pieces tui --help             # Show TUI help",
        ]

    def add_arguments(self, parser: argparse.ArgumentParser):
        """Add command-specific arguments to the parser."""
        pass

    def execute(self, **kwargs) -> int:
        """Execute the TUI command."""

        try:
            # Import here to avoid loading textual unless needed
            from pieces.tui.app import run_tui

            run_tui()

        except ImportError as e:
            print(
                "Error: Textual library not found. Please install with: pip install textual"
            )
            print(f"Import error: {e}")
            return 1

        except KeyboardInterrupt:
            print("\nTUI application closed by user.")
            return 0

        except Exception as e:
            Settings.logger.error(f"TUI error: {e}")
            Settings.show_error(
                "TUI Error", f"An error occurred while running the TUI: {e}"
            )
            return 1

        return 0
