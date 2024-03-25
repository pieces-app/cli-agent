## MAIN FUNCTIONS | Line ~33
## HELPER FUNCTIONS | Line ~381

from pieces.gui import *
import json
from bs4 import BeautifulSoup
import os
import re
import pyperclip
from collections.abc import Iterable
from pieces.api.pieces_websocket import WebSocketManager
from pieces.api.api_functions import *
from pieces.api.system import *
from pieces.api.assets import *
from pieces.api.config import *
import pickle
from pieces import __version__

# Globals for CLI Memory.
ws_manager = WebSocketManager()
assets_are_models = False
current_asset = {}
parser = None
application = None
###############################################################################
############################## MAIN FUNCTIONS #################################
###############################################################################

def startup(): # startup function to run before the cli begin
    global models,model_id,word_limit,application,pieces_os_version
    pieces_os_version = open_pieces_os()
    if pieces_os_version:

        # Call the connect api
        application = connect_api()

        # MODELS
        models = get_models_ids()
        create_file = True
        # Check if the models file exists
        if models_file.is_file():
            with open(models_file, 'rb') as f:
                model_data = pickle.load(f)
            model_id = model_data["model_id"]
            word_limit = model_data["word_limit"]
            try: # Checks if the current model is valid
                get_current_model_name()
                create_file = False
            except:
                pass
            
        if create_file:
            default_model_name = "GPT-3.5-turbo Chat Model"
            model_id = models[default_model_name]["uuid"] # default model id
            word_limit = models[default_model_name]["word_limit"] # The word limit of the default model
            dump_pickle(file = models_file, model_id=model_id, word_limit=word_limit)
            
    else:
        server_startup_failed()
        

def ask(query, **kwargs):
    global model_id, ws_manager
    try:
        ws_manager.ask_question(model_id, query)
    except Exception as e:
        show_error("Error occurred while asking the question:", e)

def search(query, **kwargs):
    global asset_ids 

    search_type = kwargs.get('search_type', 'assets')

    # Join the list of strings into a single search phrase
    search_phrase = ' '.join(query)

    # Call the API function with the search phrase and type
    results = search_api(search_phrase, search_type)

    # Check and extract asset IDs from the results
    if results:
        # Extract the iterable which contains the search results
        iterable_list = results.iterable if hasattr(results, 'iterable') else []

        # Check if iterable_list is a list and contains SearchedAsset objects
        if isinstance(iterable_list, list) and all(hasattr(asset, 'exact') and hasattr(asset, 'identifier') for asset in iterable_list):
            # Extracting suggested and exact IDs
            suggested_ids = [asset.identifier for asset in iterable_list if not asset.exact]
            exact_ids = [asset.identifier for asset in iterable_list if asset.exact]

            # Combine and store best and suggested matches in asset_ids
            combined_ids = exact_ids + suggested_ids
            asset_ids = {index + 1: asset_id for index, asset_id in enumerate(combined_ids)}

            # Prepare the combined list of names for printing
            combined_details = [(asset_id, get_asset_name_by_id(asset_id)) for asset_id in combined_ids]

            # Print the combined asset details
            if combined_details:
                print_asset_details(combined_details, "Asset Matches:", search_type)
            else:
                print("No matches found.")
        else:
            print("Unexpected response format or empty iterable.")
    else:
        print("No results found.")



def list_models(**kwargs):
    for idx,model_name in enumerate(models,start=1):
        print(f"{idx}: {model_name}")
    print(f"Currently using: {get_current_model_name()} with uuid {model_id}")


def list_apps(**kwargs):
    # Get the list of applications
    application_list = list_applications()

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


def list_assets(max_assets:int=10, **kwargs):

    asset_list = get_asset_info_list()
    
    for i, name in enumerate(asset_list, start=1):
        print(f"{i}: {name.get("name")}")
        if i >= max_assets:
            break

