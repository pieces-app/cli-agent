from . import commands_functions
import pyperclip
from collections.abc import Iterable
from pieces.api.assets import (get_assets_info_list,get_asset_by_id,
                               delete_asset_by_id,update_asset,
                               edit_asset_name,create_new_asset,get_asset_ids,reclassify_asset)
from pieces.gui import show_error,print_model_details,space_below,double_line
from pieces.api.config import open_snippet_dir
import os

def list_command(**kwargs):
    type = kwargs.get("type","assets")
    max_assets = kwargs.get("max_assets",10)
    if max_assets < 1:
        print("Max assets must be greater than 0")
        max_assets = 10
    
    if type == "assets":
        list_assets(max_assets)
    elif type == "apps":
        list_apps()
    elif type == "models":
        list_models()

def list_models():
    for idx,model_name in enumerate(commands_functions.models,start=1):
        print(f"{idx}: {model_name}")
    print(f"Currently using: {commands_functions.get_current_model_name()} with uuid {commands_functions.model_id}")


def list_apps():
    # Get the list of applications
    application_list = commands_functions.list_applications()

    # Check if the application_list object has an iterable attribute and if it is an instance of Iterable
    if hasattr(application_list, 'iterable') and isinstance(application_list.iterable, Iterable):
        # Iterate over the applications in the list
        for i, app in enumerate(application_list.iterable, start=1):
            # Get the name of the application, default to 'Unknown' if not available
            app_name = getattr(app, 'name', 'Unknown').value if hasattr(app, 'name') and hasattr(app.name, 'value') else 'Unknown'
            # Get the version of the application, default to 'Unknown' if not available
            app_version = getattr(app, 'version', 'Unknown')
            # Get the platform of the application, default to 'Unknown' if not available
            app_platform = getattr(app, 'platform', 'Unknown').value if hasattr(app, 'platform') and hasattr(app.platform, 'value') else 'Unknown'
                
            # Print the application details
            print(f"{i}: {app_name}, {app_version}, {app_platform}")
    else:
        # Print an error message if the 'Applications' object does not contain an iterable list of applications
        print("Error: The 'Applications' object does not contain an iterable list of applications.")


def list_assets(max_assets:int=10):

    asset_list = get_assets_info_list()
    
    for i, name in enumerate(asset_list, start=1):
        print(f"{i}: {name.get("name")}")
        if i >= max_assets:
            break


def open_asset(**kwargs):
    item_index = kwargs.get('ITEM_INDEX',1)
    if not item_index: item_index = 1

    asset_ids = get_assets_info_list()
    try:
        asset_id = asset_ids[item_index-1].get('id') # because we begin from 1
    except IndexError:
        show_error("Invalid asset index or asset not found.","Please choose from the list or use 'pieces list assets'")
        return
    
    commands_functions.current_asset = asset_id  
    open_asset = get_asset_by_id(asset_id)
    asset_dict = extract_asset_info(open_asset)
    

    filepath = commands_functions.extract_code_from_markdown(asset_dict["raw"], asset_dict["name"], asset_dict["language"])

    print_model_details(asset_dict["name"],asset_dict["created_at"],asset_dict["updated_at"],asset_dict["type"],asset_dict["language"],filepath)

def save_asset(**kwargs):
    asset = extract_asset_info(get_asset_by_id(commands_functions.current_asset))
    file_path = os.path.join(open_snippet_dir , f"{commands_functions.sanitize_filename(asset["name"])}{commands_functions.get_file_extension(asset["language"])}")
    print(f"Saving {file_path} to {asset['name']}")
    
    # Pass asset and file name
    update_asset(file_path, commands_functions.current_asset)

# Probably needs renamed. This only currently edits the Asset's name
def edit_asset(**kwargs):
    asset_dict = extract_asset_info(get_asset_by_id(commands_functions.current_asset))
    print_model_details(asset_dict["name"],asset_dict["created_at"],asset_dict["updated_at"],asset_dict["type"],asset_dict["language"])
    
    name = kwargs.get('name', '')
    classification = kwargs.get('classification', '')

    if not name and not classification: # If no name or no classification is provided
        # Ask the user for a new name
        name = input("Enter the new name for the asset[leave blank to keep the same]: ").strip()
        classification = input("Enter the classification for the asset[leave blank to keep the same]: ").strip()

    # Check if the user actually entered a name
    if name:
        edit_asset_name(commands_functions.current_asset, name)
    if classification:
        reclassify_asset(commands_functions.current_asset, classification)

def delete_asset(**kwargs):
    # Ask the user for confirmation before deleting
    # print()
    # open_asset()
    asset_dict = extract_asset_info(get_asset_by_id(commands_functions.current_asset))
    print_model_details(asset_dict["name"],asset_dict["created_at"],asset_dict["updated_at"],asset_dict["type"],asset_dict["language"])

    confirm = input("Are you sure you really want to delete this asset? This action cannot be undone. (y/n): ").strip().lower()
    if confirm == 'y':
        print("Deleting asset...")
        delete_asset_by_id(commands_functions.current_asset)
        commands_functions.current_asset = get_asset_ids()[0]
        space_below("Asset Deleted")
    elif confirm == 'n':
        print("Deletion cancelled.")
    else:
        print("Invalid input. Please type 'y' to confirm or 'n' to cancel.")
    
def create_asset(**kwargs):
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
            new_asset = create_new_asset(commands_functions.application, raw_string=text, metadata=None)
    
            commands_functions.current_asset = new_asset.id
            print(f"Asset Created use 'open' to view")

            return new_asset
            # Add your saving logic here
        elif user_input == 'n':
            space_below("Save Cancelled")
        else:
            print("Invalid input. Please type 'y' to save or 'n' to cancel.")

    except pyperclip.PyperclipException as e:
        show_error("Error accessing clipboard:", str(e))




def extract_asset_info(data:dict) -> dict:
    """
    Return some info about the asset
    :param data: The data containing information about the asset
    :return: A dictionary containing the asset's name, date created, date updated, type, language, and raw code snippet
    """

    name = data.get('name', 'Unknown')
    created_readable = data.get('created', {}).get('readable', 'Unknown')
    updated_readable = data.get('updated', {}).get('readable', 'Unknown')
    type = "No Type"
    language = "No Language"
    raw = None  # Initialize raw code snippet as None
    formats = data.get('formats', {})

    if formats:
        iterable = formats.get('iterable', [])
        if iterable:
            first_item = iterable[0] if len(iterable) > 0 else None
            if first_item:
                classification_str = first_item.get('classification', {}).get('generic')
                if classification_str:
                    # Extract the last part after the dot
                    type = classification_str.split('.')[-1]

                language_str = first_item.get('classification', {}).get('specific')
                if language_str:
                    # Extract the last part after the dot
                    language = language_str.split('.')[-1]

                fragment_string = first_item.get('fragment', {}).get('string').get('raw')
                if fragment_string:
                    raw = fragment_string

    return {"name":name,
             "created_at":created_readable,
             'updated_at': updated_readable,
             "type" :type,
             "language": language,
             "raw": raw}
             