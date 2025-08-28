import argparse
from typing import Optional
from pieces.base_command import BaseCommand
from pieces.urls import URLs
from pieces.core.search_command import search
from pieces.help_structure import HelpBuilder


class SearchCommand(BaseCommand):
    """Command to search for materials."""

    def get_name(self) -> str:
        return "search"

    def get_help(self) -> str:
        return "Perform a search for materials using the specified query string"

    def get_description(self) -> str:
        return "Search through your materials using various search modes including fuzzy search, neural code search, and full text search"

    def get_examples(self):
        """Return structured examples for the search command."""
        builder = HelpBuilder()

        # Basic search
        builder.section(
            header="Basic Search:", command_template="pieces search [QUERY]"
        ).example("pieces search", "Interactive search mode").example(
            "pieces search 'python function'", "Search for Python functions"
        )

        # Search modes
        builder.section(
            header="Search Modes:",
            command_template="pieces search --mode [MODE] [QUERY]",
        ).example(
            "pieces search --mode ncs 'async await'", "Neural code search"
        ).example(
            "pieces search --mode fts 'TODO comments'", "Full text search"
        ).example("pieces search --mode fuzzy 'auth'", "Fuzzy search (default)")

        return builder.build()

    def get_docs(self) -> str:
        return URLs.CLI_SEARCH_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        """Add search-specific arguments."""
        parser.add_argument(
            "query",
            type=str,
            nargs="?",
            default=None,
            help="Query string for the search",
        )
        parser.add_argument(
            "--mode",
            type=str,
            dest="search_type",
            default="fuzzy",
            choices=["fuzzy", "ncs", "fts"],
            help="Type of search",
        )

    def execute(self, **kwargs) -> int:
        """Execute the search command."""
        query = kwargs.pop("query", None)
        if query:
            query = [query]
        return search(query, **kwargs)
