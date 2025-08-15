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
            # Copilot Queries without Long-Term Memory
            "pieces ask 'how to implement authentication with JWT'",
            "pieces ask 'debug this React component error' -f components/Header.jsx utils/api.js",
            "pieces ask 'explain what this Python class does' -f models/user.py",
            "pieces ask 'summarize these saved code snippets' -m 5 8 12",
            
            # Copilot Queries with Long-Term Memory enabled  
            "pieces ask 'what Python projects was I working on in the last 3 months' --ltm",
            "pieces ask 'show me the database migration work from November 2024' --ltm", 
            "pieces ask 'what did Alex and I pair on December 5th' --ltm",
            "pieces ask 'what changes did I make today in Cursor editor' --ltm",
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
