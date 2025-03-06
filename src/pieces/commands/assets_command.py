import os
from typing import Optional
import pyperclip
import subprocess

from pieces.utils import get_file_extension
from pieces.gui import print_asset_details, space_below, double_line
from pieces.settings import Settings
from pieces.commands.config_command import ConfigCommands
from pieces.wrapper.basic_identifier.asset import BasicAsset

from pygments import highlight
from pygments.util import ClassNotFound
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import TerminalFormatter

from rich.markdown import Markdown
from rich.console import Console

from pieces_os_client.exceptions import NotFoundException


def check_assets_existence(func):
    """Decorator to ensure user has assets."""
    def wrapper(*args, **kwargs):
        assets = Settings.pieces_client.assets  # Check if there is an asset
        if not assets:
            return Settings.show_error("No materials found", "Please create an material first.")
        return func(*args, **kwargs)
    return wrapper


def check_asset_selected(func):
    """
    Decorator to check if there is a selected asset or not and if it is valid id.
    If valid id it returns the asset_data to the called function.
    """
    def wrapper(*args, **kwargs):
        from pieces.commands.list_command import ListCommand
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
            return Settings.show_error("Invalid material index or material not found.", "Please choose from the list or use 'pieces list assets'")

        print_asset_details(cls.current_asset)

        code_content = cls.current_asset.raw_content
        open_in_editor = kwargs.get('editor')

        # Check if -e flag is used or open_in_editor is True
        if open_in_editor:
            config = ConfigCommands.load_config()
            editor = config.get('editor')
            if editor:
                file_extension = get_file_extension(
                    cls.current_asset.classification)

                # Ensure the directory exists, create it if not
                if not os.path.exists(Settings.open_snippet_dir):
                    os.makedirs(Settings.open_snippet_dir)

                file_path = os.path.join(Settings.open_snippet_dir,
                                         f'{cls.current_asset.id}{file_extension}')

                # Save the code to a file in the default directory
                if isinstance(code_content, str):  # Code string raw
                    with open(file_path, 'w') as file:
                        file.write(code_content)
                else:  # Image bytes data
                    with open(file_path, 'wb') as file:
                        file.write(bytes(code_content))

                # Open the file with the configured editor
                try:
                    subprocess.run([editor, file_path])
                except Exception as e:
                    Settings.show_error("Error in opening", e)

            else:
                Console().print(Markdown(
                    "No editor configured. Use `pieces config --editor <editor_command>` to set an editor."))
        else:
            # Determine the lexer
            print("\nCode content:")
            cls.print_code(cls.current_asset.raw_content,
                           cls.current_asset.classification)

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
        if not asset:
            return
        console = Console()
        file_path = os.path.join(Settings.open_snippet_dir,
                                 f"{(asset.id)}{get_file_extension(asset.classification)}")
        data = None
        found_file = False
        try:
            found_file = True
            with open(file_path, "r") as f:
                data = f.read()
        except FileNotFoundError:
            res = console.input(
                "Seems you did not open that material yet.\nDo you want to open it in your editor? (y/n): ")
            if res == 'y':
                cls.open_asset(asset.id, editor=True)
                console.print(Markdown(
                    "**Note:** Next time to open the material in your editor, use the `pieces list -e`"))

        if data and asset.raw_content != data:
            console.print(Markdown(f"Saving `{asset.name}` material"))
            asset.raw_content = data
        else:
            if found_file:
                cls.open_asset(asset.id, editor=True)
            try:
                input(f"Content not changed.\n"
                      f"<Press enter when you finish editing {asset.name}>")
                cls.save_asset(**kwargs)
            except KeyboardInterrupt:
                pass

    @classmethod
    @check_asset_selected
    def edit_asset(cls, asset: BasicAsset, **kwargs):
        print_asset_details(asset)
        name = kwargs.get('name', '')
        classification = kwargs.get('classification', '')

        if not name and not classification:  # If no name or no classification is provided
            # Ask the user for a new name
            name = input(
                "Enter the new name for the material[leave blank to keep the same]: ").strip()
            classification = input(
                "Enter the classification for the material[leave blank to keep the same]: ").strip()

        # Check if the user actually entered a name
        if name:
            asset.name = name
        if classification:
            asset.classification = classification

    @classmethod
    @check_asset_selected
    def delete_asset(cls, asset: BasicAsset, **kwargs):
        print_asset_details(asset)

        confirm = input(
            "Are you sure you really want to delete this material? This action cannot be undone. (y/n): ").strip().lower()
        if confirm == 'y':
            print("Deleting asset...")
            asset.delete()
            cls.current_asset = None
            space_below("Material Deleted")
        elif confirm == 'n':
            print("Deletion cancelled.")
        else:
            print("Invalid input. Please type 'y' to confirm or 'n' to cancel.")

    @classmethod
    def create_asset(cls, **kwargs):
        # TODO add more ways to create an asset such as an entire file

        # Save text copied to the clipboard as an asset
        console = Console()
        try:
            text = pyperclip.paste()
            double_line("Content to save: ")

            cls.print_code(text)

            # Ask the user for confirmation to save
            user_input = input(
                "Do you want to save this content? (y/n): ").strip().lower()
            if user_input == 'y':
                console.print("Saving...\n")
                cls.current_asset = BasicAsset(
                    BasicAsset.create(raw_content=text, metadata=None))

                console.print(
                    Markdown("Material successfully saved. Use `pieces list` to view."))
                # Add your saving logic here
            elif user_input == 'n':
                space_below("Save Cancelled")
            else:
                print("Invalid input. Please type 'y' to save or 'n' to cancel.")

        except pyperclip.PyperclipException as e:
            Settings.show_error("Error accessing clipboard:", str(e))
