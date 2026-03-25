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

        builder.section(
            header="PiecesOS Launch:",
            command_template="pieces config --auto-launch-pieces-os",
        ).example(
            "pieces config --auto-launch-pieces-os",
            "Enable automatic PiecesOS startup when a command needs it",
        ).example(
            "pieces config --no-auto-launch-pieces-os",
            "Disable automatic PiecesOS startup",
        )

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
        parser.add_argument(
            "--auto-launch-pieces-os",
            dest="auto_launch_pieces_os",
            action=argparse.BooleanOptionalAction,
            default=None,
            help="Automatically launch PiecesOS when a command requires it",
        )

    def execute(self, **kwargs) -> int:
        """Execute the config command."""

        editor = kwargs.get("editor")
        auto_launch = kwargs.get("auto_launch_pieces_os")
        if editor:
            Settings.cli_config.editor = editor
            Settings.logger.print(f"Editor set to: {editor}")
        elif auto_launch is not None:
            Settings.cli_config.auto_launch_pieces_os = auto_launch
            status = "Enabled" if auto_launch else "Disabled"
            Settings.logger.print(f"Auto-launch PiecesOS: {status}")
        else:
            Settings.logger.print("Current configuration:")
            Settings.logger.print(f"Editor: {Settings.cli_config.editor or 'Not set'}")
            Settings.logger.print(
                "Auto-launch PiecesOS: "
                + ("Enabled" if Settings.cli_config.auto_launch_pieces_os else "Disabled")
            )
        return 0
