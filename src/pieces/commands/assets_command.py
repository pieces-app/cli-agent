import os
from typing import Optional
import pyperclip
import subprocess

from pieces.utils import get_file_extension,sanitize_filename,export_code_to_file
from pieces.gui import print_asset_details,space_below,double_line
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
		assets = Settings.pieces_client.assets # Check if there is an asset
		if not assets:
			return Settings.show_error("No assets found", "Please create an asset first.")
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
				raise ValueError("No asset selected")
			AssetsCommands.current_asset.asset # Check if the current asset is vaild
		except (ValueError, NotFoundException):
			ListCommand.list_assets()
		return func(asset=AssetsCommands.current_asset,*args, **kwargs)	
	return wrapper

class AssetsCommands:
	current_asset:Optional[BasicAsset] = None

	@classmethod
	@check_assets_existence
	def open_asset(cls, asset_id:str, **kwargs):
		try:
			cls.current_asset = BasicAsset(asset_id)

		except IndexError:
			return Settings.show_error("Invalid asset index or asset not found.", "Please choose from the list or use 'pieces list assets'")
	
		print_asset_details(cls.current_asset)

		code_content = cls.current_asset.raw_content
		open_in_editor = kwargs.get('editor')
			
		# Check if -e flag is used or open_in_editor is True
		if open_in_editor:
			config = ConfigCommands.load_config()
			editor = config.get('editor')
			if editor:
				# Save the code to a file in the default directory
				file_path = export_code_to_file(code_content, cls.current_asset.name, cls.current_asset.classification)

				# Open the file with the configured editor
				try:
					subprocess.run([editor, file_path], shell=True)
				except Exception as e:
					Settings.show_error("Error in opening",e)

			else:
				print("No editor configured. Use 'pieces config editor <editor_command>' to set an editor.")
		else:
			# Determine the lexer
			print("\nCode content:")
			cls.print_code(cls.current_asset.raw_content, cls.current_asset.classification)

	@staticmethod
	def print_code(code_content, classification = None):
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
	def update_asset(cls,asset:BasicAsset,**kwargs):
		file_path = os.path.join(Settings.open_snippet_dir , f"{sanitize_filename(asset.name)}{get_file_extension(asset.classification)}")
		print(f"Saving {file_path} to {asset.name} snippet")
		
		try:
			with open(file_path,"r") as f:
				data = f.read()
		except FileNotFoundError:
			Settings.show_error("Error in update asset","File not found")
			return

		asset.raw_content = data



	@classmethod
	@check_asset_selected
	def edit_asset(cls,asset:BasicAsset,**kwargs):
		print_asset_details(asset)
		name = kwargs.get('name', '')
		classification = kwargs.get('classification', '')

		if not name and not classification: # If no name or no classification is provided
			# Ask the user for a new name
			name = input("Enter the new name for the asset[leave blank to keep the same]: ").strip()
			classification = input("Enter the classification for the asset[leave blank to keep the same]: ").strip()

		# Check if the user actually entered a name
		if name:
			asset.name = name
		if classification:
			asset.classification = classification

	@classmethod
	@check_asset_selected
	def delete_asset(cls,asset:BasicAsset,**kwargs):
		print_asset_details(asset)

		confirm = input("Are you sure you really want to delete this asset? This action cannot be undone. (y/n): ").strip().lower()
		if confirm == 'y':
			print("Deleting asset...")
			asset.delete()
			cls.current_asset = None
			space_below("Asset Deleted")
		elif confirm == 'n':
			print("Deletion cancelled.")
		else:
			print("Invalid input. Please type 'y' to confirm or 'n' to cancel.")
		
	@classmethod
	def create_asset(cls,**kwargs):
		# TODO add more ways to create an asset such as an entire file

		# Save text copied to the clipboard as an asset
		console = Console()
		try:
			text = pyperclip.paste()
			double_line("Content to save: ")

			cls.print_code(text)

			# Ask the user for confirmation to save
			user_input = input("Do you want to save this content? (y/n): ").strip().lower()
			if user_input == 'y':
				console.print("Saving...\n")
				cls.current_asset = BasicAsset(BasicAsset.create(raw_content=text, metadata=None))
				
				console.print(Markdown("Snippet successfully saved. Use `pieces list` to view."))
				# Add your saving logic here
			elif user_input == 'n':
				space_below("Save Cancelled")
			else:
				print("Invalid input. Please type 'y' to save or 'n' to cancel.")

		except pyperclip.PyperclipException as e:
			Settings.show_error("Error accessing clipboard:", str(e))