def change_model(**kwargs): # Change the model used in the ask command
    global model_id,word_limit
    model_index = kwargs.get('MODEL_INDEX')
    try:
        if model_index:
            model_name = list(models.keys())[model_index-1] # because we begin from 1
            word_limit = models[model_name].get("word_limit")
            model_id  = models[model_name].get("uuid")
            dump_pickle(file = models_file,model_id = model_id,word_limit = word_limit)
            print(f"Switched to {model_name} with uuid {model_id}")
        else:
            raise Exception("Invalid model index or model index not provided.")
    except:
        print("Invalid model index or model index not provided.")
        print("Please choose from the list or use 'pieces list models'")
        



def open_asset(**kwargs):
    global current_asset

    item_index = kwargs.get('ITEM_INDEX')

    asset_ids = get_asset_info_list()

    if item_index is not None:
        try:
            asset_id = asset_ids[item_index-1].get('id') # because we begin from 1
        except IndexError:
            show_error("Invalid asset index or asset not found.","Please choose from the list or use 'pieces list_assets'")
            return
    else:
        asset_id = asset_ids[0].get('id')
    opened_asset = get_asset_by_id(asset_id)    
    current_asset = {asset_id}
    name = opened_asset.get('name', 'Unknown')
    created_readable = opened_asset.get('created', {}).get('readable', 'Unknown')
    updated_readable = opened_asset.get('updated', {}).get('readable', 'Unknown')
    type = "No Type"
    language = "No Language"
    code_snippet = "No Code Available"
    formats = opened_asset.get('formats', {})

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
                    code_snippet = extract_code_from_markdown(raw, name, language)

    # Printing the asset details
    print_model_details(name, created_readable, updated_readable, type, language, code_snippet)

def save_asset(**kwargs):
    ### THIS DOES NOT CURRENTLY WORK ###
    global application
    global current_asset
    print("Not Currently Working")

    if not current_asset:
        open_asset()
    else:
        asset_to_update = current_asset.get('id')
        # Pass asset and file name
        update_asset(asset_to_update, application)

# Probably needs renamed. This only currently edits the Asset's name
def edit_asset(**kwargs):
    global application
    global current_asset

    if not current_asset:
        open_asset()
        asset_to_update = current_asset.get('id')

        # Ask the user for a new name
        new_name = input("Enter the new name for the asset: ")

        # Check if the user actually entered a name
        if new_name.strip():
            # Pass asset and new name to the edit_asset_name function
            edit_asset_name(asset_to_update, new_name)
        else:
            print("No new name provided. Asset name not updated.")
    else:
        asset_to_update = current_asset.get('id')
        if asset_to_update is None:
            print("No asset to update.")
            return

        # Ask the user for a new name
        new_name = input("Enter the new name for the asset: ")

        # Check if the user actually entered a name
        if new_name.strip():
            # Pass asset and new name to the edit_asset_name function
            edit_asset_name(asset_to_update, new_name)
        else:
            print("No new name provided. Asset name not updated.")

def delete_asset(**kwargs):
    global application
    global current_asset

    if not current_asset:
        # Open the most recent asset
        if run_in_loop:
            open_asset()
            delete_most_recent()
        else:
            print()
            asset_to_delete = list_assets(max_results=1)
            open_asset()
            print()
            confirm = input("This is your most recent asset. Are you sure you want to delete it? This action cannot be undone. (y/n): ").strip().lower()
            if confirm == 'y':
                print("Deleting asset...")
                # print(asset_to_delete)
                delete_result = delete_asset_by_id(asset_to_delete)
                print(delete_result)
                current_asset = None
                space_below("Asset Deleted")
                list_assets()
            elif confirm == 'n':
                space_below("Deletion cancelled")
            else:
                space_below("Invalid input. Please type 'y' to confirm or 'n' to cancel.")
    else:
        asset_to_delete = list(current_asset)[0]

        # Ask the user for confirmation before deleting
        # print()
        # open_asset()
        confirm = input("Are you sure you really want to delete this asset? This action cannot be undone. (y/n): ").strip().lower()
        if confirm == 'y':
            print("Deleting asset...")
            delete_asset_by_id(asset_to_delete)
            current_asset = None
            space_below("Asset Deleted")
            list_assets()
        elif confirm == 'n':
            print("Deletion cancelled.")
        else:
            print("Invalid input. Please type 'y' to confirm or 'n' to cancel.")
    
