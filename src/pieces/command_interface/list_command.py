import argparse
from pieces.base_command import BaseCommand
from pieces.urls import URLs
from pieces.core.list_command import ListCommand as ListCore
from pieces.help_structure import HelpBuilder


class ListCommand(BaseCommand):
    """Command to list various Pieces resources."""

    def get_name(self) -> str:
        return "list"

    def get_aliases(self) -> list[str]:
        return ["drive"]

    def get_help(self) -> str:
        return "List materials or apps or models"

    def get_description(self) -> str:
        return "List and browse various Pieces resources including code materials, connected applications, and available AI models. Use the editor flag to open snippets directly in your default editor."

    def get_examples(self):
        """Return structured examples for the list command."""
        builder = HelpBuilder()

        # Basic listing examples
        builder.section(
            header="Basic Usage:", command_template="pieces list [TYPE]"
        ).example("pieces list", "List all materials (default)").example(
            "pieces list materials", "Explicitly list materials"
        ).example("pieces list apps", "List connected applications").example(
            "pieces list models", "List available AI models"
        )

        # Advanced usage
        builder.section(
            header="Advanced Options:", command_template="pieces list [OPTIONS]"
        ).example(
            "pieces list --editor", "List materials and open selected in editor"
        ).example("pieces drive", "Alias for list command")

        return builder.build()

    def get_docs(self) -> str:
        return URLs.CLI_LIST_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        """Add list-specific arguments."""
        parser.add_argument(
            "type",
            nargs="?",
            type=str,
            default="materials",
            help="Type of the list",
            choices=["materials", "apps", "models"],
        )
        parser.add_argument(
            "--editor",
            "-e",
            dest="editor",
            action="store_true",
            default=False,
            help="Open the chosen material in the editor",
        )

    def execute(self, **kwargs) -> int:
        """Execute the list command."""
        ListCore.list_command(**kwargs)
        return 0
