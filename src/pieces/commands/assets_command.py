import os
from typing import Optional
import pyperclip
import subprocess

from pieces.utils import get_file_extension,sanitize_filename,export_code_to_file
from pieces.gui import show_error,print_asset_details,space_below,double_line,deprecated
from pieces.settings import Settings
from pieces.commands.config_command import ConfigCommands
from pieces.wrapper.basic_identifier.asset import BasicAsset

from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import TerminalFormatter


def check_assets_existence(func):
	"""Decorator to ensure user has assets."""
	def wrapper(*args, **kwargs):
		assets = Settings.pieces_client.assets # Check if there is an asset
		if not assets:
			return show_error("No assets found", "Please create an asset first.")
		return func(*args, **kwargs)
	return wrapper


def check_asset_selected(func):
	"""
	Decorator to check if there is a selected asset or not and if it is valid id.
	If valid id it returns the asset_data to the called function.
	"""
	def wrapper(*args, **kwargs):
		if AssetsCommands.current_asset is None:
			return show_error("No asset selected.", "Please open an asset first using pieces open.")
		try: 
			AssetsCommands.current_asset.asset # Check if the current asset is vaild
		except:
			# The selected asset is deleted
			return show_error("Error occured in the command", "Please make sure the selected asset is valid.")
		return func(asset=AssetsCommands.current_asset,*args, **kwargs)	
	return wrapper

class AssetsCommands:
	current_asset:Optional[BasicAsset] = None

	@classmethod
	@check_assets_existence
	@deprecated("open","list assets")
	def open_asset(cls, **kwargs):
		item_index = kwargs.get("ITEM_INDEX",1)
		assets = Settings.pieces_client.assets()
		try:
			asset:BasicAsset = assets[item_index-1]  # because we begin from 1
			cls.current_asset = asset
		except IndexError:
			return show_error("Invalid asset index or asset not found.", "Please choose from the list or use 'pieces list assets'")
	
		print_asset_details(asset)

		code_content = asset.raw_content
		open_in_editor = kwargs.get('editor')
			
		# Check if -e flag is used or open_in_editor is True
		if open_in_editor:
			config = ConfigCommands.load_config()
			editor = config.get('editor')
			if editor:
				# Save the code to a file in the default directory
				file_path = export_code_to_file(code_content, asset.name, asset.classification)

				# Open the file with the configured editor
				try:
					subprocess.run([editor, file_path], shell=True)
				except Exception as e:
					show_error("Error in opening",e)

			else:
				print("No editor configured. Use 'pieces config editor <editor_command>' to set an editor.")
		else:
			# Determine the lexer
			try:
				lexer = get_lexer_by_name(asset.classification, stripall=True)
			except:
				lexer = guess_lexer(code_content)

			# Print the code with syntax highlighting
			formatted_code = highlight(code_content, lexer, TerminalFormatter())
			print("\nCode content:")
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
			show_error("Error in update asset","File not found")
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
		try:
			text = pyperclip.paste()
			double_line("Content to save: ")
			space_below(text)

			# Ask the user for confirmation to save
			user_input = input("Do you want to save this content? (y/n): ").strip().lower()
			if user_input == 'y':
				space_below("Saving Content...")
				cls.current_asset = BasicAsset(BasicAsset.create(raw_content=text, metadata=None))
				print("Asset Created use 'open' to view")
				# Add your saving logic here
			elif user_input == 'n':
				space_below("Save Cancelled")
			else:
				print("Invalid input. Please type 'y' to save or 'n' to cancel.")

		except pyperclip.PyperclipException as e:
			show_error("Error accessing clipboard:", str(e))





