import argparse
import sys
from importlib.resources import files
from pieces.base_command import BaseCommand
from pieces.settings import Settings
from pieces.urls import URLs
from pieces.help_structure import HelpBuilder
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

    def get_examples(self):
        """Return structured examples for the completion command."""
        builder = HelpBuilder()

        builder.section(
            header="Shell Completion Scripts:",
            command_template="pieces completion [SHELL]",
        ).example("pieces completion bash", "Generate Bash completion script").example(
            "pieces completion zsh", "Generate Zsh completion script"
        ).example("pieces completion fish", "Generate Fish completion script").example(
            "pieces completion powershell", "Generate PowerShell completion script"
        )

        return builder.build()

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

            try:
                print(content)
            except OSError as e:
                if (
                    e.errno == 22
                ):  # Invalid argument - likely Windows console limitation
                    self._write_content_chunked(content)
                else:
                    raise  # Re-raise if it's a different OSError

            return 0
        except (FileNotFoundError, ModuleNotFoundError):
            Settings.logger.console_error.print(
                f"Error: No completion script found for '{shell}'"
            )
            return 1

    def _write_content_chunked(self, content: str, chunk_size: int = 8192) -> None:
        """Write content in chunks to handle large output on Windows consoles."""
        try:
            # Try sys.stdout.write first as it handles large strings better
            sys.stdout.write(content)
            sys.stdout.flush()
        except OSError:
            # Fallback to chunked writing if that fails too
            for i in range(0, len(content), chunk_size):
                chunk = content[i : i + chunk_size]
                sys.stdout.write(chunk)
                sys.stdout.flush()
