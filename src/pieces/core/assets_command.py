import os
import sys
from typing import Optional, Tuple
import pyperclip
import subprocess
import shutil

from pieces.urls import URLs
from pieces.utils import get_file_extension
from pieces.gui import print_asset_details, space_below, double_line
from pieces.settings import Settings
from pieces.core.config_command import ConfigCommands
from pieces._vendor.pieces_os_client.wrapper.basic_identifier.asset import BasicAsset

from pygments import highlight
from pygments.util import ClassNotFound
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import TerminalFormatter

from rich.markdown import Markdown

from pieces._vendor.pieces_os_client.exceptions import NotFoundException


def check_assets_existence(func):
    """Decorator to ensure user has assets."""

    def wrapper(*args, **kwargs):
        assets = Settings.pieces_client.assets()  # Check if there is an asset
        if not assets:
            return Settings.show_error(
                "No materials found", "Please create an material first."
            )
        return func(*args, **kwargs)

    return wrapper


def check_asset_selected(func):
    """
    Decorator to check if there is a selected asset or not and if it is valid id.
    If valid id it returns the asset_data to the called function.
    """

    def wrapper(*args, **kwargs):
        from pieces.core.list_command import ListCommand

        try:
            if AssetsCommands.current_asset is None:
                raise ValueError("No material selected")
            AssetsCommands.current_asset.asset  # Check if the current asset is vaild
        except (ValueError, NotFoundException):
            ListCommand.list_assets()
        return func(asset=AssetsCommands.current_asset, *args, **kwargs)

    return wrapper


