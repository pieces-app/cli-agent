import argparse
from pieces.base_command import BaseCommand
from pieces.urls import URLs
from pieces.copilot import AskStream


class AskCommand(BaseCommand):
    """Command to ask questions to the Pieces Copilot."""

    def __init__(self):
        super().__init__()
        self.ask_stream = AskStream()

    def get_name(self) -> str:
        return "ask"

    def get_help(self) -> str:
        return "Ask a question to the Copilot"

    def get_description(self) -> str:
        return "Ask questions to the Pieces Copilot AI assistant with context from files, saved materials, or your long-term memory (LTM). Get intelligent code assistance and explanations"

    def get_examples(self) -> list[str]:
        return [
            "pieces ask 'how to implement a REST API'",
            "pieces ask 'debug the main function' -f main.py utils.py",
            "pieces ask 'What are these snippets about' -m 1 2 3",
            "pieces ask 'What I was working on yesterday' --ltm",
        ]

    def get_docs(self) -> str:
        return URLs.CLI_ASK_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        """Add ask-specific arguments."""
        parser.add_argument(
            "query",
            type=str,
            help="Question to be asked to the Copilot",
            nargs="?",
            default=None,
        )
        parser.add_argument(
            "--files",
            "-f",
            nargs="*",
            type=str,
            dest="files",
            help="Provide one or more files or folders as context (absolute or relative path)",
        )
        parser.add_argument(
            "--materials",
            "-m",
            nargs="*",
            type=int,
            dest="materials",
            help="Use one or more saved materials as context (provide material's index).",
        )
        parser.add_argument(
            "--ltm",
            action="store_true",
            dest="ltm",
            help="Enable Long-Term Memory (LTM) to include prior context",
        )

    def execute(self, **kwargs) -> int:
        """Execute the ask command."""
        self.ask_stream.ask(**kwargs)
        return 0
