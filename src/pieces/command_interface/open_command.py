import argparse
from pieces.base_command import BaseCommand
from pieces.urls import URLs
from pieces.core import open_command
from pieces.help_structure import HelpBuilder


class OpenCommand(BaseCommand):
    """Command to open PiecesOS or Applet components."""

    def get_name(self) -> str:
        return "open"

    def get_help(self) -> str:
        return "Opens PiecesOS or Applet"

    def get_description(self) -> str:
        return "Open various Pieces applications and components including PiecesOS, Copilot, Drive, and Settings from the command line"

    def get_examples(self):
        """Return structured examples for the open command."""
        builder = HelpBuilder()

        # Basic usage
        builder.section(
            header="Basic Usage:", command_template="pieces open [COMPONENT]"
        ).example("pieces open", "Open the default Pieces component")

        # Specific components
        builder.section(
            header="Open Specific Components:",
            command_template="pieces open --[OPTION]",
        ).example("pieces open --pieces_os", "Open PiecesOS").example(
            "pieces open --copilot", "Open Pieces Copilot"
        ).example("pieces open --drive", "Open Pieces Drive").example(
            "pieces open --settings", "Open Pieces Settings"
        ).example("pieces open --ltm", "Open Long-Term Memory")

        return builder.build()

    def get_docs(self) -> str:
        return URLs.CLI_OPEN_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        """Add open-specific arguments."""
        parser.add_argument(
            "-p", "--pieces_os", dest="pos", action="store_true", help="Opens PiecesOS"
        )
        parser.add_argument(
            "-c",
            "--copilot",
            dest="copilot",
            action="store_true",
            help="Opens Pieces Copilot",
        )
        parser.add_argument(
            "-d",
            "--drive",
            dest="drive",
            action="store_true",
            help="Opens Pieces Drive",
        )
        parser.add_argument(
            "-s",
            "--settings",
            dest="settings",
            action="store_true",
            help="Opens Pieces Settings",
        )
        parser.add_argument(
            "--ltm",
            dest="ltm",
            action="store_true",
            help="Opens Pieces LTM (Long-Term Memory)",
        )

    def execute(self, **kwargs) -> int:
        """Execute the open command."""
        open_command(**kwargs)
        return 0