class AssetsCommands:
    current_asset: Optional[BasicAsset] = None

    @classmethod
    @check_assets_existence
    def open_asset(cls, asset_id: str, **kwargs):
        try:
            cls.current_asset = BasicAsset(asset_id)

        except IndexError:
            return Settings.show_error(
                "Invalid material index or material not found.",
                "Please choose from the list or use 'pieces list assets'",
            )

        code_content = cls.current_asset.raw_content
        open_in_editor = kwargs.get("editor")

        # Check if -e flag is used or open_in_editor is True
        if open_in_editor:
            check, editor = cls.check_editor()
            if not check:
                return
            file_extension = get_file_extension(cls.current_asset.classification)

            # Ensure the directory exists, create it if not
            if not os.path.exists(Settings.open_snippet_dir):
                os.makedirs(Settings.open_snippet_dir)

            file_path = os.path.join(
                Settings.open_snippet_dir, f"{cls.current_asset.id}{file_extension}"
            )

            # Save the code to a file in the default directory
            if isinstance(code_content, str):  # Code string raw
                with open(file_path, "w") as file:
                    file.write(code_content)
            else:  # Image bytes data
                with open(file_path, "wb") as file:
                    file.write(bytes(code_content))

            # Open the file with the configured editor
            editor_exe = shutil.which(editor)
            if not editor_exe:
                Settings.show_error(
                    "Editor executable not Found please make sure it is added to the path"
                )
                return
            try:
                subprocess.run([editor_exe, file_path])
            except Exception as e:
                Settings.show_error("Error in opening", e)

        else:
            # Determine the lexer
            Settings.logger.print("\nCode content:")
            cls.print_code(
                cls.current_asset.raw_content, cls.current_asset.classification
            )

    @classmethod
    def check_editor(cls) -> Tuple[bool, str]:
        if not cls.current_asset:
            return False, ""
        config = ConfigCommands.load_config()
        editor = config.get("editor")

        if editor:
            return True, editor
        else:
            print_asset_details(cls.current_asset)
            Settings.logger.print(
                Markdown(
                    "No editor configured. Use `pieces config --editor <editor_command>` to set an editor."
                )
            )
            return False, ""

    @staticmethod
    def print_code(code_content, classification=None):
        try:
            if classification:
                lexer = get_lexer_by_name(classification, stripall=True)
            else:
                raise ClassNotFound
        except ClassNotFound:
            lexer = guess_lexer(code_content)
        formatted_code = highlight(code_content, lexer, TerminalFormatter())
        print(formatted_code)

    @classmethod
    @check_asset_selected
    def save_asset(cls, asset: BasicAsset, **kwargs):
        if not cls.check_editor()[0]:
            return

        file_path = os.path.join(
            Settings.open_snippet_dir,
            f"{(asset.id)}{get_file_extension(asset.classification)}",
        )
        data = None
        try:
            with open(file_path, "r") as f:
                data = f.read()
        except FileNotFoundError:
            cls.open_asset(asset.id, editor=True)
            Settings.logger.print(
                Markdown(
                    "**Note:** Next time to open the material in your editor, use the `pieces list -e`"
                )
            )

        if data and asset.raw_content != data:
            Settings.logger.print(Markdown(f"Saving `{asset.name}` material"))
            asset.raw_content = data
        else:
            try:
                Settings.logger.input(
                    f"Content not changed.\n"
                    f"<Press enter when you finish editing {asset.name}>"
                )
                cls.save_asset(**kwargs)
            except KeyboardInterrupt:
                pass

    @classmethod
    @check_asset_selected
    def edit_asset(cls, asset: BasicAsset, **kwargs):
        print_asset_details(asset)
        name = kwargs.get("name", "")
        classification = kwargs.get("classification", "")

        if (
            not name and not classification
        ):  # If no name or no classification is provided
            # Ask the user for a new name
            name = Settings.logger.input(
                "Enter the new name for the material[leave blank to keep the same]: "
            ).strip()
            classification = Settings.logger.input(
                "Enter the classification for the material[leave blank to keep the same]: "
            ).strip()

        # Check if the user actually entered a name
        if name:
            asset.name = name
        if classification:
            asset.classification = classification

    @classmethod
    @check_asset_selected
    def share_asset(cls, asset: BasicAsset, **kwargs):
        Settings.logger.print("Generating shareable link")
        if asset.asset.shares:
            link = asset.asset.shares.iterable[0].link
        else:
            user = Settings.pieces_client.user_api.user_snapshot()
            # Update the local cache because the websockets are not running
            Settings.pieces_client.user.on_user_callback(user.user)
            try:
                share = asset.share()
            except PermissionError:
                Settings.logger.print(
                    Markdown(
                        "Please sign in using `pieces login` command and make sure you are connected to the Pieces cloud"
                    )
                )
                return
            link = share.iterable[0].link
        Settings.logger.print(f"Generated shareable link {link}")
        if Settings.logger.confirm("Do you want to open it in the browser?"):
            URLs.open_website(link)

    @classmethod
    @check_asset_selected
    def delete_asset(cls, asset: BasicAsset, **kwargs):
        print_asset_details(asset)

        confirm = Settings.logger.confirm(
            "Are you sure you really want to delete this material? This action cannot be undone."
        )
        if confirm:
            Settings.logger.print("Deleting material...")
            asset.delete()
            cls.current_asset = None
            space_below("Material Deleted")
        elif confirm == "n":
            Settings.logger.print("Deletion cancelled.")

    @classmethod
    def create_asset(cls, **kwargs):
        # TODO add more ways to create an asset such as an entire file

        # Save text copied to the clipboard as an asset
        text = None

        # Check if the content has the flag -c
        content_flag = kwargs.get("content", None)
        if content_flag:
            text = sys.stdin.read()
        else:
            try:
                text = pyperclip.paste()
            except pyperclip.PyperclipException as e:
                Settings.show_error("Error accessing clipboard:", str(e))
                return

        if not text:
            Settings.logger.print(
                "No content found in the clipboard to create a material."
            )
            return

        double_line("Content to save: ")
        cls.print_code(text)

        # Ask the user for confirmation to save
        try:
            user_input = Settings.logger.confirm("Do you want to save this content?")
        except EOFError:
            user_input = True

        if user_input:
            Settings.logger.print("Saving...\n")
            cls.current_asset = BasicAsset(
                BasicAsset.create(raw_content=text, metadata=None)
            )
            Settings.logger.print(
                Markdown("Material successfully saved. Use `pieces list` to view.")
            )
        elif user_input == "n":
            space_below("Save cancelled.")
