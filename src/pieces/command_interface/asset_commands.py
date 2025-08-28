import argparse
from pieces.base_command import BaseCommand
from pieces.urls import URLs
from pieces.core.assets_command import AssetsCommands
from pieces.help_structure import HelpBuilder


class SaveCommand(BaseCommand):
    """Command to save/update the current material."""

    def get_name(self) -> str:
        return "modify"

    def get_aliases(self) -> list[str]:
        return ["save"]

    def get_help(self) -> str:
        return "Updates the current material content"

    def get_description(self) -> str:
        return "Save or update changes to the currently selected material. Use this after making modifications to persist your changes"

    def get_examples(self):
        """Return structured examples for the save command."""
        builder = HelpBuilder()

        builder.section(header="Save Changes:", command_template="pieces save").example(
            "pieces save", "Save modifications to currently selected material"
        )

        return builder.build()

    def get_docs(self) -> str:
        return URLs.CLI_SAVE_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        """Save command has no additional arguments."""
        pass

    def execute(self, **kwargs) -> int:
        """Execute the save command."""
        AssetsCommands.save_asset(**kwargs)
        return 0


class DeleteCommand(BaseCommand):
    """Command to delete the current material."""

    def get_name(self) -> str:
        return "delete"

    def get_help(self) -> str:
        return "Delete the current material"

    def get_description(self) -> str:
        return "Permanently delete the currently selected material from your Pieces database. This action cannot be undone"

    def get_examples(self):
        """Return structured examples for the delete command."""
        builder = HelpBuilder()

        builder.section(
            header="Delete Material:", command_template="pieces delete"
        ).example("pieces delete", "Permanently delete currently selected material")

        return builder.build()

    def get_docs(self) -> str:
        return URLs.CLI_DELETE_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        """Delete command has no additional arguments."""
        pass

    def execute(self, **kwargs) -> int:
        """Execute the delete command."""
        AssetsCommands.delete_asset(**kwargs)
        return 0


class CreateCommand(BaseCommand):
    """Command to create a new material."""

    def get_name(self) -> str:
        return "create"

    def get_help(self) -> str:
        return "Create a new material"

    def get_description(self) -> str:
        return "Create a new code snippet or material in your Pieces database. You can create a snippet from clipboard content or enter it manually."

    def get_examples(self):
        """Return structured examples for the create command."""
        builder = HelpBuilder()

        # Basic creation
        builder.section(
            header="Create Material:", command_template="pieces create [OPTIONS]"
        ).example("pieces create", "Create material from clipboard content")

        # From content
        builder.section(
            header="Create from Input:", command_template="pieces create -c"
        ).example(
            "cat main.py | pieces create -c", "Create material from piped content"
        )

        return builder.build()

    def get_docs(self) -> str:
        return URLs.CLI_CREATE_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        """Add create-specific arguments."""
        parser.add_argument(
            "-c",
            "--content",
            dest="content",
            action="store_true",
            help="Enter snippet content manually in the terminal or via stdin",
        )

    def execute(self, **kwargs) -> int:
        """Execute the create command."""
        AssetsCommands.create_asset(**kwargs)
        return 0


class ShareCommand(BaseCommand):
    """Command to share the current material."""

    def get_name(self) -> str:
        return "share"

    def get_help(self) -> str:
        return "Share the current material"

    def get_description(self) -> str:
        return "Generate a shareable link for the currently selected material, allowing others to view and access your code snippet"

    def get_examples(self):
        """Return structured examples for the share command."""
        builder = HelpBuilder()

        builder.section(
            header="Share Material:", command_template="pieces share"
        ).example("pieces share", "Generate shareable link for current material")

        return builder.build()

    def get_docs(self) -> str:
        return URLs.CLI_SHARE_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        """Share command has no additional arguments."""
        pass

    def execute(self, **kwargs) -> int:
        """Execute the share command."""
        AssetsCommands.share_asset(**kwargs)
        return 0


class EditCommand(BaseCommand):
    """Command to edit an existing material."""

    def get_name(self) -> str:
        return "edit"

    def get_help(self) -> str:
        return "Edit an existing material's metadata"

    def get_description(self) -> str:
        return "Edit properties of an existing material including its name, language classification, and other metadata"

    def get_examples(self):
        """Return structured examples for the edit command."""
        builder = HelpBuilder()

        # Basic editing
        builder.section(
            header="Interactive Edit:", command_template="pieces edit"
        ).example("pieces edit", "Interactively edit material properties")

        # Specific edits
        builder.section(
            header="Direct Property Updates:", command_template="pieces edit [OPTIONS]"
        ).example("pieces edit --name 'New Name'", "Update material name").example(
            "pieces edit --classification python", "Change language classification"
        ).example(
            "pieces edit -n 'API Handler' -c javascript", "Update name and language"
        )

        return builder.build()

    def get_docs(self) -> str:
        return URLs.CLI_EDIT_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        """Add edit-specific arguments."""
        parser.add_argument(
            "--name",
            "-n",
            dest="name",
            help="Set a new name for the material",
            required=False,
        )
        parser.add_argument(
            "--classification",
            "-c",
            dest="classification",
            help="Reclassify a material (eg. py, js)",
            required=False,
        )

    def execute(self, **kwargs) -> int:
        """Execute the edit command."""
        AssetsCommands.edit_asset(**kwargs)
        return 0
