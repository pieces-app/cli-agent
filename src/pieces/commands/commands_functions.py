## MAIN FUNCTIONS | Line ~33
## HELPER FUNCTIONS | Line ~381

from pieces.gui import *
import json
from bs4 import BeautifulSoup
import os
import re
from pieces.api.api_functions import *
from pieces.settings import Settings
from pieces import __version__
from pieces.commands.assets.assets_api import AssetsCommandsApi

###############################################################################
############################## MAIN FUNCTIONS #################################
###############################################################################





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



def change_model(**kwargs): # Change the model used in the ask command
    model_index = kwargs.get('MODEL_INDEX')
    try:
        if model_index:
            model_name = list(Settings.models.keys())[model_index-1] # because we begin from 1
            model_id  = Settings.models[model_name].get("uuid")
            Settings.dump_pickle(file = Settings.models_file,model_id = model_id)
            print(f"Switched to {model_name} with uuid {model_id}")
        else:
            raise Exception("Invalid model index or model index not provided.")
    except:
        print("Invalid model index or model index not provided.")
        print("Please choose from the list or use 'pieces list models'")
        



###############################################################################
############################## HELPER FUNCTIONS ###############################
###############################################################################


def get_asset_name_by_id(asset_id):
    asset = AssetsCommandsApi.get_asset_by_id(asset_id)  
    return asset.get('name') if asset else "Unknown"


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

    # Ensure the directory exists, create it if not
    if not os.path.exists(Settings.open_snippet_dir):
        os.makedirs(Settings.open_snippet_dir)

    # Path to save the extracted code
    file_path = os.path.join(Settings.open_snippet_dir, f'{filename}{file_extension}')

    # Writing the extracted code to a new file
    with open(file_path, 'w') as file:
        file.write(extracted_code)

    return file_path

def get_file_extension(language):
    with open(Settings.extensions_dir) as f:
        extension_mapping = json.load(f)

    # Lowercase the language for case-insensitive matching
    language = language.lower()

    # Return the corresponding file extension or default to '.txt' if not found
    return extension_mapping.get(language, '.txt')

def version(**kwargs):
    if Settings.pieces_os_version:
        print(f"Pieces Version: {Settings.pieces_os_version}")
        print(f"Cli Version: {__version__}")
    else:
        pass
