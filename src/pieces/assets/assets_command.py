import os
import pyperclip

from pieces.utils import get_file_extension,sanitize_filename,export_code_to_file
from .assets_api import AssetsCommandsApi
from pieces.gui import show_error,print_model_details,space_below,double_line,deprecated
from pieces.settings import Settings
import subprocess
from prompt_toolkit import PromptSession
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import TerminalFormatter
import json
import tempfile

#Ensure the data_path directory exists
os.makedirs(Settings.pieces_data_dir, exist_ok=True)
CONFIG_FILE = os.path.join(Settings.pieces_data_dir, "pieces_config.json")

def check_assets_existence(func):
	"""Decorator to ensure user has assets."""
	def wrapper(*args, **kwargs):
		assets = AssetsCommandsApi().assets_snapshot # Check if there is an asset
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
			asset_data = AssetsCommandsApi.get_asset_snapshot(AssetsCommands.current_asset)
		except:
			# The selected asset is deleted
			return show_error("Error occured in the command", "Please make sure the selected asset is valid.")
		return func(asset_data=asset_data,*args, **kwargs)	
			
	return wrapper

class AssetsCommands:
	current_asset = None

	@classmethod
	def load_config(cls):
	    if os.path.exists(CONFIG_FILE):
		try:
		with open(CONFIG_FILE, 'r') as f:
			content = f.read().strip()
			if content:
			return json.loads(content)
			else:
			print("Config file is empty. Creating a new configuration.")
			return {}
		except json.JSONDecodeError:
		print("Invalid JSON in config file. Creating a new configuration.")
		return {}
	    else:
		print("Config file does not exist. Creating a new configuration.")
		return {}

	@classmethod
	def save_config(cls, config):
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f)

	@classmethod
	def config(cls, **kwargs):
            config = cls.load_config()
            if 'editor' in kwargs:
                config['editor'] = kwargs['editor']
                cls.save_config(config)
                print(f"Editor set to: {kwargs['editor']}")
            else:
                print("Current configuration:")
                print(f"Editor: {config.get('editor', 'Not set')}")

	@classmethod
        @check_assets_existence
	@deprecated("open","list assets")
        def open_asset(cls, item_index=1, open_in_editor=False, **kwargs):
            asset_ids = AssetsCommandsApi().assets_snapshot
            try:
                cls.current_asset = list(asset_ids.keys())[item_index-1]  # because we begin from 1
            except IndexError:
                return show_error("Invalid asset index or asset not found.", "Please choose from the list or use 'pieces list assets'")
        
            asset_dict = AssetsCommandsApi.extract_asset_info(AssetsCommandsApi.get_asset_snapshot(cls.current_asset))
        
            print_model_details(asset_dict["name"], asset_dict["created_at"], asset_dict["updated_at"], asset_dict["type"], asset_dict["language"])
        
            code_content = asset_dict["raw"]

            if not open_in_editor:
                # Determine the lexer
                try:
                    lexer = get_lexer_by_name(asset_dict["language"], stripall=True)
                except:
                    lexer = guess_lexer(code_content)

                # Print the code with syntax highlighting
                formatted_code = highlight(code_content, lexer, TerminalFormatter())
                print("\nCode content:")
                print(formatted_code)

            # Check if -e flag is used or open_in_editor is True
            if kwargs.get('e') or open_in_editor:
                config = cls.load_config()
                editor = config.get('editor')
                if editor:
                    # Save the code to a temporary file
                    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f".{asset_dict['language']}") as temp_file:
                        temp_file.write(code_content)
                        temp_file_path = temp_file.name

                    # Open the file with the configured editor
                    subprocess.run([editor, temp_file_path])

                    # Update the asset with the new content
                    AssetsCommandsApi.update_asset_value(temp_file_path, cls.current_asset)
                    print("Asset updated successfully.")

                    # Clean up the temporary file
                    os.unlink(temp_file_path)
                else:
                    print("No editor configured. Use 'pieces config editor <editor_command>' to set an editor.")

	@classmethod
        def open_in_editor(cls, code_content, language):
            config = cls.load_config()
            editor = config.get('editor')
            if not editor:
                return print("No editor configured. Use 'pieces config editor <editor_command>' to set an editor.")
        
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f".{language}") as temp_file:
                temp_file.write(code_content)
                temp_file_path = temp_file.name

            try:
                subprocess.run([editor, temp_file_path], check=True)
                print(f"Opened in {editor}")
            except subprocess.CalledProcessError:
                print(f"Failed to open editor {editor}. Please check your configuration.")
            finally:
                os.unlink(temp_file_path)
		

	@classmethod
	@check_asset_selected
	def update_asset(cls,asset_data,**kwargs):
		asset = AssetsCommandsApi.extract_asset_info(asset_data)
		file_path = os.path.join(Settings.open_snippet_dir , f"{sanitize_filename(asset['name'])}{get_file_extension(asset['language'])}")
		print(f"Saving {file_path} to {asset['name']} snippet with uuid {cls.current_asset}")

		
		# Pass asset and file name
		AssetsCommandsApi.update_asset_value(file_path, cls.current_asset)


	@classmethod
	@check_asset_selected
	def edit_asset(cls,asset_data,**kwargs):
		asset_dict = AssetsCommandsApi.extract_asset_info(asset_data)
		print_model_details(asset_dict["name"],asset_dict["created_at"],asset_dict["updated_at"],asset_dict["type"],asset_dict["language"])
		
		name = kwargs.get('name', '')
		classification = kwargs.get('classification', '')

		if not name and not classification: # If no name or no classification is provided
			# Ask the user for a new name
			name = input("Enter the new name for the asset[leave blank to keep the same]: ").strip()
			classification = input("Enter the classification for the asset[leave blank to keep the same]: ").strip()

		# Check if the user actually entered a name
		if name:
			AssetsCommandsApi.edit_asset_name(cls.current_asset, name)
		if classification:
			AssetsCommandsApi.reclassify_asset(cls.current_asset, classification)

	@classmethod
	@check_asset_selected
	def delete_asset(cls,asset_data,**kwargs):
		# Ask the user for confirmation before deleting
		# print()
		# open_asset()
		asset_dict = AssetsCommandsApi.extract_asset_info(asset_data)
		print_model_details(asset_dict["name"],asset_dict["created_at"],asset_dict["updated_at"],asset_dict["type"],asset_dict["language"])

		confirm = input("Are you sure you really want to delete this asset? This action cannot be undone. (y/n): ").strip().lower()
		if confirm == 'y':
			print("Deleting asset...")
			AssetsCommandsApi.delete_asset_by_id(cls.current_asset)
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
				new_asset = AssetsCommandsApi.create_new_asset(raw_string=text, metadata=None)
		
				cls.current_asset = new_asset.id
				print("Asset Created use 'open' to view")

				return new_asset
				# Add your saving logic here
			elif user_input == 'n':
				space_below("Save Cancelled")
			else:
				print("Invalid input. Please type 'y' to save or 'n' to cancel.")

		except pyperclip.PyperclipException as e:
			show_error("Error accessing clipboard:", str(e))





