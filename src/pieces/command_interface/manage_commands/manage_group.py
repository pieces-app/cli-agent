"""
Main manage command group for CLI maintenance operations.
"""

from pieces.base_command import CommandGroup
from pieces.urls import URLs

from .update_command import ManageUpdateCommand
from .status_command import ManageStatusCommand
from .uninstall_command import ManageUninstallCommand


class ManageCommandGroup(CommandGroup):
    """Manage command group for CLI maintenance operations."""

    def get_name(self) -> str:
        return "manage"

    def get_help(self) -> str:
        return "Manage Pieces CLI installation"

    def get_description(self) -> str:
        return "Manage the Pieces CLI installation including updating to the latest version and uninstalling the tool. Automatically detects installation method (pip, homebrew, chocolatey, winget, or installer script) and uses appropriate tools."

    def get_examples(self) -> list[str]:
        return [
            "pieces manage update",
            "pieces manage uninstall",
            "pieces manage update --force",
            "pieces manage uninstall --remove-config",
        ]

    def get_docs(self) -> str:
        return URLs.CLI_MANAGE_DOCS.value

    def _register_subcommands(self):
        """Register all manage subcommands."""
        self.add_subcommand(ManageUpdateCommand())
        self.add_subcommand(ManageStatusCommand())
        self.add_subcommand(ManageUninstallCommand())

