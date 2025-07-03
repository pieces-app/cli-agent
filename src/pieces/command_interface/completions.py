import argparse
from importlib.resources import files
from pieces.base_command import BaseCommand
from pieces.settings import Settings
from pieces.urls import URLs
from pieces import __version__
from rich.markdown import Markdown
from typing import Literal, List, get_args


supported_shells_type = Literal["bash", "zsh", "fish", "powershell"]
supported_shells: List[supported_shells_type] = list(get_args(supported_shells_type))


class CompletionCommand(BaseCommand):
    """Command to show shell completion scripts."""

    def get_name(self) -> str:
        return "completion"

    def get_help(self) -> str:
        return "Display shell completion scripts"

    def get_description(self) -> str:
        return "Display the raw completion script for a specific shell"

    def get_examples(self) -> list[str]:
        return [
            "pieces completion bash",
            "pieces completion zsh",
            "pieces completion fish",
            "pieces completion powershell",
        ]

    def get_docs(self) -> str:
        return URLs.CLI_COMPLETION_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "shell",
            choices=supported_shells,
            help="Shell to show the completion script for",
        )

    def execute(self, **kwargs) -> int:
        """Execute the completion command."""
        shell = kwargs["shell"]

        if __version__ == "dev":
            Settings.logger.print(
                Markdown(
                    f"Please use `python completion_scripts/autocomplete_generator.py --{shell}` to generate the completion"
                )
            )
            return 3

        return self._show_completion(shell)

    def _show_completion(self, shell: str) -> int:
        """Display the completion script source."""
        try:
            path = files("pieces.completions").joinpath(shell)
            content = path.read_text(encoding="utf-8")
            print(content)  # Use print to avoid any formatting issues
            return 0
        except FileNotFoundError:
            Settings.logger.console_error.print(
                f"Error: No completion script found for '{shell}'"
            )
            return 1
