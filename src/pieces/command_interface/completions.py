import argparse
from importlib.resources import files
from pieces.base_command import BaseCommand
from pieces.settings import Settings
from pieces.urls import URLs
from pieces import __version__
import sys
from rich.markdown import Markdown


class CompletionCommand(BaseCommand):
    """Command to print shell completion scripts."""

    def get_name(self) -> str:
        return "completion"

    def get_help(self) -> str:
        return "Outputs shell completion scripts"

    def get_description(self) -> str:
        return "Print the auto-completion script for bash, zsh, or fish"

    def get_examples(self) -> list[str]:
        return [
            "pieces completion bash",
            "pieces completion zsh",
            "pieces completion fish",
        ]

    def get_docs(self) -> str:
        return URLs.CLI_COMPLETION_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "shell",
            choices=["bash", "zsh", "fish"],
            help="Shell to generate the completion script for",
        )

    def execute(self, **kwargs) -> int:
        """Print the completion script for the given shell."""
        shell = kwargs["shell"]
        try:
            if __version__ == "dev":
                Settings.logger.print(
                    Markdown(
                        f"Please use `python completion_scripts/autocomplete_generator.py --{shell}` to generate the completion"
                    )
                )
                return 3
            path = files("pieces.completions").joinpath(shell)
            content = path.read_text(encoding="utf-8")
            print(content)
            return 0
        except FileNotFoundError:
            print(f"Error: No completion script found for '{shell}'", file=sys.stderr)
            return 1