def create_asset(**kwargs):
    global application
    global current_asset
    
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
            new_asset = create_new_asset(application, raw_string=text, metadata=None)
    
            current_asset = {new_asset.id}
            # print(current_asset)
            print(f"Asset Created use 'open' to view")

            return new_asset
            # Add your saving logic here
        elif user_input == 'n':
            space_below("Save Cancelled")
        else:
            print("Invalid input. Please type 'y' to save or 'n' to cancel.")

    except pyperclip.PyperclipException as e:
        show_error("Error accessing clipboard:", str(e))



###############################################################################
############################## HELPER FUNCTIONS ###############################
###############################################################################
def dump_pickle(file,**data):
    """Store data in a pickle file."""
    with open(file, 'wb') as f:
        pickle.dump(data, f)


def get_current_model_name() -> str:
    with open(models_file, 'rb') as f:
        model_data = pickle.load(f)
    model_id = model_data["model_id"]
    models_reverse = {v.get("uuid"):k for k,v in models.items()}
    return models_reverse[model_id]


def get_asset_name_by_id(asset_id):
    asset = get_asset_by_id(asset_id)  # Assuming this function returns the asset details
    return asset.get('name') if asset else "Unknown"

def set_parser(p):
    global parser
    parser = p


# Used to create a valid file name when opening to "Opened Snippets"
def sanitize_filename(name):
    """ Sanitize the filename by removing or replacing invalid characters. """
    # Replace spaces with underscores
    name = name.replace(" ", "_")
    # Remove invalid characters
    name = re.sub(r'[\\/*?:"<>|]', '', name)
    return name

def extract_code_from_markdown(markdown, name, language):
    # Sanitize the name to ensure it's a valid filename
    filename = sanitize_filename(name)
    file_extension = get_file_extension(language)

    # Using BeautifulSoup to parse the HTML and extract text
    soup = BeautifulSoup(markdown, 'html.parser')
    extracted_code = soup.get_text()

    # Minimize multiple consecutive newlines to a single newline
    extracted_code = re.sub(r'\n\s*\n', '\n', extracted_code)

    directory = os.path.join(os.getcwd(),'opened_snippets')  # Change the dir to the same dir that the user writing the command in

    # Ensure the directory exists, create it if not
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Path to save the extracted code
    file_path = os.path.join(directory, f'{filename}{file_extension}')

    # Writing the extracted code to a new file
    with open(file_path, 'w') as file:
        file.write(extracted_code)

    return file_path

def get_file_extension(language):
    with open(f'{BASE_DIR}/commands/extensions.json') as f:
        extension_mapping = json.load(f)

    # Lowercase the language for case-insensitive matching
    language = language.lower()

    # Return the corresponding file extension or default to '.txt' if not found
    return extension_mapping.get(language, '.txt')

def version(**kwargs):

    if pieces_os_version:
        print(f"Pieces Version: {pieces_os_version}")
        print(f"Cli Version: {__version__}")
    else:
        ### LOGIC TO look up cache from SQLite3 to get the cli and pieces os version

        # Get the version from cache
        # Establish a local database connection
        # conn = create_connection('applications.db')

        # # Create the table if it does not exist
        # create_table(conn)
        # # create_tables(conn)

        # # Check the database for an existing application
        # application_id = "DEFAULT"  # Replace with a default application ID
        # application = get_application(conn, application_id)
        # # application =  get_application_with_versions(conn, application_id)
        pass
