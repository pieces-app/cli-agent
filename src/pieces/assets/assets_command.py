import os
import pyperclip
import threading

from pieces.utils import get_file_extension,sanitize_filename,export_code_to_file
from .assets_api import AssetsCommandsApi
from pieces.gui import show_error,print_model_details,space_below,double_line
from pieces.settings import Settings


def check_assets_existence(func):
	"""Decorator to ensure user has assets."""
	def wrapper(*args, **kwargs):
		assets = AssetsCommandsApi.get_assets_snapshot() # Check if there is an asset
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
			return show_error("Error occured in the getting the asset data", "Please make sure the selected asset is valid.")
		return func(asset_data=asset_data,*args, **kwargs)
			
			
	return wrapper

class AssetsCommands:
	current_asset = None
	current_shareable_link_thread = None
	current_asset_shareable = None

	@classmethod
	@check_assets_existence
	def open_asset(cls,**kwargs):
		item_index = kwargs.get('ITEM_INDEX',1)
		if not item_index:
			item_index = 1
		asset_ids = AssetsCommandsApi.get_assets_snapshot()
		try:
			cls.current_asset = list(asset_ids.keys())[item_index-1] # because we begin from 1
		except IndexError:
			show_error("Invalid asset index or asset not found.","Please choose from the list or use 'pieces list assets'")
			return
		
		asset_dict = AssetsCommandsApi.extract_asset_info(AssetsCommandsApi.get_asset_snapshot(cls.current_asset))
		

		filepath = export_code_to_file(asset_dict["raw"], asset_dict["name"], asset_dict["language"])

		print_model_details(asset_dict["name"],asset_dict["created_at"],asset_dict["updated_at"],asset_dict["type"],asset_dict["language"],filepath)


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
				print(f"Asset Created use 'open' to view")

				return new_asset
				# Add your saving logic here
			elif user_input == 'n':
				space_below("Save Cancelled")
			else:
				print("Invalid input. Please type 'y' to save or 'n' to cancel.")

		except pyperclip.PyperclipException as e:
			show_error("Error accessing clipboard:", str(e))
	
	@classmethod
	@check_asset_selected
	def share_asset(cls,asset_data,**kwargs):

		# Handle delete
		if kwargs.get("delete"):
			if not asset_data.shares:
				return print("That asset does not have a shareable link")
			
			print(asset_data.shares.iterable[0].link)
			if input("Are you sure you want to delete this shareable link? (y/n): ").strip().lower() == "y":
				print("Deleting")
				AssetsCommandsApi.delete_shareable_link(asset_data.shares.iterable[0].id)
				print("Shareable link deleted successfully.")
				asset_data.shares.iterable
				AssetsCommandsApi.assets_snapshot[asset_data.id] = asset_data.shares.iterable.pop(0) # Remove the asset shares from the cached assets
			return
		
		# Handle creatation
		if cls.current_shareable_link_thread:
			print("There is currently one that is generating. Please wait")
			return
		
		if asset_data.shares:
			print(f"Link: {asset_data.shares.iterable[0].link}")
			res = input("There is already a generated shareable link. Would you like to create another one (y/n): ").strip().lower()
			if res != "y":
				return

		print("Generating shareable link...")
		cls.current_shareable_link_thread = AssetsCommandsApi.generate_shareable_link(asset_data,async_req=True)
		cls.current_asset_shareable = asset_data
		print("This might take a while. You can continue using the cli until the link is generated")
		threading.Thread(target=cls.check_link).start()


	@classmethod
	def check_link(cls):
		session = Settings.prompt_session
		share = None
		for _ in range(3): # Try sharing three times
			try:
				share = cls.current_shareable_link_thread.get() # Wait for the link to be available
			except Exception as e:
				cls.current_shareable_link_thread = AssetsCommandsApi.generate_shareable_link(cls.current_asset_shareable,async_req=True)

		if not share:
			print("\nFailed to generate a shareable link")
			return
		print("\n")
		print(f"Generated shareable Link: {share.iterable[0].link}")

		cls.current_shareable_link_thread = None
		cls.current_asset_shareable = None
		
		res = session.prompt("Post this snippet along with the context metadata as a github gist? (y/n): ").strip().lower() 
		if res == "y":
			gist_name = session.prompt(f"Gist name [{cls.current_asset_shareable.name}]: ").strip()
			gist_name = gist_name if gist_name else cls.current_asset_shareable.name
			description = cls.current_asset_shareable.annotations.iterable[0].text
			gist_description = session.prompt(f"Gist description [{description}]: ").strip()
			gist_description = gist_description if gist_description else description
			gist_private = session.prompt("Do you want that gist to be private? (y/n): ").strip().lower()
			gist_private = True if gist_private != "n" else False
			dis = AssetsCommandsApi.create_gist(gist_name, gist_description, not gist_private)
			print(dis)

