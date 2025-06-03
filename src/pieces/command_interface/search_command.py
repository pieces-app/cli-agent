import argparse
from typing import Optional
from pieces.base_command import BaseCommand
from pieces.urls import URLs
from pieces.core.search_command import search


class SearchCommand(BaseCommand):
    """Command to search for materials."""

    def get_name(self) -> str:
        return "search"

    def get_help(self) -> str:
        return "Perform a search for materials using the specified query string"

    def get_description(self) -> str:
        return "Search through your materials using various search modes including fuzzy search, neural code search, and full text search"

    def get_examples(self) -> list[str]:
        return [
            "pieces search",
            "pieces search 'python function'",
            "pieces search --mode ncs 'async await'",
            "pieces search --mode fts 'TODO comments'",
        ]

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
        query = kwargs.get("query")
        if query:
            query = [query]
        return search(query, **kwargs)
