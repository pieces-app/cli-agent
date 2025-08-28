import argparse
from pieces.base_command import BaseCommand
from pieces.urls import URLs
from pieces.settings import Settings
from pieces.help_structure import HelpBuilder


class ConfigCommand(BaseCommand):
    """Command to configure Pieces CLI settings."""

    def get_name(self) -> str:
        return "config"

    def get_help(self) -> str:
        return "Configure settings"

    def get_description(self) -> str:
        return "Configure various Pieces CLI settings including default editor and other preferences"

    def get_examples(self):
        """Return structured examples for the config command."""
        builder = HelpBuilder()

        # Basic configuration
        builder.section(
            header="View Configuration:", command_template="pieces config"
        ).example("pieces config", "Display current configuration settings")

        # Editor configuration
        builder.section(
            header="Set Default Editor:",
            command_template="pieces config --editor [EDITOR]",
        ).example(
            "pieces config --editor code", "Set VS Code as default editor"
        ).example(
            "pieces config --editor subl", "Set Sublime Text as default editor"
        ).example(
            "pieces config --editor nvim", "Set Neovim as default editor"
        ).example("pieces config --editor vim", "Set Vim as default editor")

        return builder.build()

    def get_docs(self) -> str:
        return URLs.CLI_CONFIG_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        """Add config-specific arguments."""
        parser.add_argument(
            "--editor",
            "-e",
            dest="editor",
            type=str,
            help="Set the default code editor",
        )

    def execute(self, **kwargs) -> int:
        """Execute the config command."""

        editor = kwargs.get("editor")
        if editor:
            Settings.cli_config.editor = editor
            Settings.logger.print(f"Editor set to: {editor}")
        else:
            Settings.logger.print("Current configuration:")
            Settings.logger.print(f"Editor: {Settings.cli_config.editor or 'Not set'}")
        return 0
