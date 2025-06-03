import argparse
from pieces.base_command import BaseCommand
from pieces.urls import URLs
from pieces.core.list_command import ListCommand as ListCore


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

    def get_examples(self) -> list[str]:
        return [
            "pieces list",
            "pieces list materials",
            "pieces list apps",
            "pieces list models",
            "pieces drive",
            "pieces list --editor",
        ]

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
