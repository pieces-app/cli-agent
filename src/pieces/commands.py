## MAIN FUNCTIONS | Line ~33
## HELPER FUNCTIONS | Line ~381
## MAIN CLI FUNCTION | Line ~556

from pieces.gui import *
from pieces.api import *
import platform
import sys
import shlex
from bs4 import BeautifulSoup
import os
import re
import pyperclip
from collections.abc import Iterable

# Globals for CLI Memory.
ws_manager = WebSocketManager()

pieces_os_version = None
run_in_loop = False # is CLI looping?
asset_ids = {} # Asset ids for any list or search
assets_are_models = False
current_model = {'ac61838c-4676-4cae-98aa-037e4d3ad27c'} # GPT 3.5
current_asset = {}
parser = None
application = None
ws = None # Websocket connection to pass to api.py when running
ws_thread = None # Websocket thread to pass to api.py when running
cli_version = None

###############################################################################
############################## MAIN FUNCTIONS #################################
###############################################################################

def ask(query, **kwargs):
    global current_model, ws_manager, run_in_loop

    if current_model:
        model_id = next(iter(current_model))
    else:
        raise ValueError("No model ID available")

    try:
        ws, ws_thread = ws_manager.ask_question(model_id, query, run_in_loop)
    except Exception as e:
        print(f"Error occurred while asking the question: {e}")

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

def list_assets(list_type_or_max='assets', **kwargs):
    max_results = None
    list_apps = False
    global assets_are_models

    # Check if the argument is a digit (for max_results value) or 'apps'
    if list_type_or_max.isdigit():
        max_results = int(list_type_or_max)
    elif list_type_or_max == 'apps':
        list_apps = True

    if list_type_or_max == 'models':
        return list_all_models(**kwargs)  # Call the function to list all models

    if list_apps:
        # Logic for listing applications
        double_space("Listing applications...")
        application_list = list_applications()

        if hasattr(application_list, 'iterable') and isinstance(application_list.iterable, Iterable):
            for i, app in enumerate(application_list.iterable, start=1):
                app_name = getattr(app, 'name', 'Unknown').value if hasattr(app, 'name') and hasattr(app.name, 'value') else 'Unknown'
                app_version = getattr(app, 'version', 'Unknown')
                app_platform = getattr(app, 'platform', 'Unknown').value if hasattr(app, 'platform') and hasattr(app.platform, 'value') else 'Unknown'

                print(f"{i}: {app_name}, {app_version}, {app_platform}")
        else:
            print("Error: The 'Applications' object does not contain an iterable list of applications.")

        print()
        return  

    # Existing logic for listing assets
    global run_in_loop, asset_ids
    
    default_max_results = 10
    
    if max_results is None:
        max_results = default_max_results

    assets_are_models = False

    ids = get_asset_ids(max=max_results)
    names = get_asset_names(ids)
    
    for i, name in enumerate(names, start=1):
        print(f"{i}: {name}")
        if i >= max_results:
            break

    if run_in_loop:
        asset_ids = {i: id for i, id in enumerate(ids, start=1)}
        first_id = ids[0]
        return first_id
    else:
        first_id = ids[0]
        return first_id
    
def open_asset(**kwargs):
    global asset_ids
    global current_asset
    global assets_are_models

    item_index = kwargs.get('ITEM_INDEX')

    if assets_are_models:
        if item_index is not None and item_index in asset_ids:
            print(f"Model ID: {asset_ids[item_index]}")
        else:
            print("Invalid model index or model index not provided.")
        return
    
    opened_asset = None

    if item_index is not None:
        asset_id = asset_ids.get(item_index)        
        
        if asset_id:
            opened_asset = get_asset_by_id(asset_id)
        else:
            asset_id = list_assets(max_results=1)
            print()
            opened_asset = get_asset_by_id(asset_id)
            return
    else:
        asset_id = list_assets(max_results=1)
        print()
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
        print("Error accessing clipboard:", str(e))
    
def check():
    try:
        # Check if Pieces is Running
        is_running, message, application = check_api()
    except ValueError:
        # Handle the case where check_api() returns only 'False' for os_running
        server_startup_failed()
        return False
    else:
        if is_running:
            return is_running, message, application
        else:
            server_startup_failed()
    return is_running


###############################################################################
############################## HELPER FUNCTIONS ###############################
###############################################################################

def list_all_models(**kwargs):
    global asset_ids
    global assets_are_models

    try:
        response = list_models() 
    except Exception as e:
        print(f"Error occurred while fetching models: {e}")
        return

    # Check if response is valid and contains model data
    if hasattr(response, 'iterable') and response.iterable:
        print("\nModels")
        asset_ids = {}  # Reset asset_ids to store new model IDs
        for index, model in enumerate(response.iterable, start=1):
            model_name = getattr(model, 'name', 'Unknown')
            model_version = getattr(model, 'version', 'Unknown')
            model_id = getattr(model, 'id', 'Unknown')
            print(f"{index}: Model Name: {model_name}, Model Version: {model_version}")

            # Store model ID in asset_ids with the index as the key
            asset_ids[index] = model_id
        assets_are_models = True
    else:
        print("No models found or invalid response format.")

def get_asset_name_by_id(asset_id):
    asset = get_asset_by_id(asset_id)  # Assuming this function returns the asset details
    return asset.get('name') if asset else "Unknown"

def set_application(app):
    global application
    application = app

def set_parser(p):
    global parser
    parser = p

def help(**kwargs):
    print_help()
    pass

def set_pieces_os_version(version):
    global pieces_os_version
    pieces_os_version = version

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

    # Define the directory path relative to the current script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    directory = os.path.join(script_dir, 'opened_snippets')

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
    extension_mapping = {
        'csx': '.csx', 'cs': '.cs', 'html': '.html', 'htm': '.htm', 'shtml': '.shtml',
        'xhtml': '.xhtml', 'hs': '.hs', 'hs-boot': '.hs-boot', 'hsig': '.hsig',
        'cpp': '.cpp', 'cc': '.cc', 'cp': '.cpp', 'cxx': '.cpp', 'c': '.c',
        'h': '.h', 'hh': '.h', 'hpp': '.hpp', 'hxx': '.hxx', 'inl': '.inl',
        'ipp': '.ipp', 'ixx': '.ixx', 'cppm': '.cppm', 'csv': '.csv', 'doc': '.doc',
        'docm': '.docm', 'docx': '.docx', 'exe': '.exe', 'gif': '.gif', 'ico': '.ico',
        'jpe': '.jpg', 'jpeg': '.jpg', 'jpg': '.jpg', 'jpgm': '.jpgm', 'jpgv': '.jpgv',
        'log': '.log', 'mp2': '.mp2', 'mp2a': '.mp2a', 'mp3': '.mp3', 'mp4': '.mp4',
        'mp4a': '.mp4', 'oga': '.ogg', 'ogg': '.ogg', 'ogv': '.ogv', 'ogx': '.ogx',
        'ppt': '.ppt', 'pptx': '.pptx', 'pptm': '.pptm', 'qt': '.mov', 'text': '.txt',
        'tif': '.tif', 'tiff': '.tiff', 'txt': '.txt', 'wav': '.wav', 'weba': '.weba',
        'webm': '.webm', 'webp': '.webp', 'xla': '.xls', 'xlam': '.xlam', 'xlc': '.xlc',
        'xlm': '.xlm', 'xls': '.xls', 'xlsb': '.xlsb', 'xlsm': '.xlsm', 'xlsx': '.xlsx',
        'xlt': '.xlt', 'xltm': '.xltm', 'xltx': '.xltx', 'pdf': '.pdf', 'png': '.png',
        'rpm': '.rpm', 'zip': '.zip', 'woff': '.woff', 'woff2': '.woff2', 'svgz': '.svgz',
        'bin': '.bin', 'bmp': '.bmp', 'eot': '.eot', 'gz': '.gz', 'jar': '.jar',
        'mpkg': '.mpkg', 'ai': '.ai', 'eps': '.eps', 'dmg': '.dmg', 'list': '.txt',
        'rtx': '.rtx', 'uri': '.uri', 'uris': '.txt', 'urls': '.txt', 'css': '.css',
        'dart': '.dart', 'java': '.java', 'bsh': '.bsh', 'js': '.js', 'jsx': '.jsx',
        'mjs': '.mjs', 'htc': '.htc', 'json': '.json', 'ipynb': '.ipynb', 'gltf': '.gltf',
        'jsonml': '.jsonml', 'ps': '.ps', 'ssml': '.ssml', 'wasm': '.wasm', 'rtf': '.rtf',
        'cco': '.txt', 'pl': '.pl', 'pc': '.txt', 'pm': '.pm', 'pmc': '.txt',
        'pod': '.pod', 't': '.t', 'xml': '.xml', 'tld': '.txt', 'dtml': '.dtml',
        'rng': '.rng', 'rss': '.rss', 'opml': '.opml', 'svg': '.svg', 'xaml': '.xaml',
        'sublime-snippet': '.txt', 'tmLanguage': '.txt', 'tmPreferences': '.txt',
        'tmSnippet': '.txt', 'tmTheme': '.txt', 'csproj': '.csproj', 'fsproj': '.fsproj',
        'sqlproj': '.sqlproj', 'vbproj': '.vbproj', 'vcproj': '.vcproj', 'vcxproj': '.vcxproj',
        'dae': '.dae', 'props': '.props', 'targets': '.targets', 'xsd': '.xsd', 'xsl': '.xsl',
        'xslt': '.xslt', 'ecma': '.txt', 'node': '.txt', 'php': '.php', 'php3': '.php',
        'php4': '.php', 'php5': '.php', 'php7': '.php', 'php8': '.php', 'phps': '.php',
        'phpt': '.phpt', 'phtml': '.phtml', 'py': '.py', 'py3': '.py', 'pyw': '.pyw',
        'pyi': '.pyi', 'pyx': '.pyx', 'pyx.in': '.pyx', 'pxd': '.pxd', 'pxd.in': '.pxd',
        'pxi': '.pxi', 'pxi.in': '.pxi', 'rpy': '.rpy', 'cpy': '.cpy', 'gyp': '.gyp',
        'gypi': '.gypi', 'vpy': '.vpy', 'smk': '.smk', 'wscript': '.wscript', 'bazel': '.bazel',
        'bzl': '.bzl', 'pyc': '.pyc', 'class': '.class', 'p': '.p', 'pas': '.pas',
        'curl': '.curl', 'mcurl': '.txt', 'go': '.go', 'swift': '.swift', 'rs': '.rs',
        'ts': '.ts', 'tsx': '.tsx', 'rb': '.rb', 'rbi': '.rbi', 'rbx': '.rbx',
        'rjs': '.rjs', 'rabl': '.rabl', 'rake': '.rake', 'capfile': '.capfile', 'jbuilder': '.jbuilder',
        'gemspec': '.gemspec', 'podspec': '.podspec', 'irbrc': '.irbrc', 'pryrc': '.pryrc', 'prawn': '.prawn',
        'thor': '.thor', 'Appfile': '.txt', 'Appraisals': '.txt', 'Berksfile': '.txt', 'Brewfile': '.txt',
        'Cheffile': '.txt', 'Deliverfile': '.txt', 'Fastfile': '.txt', 'Gemfile': '.Gemfile', 'Guardfile': '.txt',
        'Podfile': '.Podfile', 'Rakefile': '.Rakefile', 'Rantfile': '.txt', 'Scanfile': '.txt', 'simplecov': '.txt',
        'Snapfile': '.txt', 'Thorfile': '.txt', 'Vagrantfile': '.Vagrantfile', 'scala': '.scala', 'sbt': '.sbt',
        'sc': '.txt', 'cmd': '.cmd', 'bat': '.bat', 'coffee': '.coffee', 'erl': '.erl',
        'hrl': '.hrl', 'escript': '.escript', 'lua': '.lua', 'md': '.md', 'mdown': '.mdown',
        'mdwn': '.mdwn', 'markdown': '.md', 'markdn': '.md', 'matlab': '.matlab', 'm': '.m',
        'ps1': '.ps1', 'sh': '.sh', 'bash': '.sh', 'bashrc': '.bashrc', 'ash': '.sh',
        'zsh': '.zsh', '.bash_aliases': '.bash_aliases', '.bash_completions': '.bash_completions', '.bash_functions': '.bash_functions', '.bash_login': '.bash_login',
        '.bash_logout': '.bash_logout', '.bash_profile': '.bash_profile', '.bash_variables': '.bash_variables', '.profile': '.profile', '.textmate_init': '.textmate_init',
        '.zlogin': '.zlogin', '.zlogout': '.zlogout', '.zprofile': '.zprofile', '.zshenv': '.zshenv', '.zshrc': '.zshrc',
        'PKGBUILD': '.PKGBUILD', 'ebuild': '.ebuild', 'eclass': '.eclass', 'r': '.r', 'sql': '.sql',
        'ddl': '.ddl', 'dml': '.dml', 'tex': '.tex', 'ltx': '.ltx', 'sty': '.sty',
        'cls': '.cls', 'unknown': '.txt', 'yaml': '.yaml', 'yml': '.yml', 'toml': '.toml',
        'tml': '.txt', 'Cargo.lock': '.lock', 'Gopkg.lock': '.lock', 'Pipfile': '.Pipfile', 'poetry.lock': '.lock',
        'uniform_resource_locator': '.txt', 'custom_url_scheme': '.txt', 'unix_file_path': '.txt', 'windows_file_path': '.txt', 'uniform_resource_identifier': '.txt',
    }

    # Lowercase the language for case-insensitive matching
    language = language.lower()

    # Return the corresponding file extension or default to '.txt' if not found
    return extension_mapping.get(language, '.txt')

def version(**kwargs):
    ### INCOMPLETE ###
    global pieces_os_version
    global cli_version

    if pieces_os_version:
        print(f"Pieces Version: {pieces_os_version}")
        print(f"Cli Version: {cli_version}")
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

###############################################################################
############################## MAIN CLI FUNCTION ##############################
###############################################################################

# def loop(**kwargs):
#     # Logic to return operating system and Python version
   
#     global run_in_loop, parser, ws, pieces_os_version, cli_version, application

#     run_in_loop = True

#     # Open Websocket Connection
    
#     # Do initial check Versions and Ensure Server is Running
#     os_info = platform.platform()
#     python_version = sys.version.split()[0]
#     os_running, os_version, this_application = check()

#     welcome()
    
#     #### PLACEHOLDER ####
#     placeholder_cli_version = "0.1.0"

#     pieces_os_version = os_version
#     cli_version = placeholder_cli_version
#     application = this_application
  
#     print_response(f"Operating System: {os_info}", f"Python Version: {python_version}", f"Pieces OS Version: {os_version if os_running else 'Not available'}", f"Pieces CLI Version: {placeholder_cli_version}", f"Application: {application.name.name}")
#     print_instructions()
        
#     # Start the loop
#     while run_in_loop:
#         is_running, message, application = check()
#         if not is_running:
#             double_line("Server no longer available. Exiting loop.")
#             break

#         # user_input = input("User: ").strip().lower()
#         user_input = input("User: ").strip()
#         command_parts = shlex.split(user_input)
#         if command_parts:
#             command_name = command_parts[0].lower()  # Lowercase only the command name
#             command_args = command_parts[1:]  # Keep the arguments in their original case
#         else:
#             continue  # Skip if the input is empty

#         if user_input == 'exit':
#             double_space("Exiting...")
#             ws_manager.close_websocket_connection()  # Close using the ws_manager instance
#             if ws_thread and ws_thread.is_alive():
#                 ws_thread.join()  # Wait for the WebSocket thread to finish
#             break

#         # Check if the input is a number and treat it as an index for 'open' command
#         if user_input.isdigit():
#             command_name = 'open'
#             command_args = [user_input]
#         else:
#             # Use shlex to split the input into command and arguments
#             split_input = shlex.split(user_input)
#             if not split_input:
#                 continue  # Skip if the input is empty

#             command_name, *command_args = split_input

#         command_name = command_name.lower()

#         if command_name in parser._subparsers._group_actions[0].choices:
#             subparser = parser._subparsers._group_actions[0].choices[command_name]
#             command_func = subparser.get_default('func')  # Get the function associated with the command

#             if command_func:
#                 # Parse the arguments using the subparser
#                 try:
#                     args = subparser.parse_args(command_args)
#                     command_func(**vars(args))
#                 except SystemExit:
#                     # Handle the case where the argument parsing fails
#                     print(f"Invalid arguments for command: {command_name}")
#             else:
#                 print(f"No function associated with command: {command_name}")
#         else:
#             print(f"Unknown command: {command_name}")
        
#         print()

def loop(**kwargs):
    global run_in_loop, parser, ws, pieces_os_version, cli_version, application

    run_in_loop = True

    # Open Websocket Connection

    # Initial setup
    os_info = platform.platform()
    python_version = sys.version.split()[0]

    try:
        os_running, os_version, this_application = check()
        if not os_running:
            raise RuntimeError("Server not running")
    except Exception as e:
        # print(f"Error during startup: {e}")
        sys.exit(1)  # Exit the program

    welcome()

    # Placeholder values
    placeholder_cli_version = "0.1.0"

    pieces_os_version = os_version
    cli_version = placeholder_cli_version
    application = this_application

    print_response(f"Operating System: {os_info}", f"Python Version: {python_version}",
                   f"Pieces OS Version: {pieces_os_version}",
                   f"Pieces CLI Version: {placeholder_cli_version}",
                   f"Application: {application.name.name if application else 'Unknown'}")
    print_instructions()

    # Start the loop
    while run_in_loop:
        try:
            is_running, message, application = check()
            if not is_running:
                raise RuntimeError("Server no longer available")
        except Exception as e:
            print(f"Error in loop: {e}")
            break

        if not is_running:
            double_line("Server no longer available. Exiting loop.")
            break

        try:
            user_input = input("User: ").strip()
            command_parts = shlex.split(user_input)
            if command_parts:
                command_name = command_parts[0].lower()  # Lowercase only the command name
                command_args = command_parts[1:]  # Keep the arguments in their original case
            else:
                continue  # Skip if the input is empty

            if user_input == 'exit':
                double_space("Exiting...")
                ws_manager.close_websocket_connection()  # Close using the ws_manager instance
                if ws_thread and ws_thread.is_alive():
                    ws_thread.join()  # Wait for the WebSocket thread to finish
                break

            # Check if the input is a number and treat it as an index for 'open' command
            if user_input.isdigit():
                command_name = 'open'
                command_args = [user_input]
            else:
                # Use shlex to split the input into command and arguments
                split_input = shlex.split(user_input)
                if not split_input:
                    continue  # Skip if the input is empty

                command_name, *command_args = split_input

            command_name = command_name.lower()

            if command_name in parser._subparsers._group_actions[0].choices:
                subparser = parser._subparsers._group_actions[0].choices[command_name]
                command_func = subparser.get_default('func')  # Get the function associated with the command

                if command_func:
                    # Parse the arguments using the subparser
                    try:
                        args = subparser.parse_args(command_args)
                        command_func(**vars(args))
                    except SystemExit:
                        # Handle the case where the argument parsing fails
                        print(f"Invalid arguments for command: {command_name}")
                else:
                    print(f"No function associated with command: {command_name}")
            else:
                print(f"Unknown command: {command_name}")
        except Exception as e:
            print(f"An error occurred: {e}")

        print()


## def ask(query, **kwargs):
#     global current_model, ws, run_in_loop

#     if current_model:
#         model_id = next(iter(current_model))
#     else:
#         raise ValueError("No model ID available")

#     try:
#         # ws, ws_thread = ask_question(model_id, query, ws, run_in_loop)
#         ws_manager = WebSocketManager()
#         ws, ws_thread = ws_manager.ask_question(model_id, query, run_in_loop)

#     except Exception as e:
#         print(f"Error occurred while asking the question: {e}")
        

## LOOP
        # if user_input == 'exit':
        #     double_space("Exiting...")
        #     if ws:
        #         ws_manager = WebSocketManager()
        #         ws_manager.close_websocket_connection(ws)
        #         # close_websocket_connection(ws)
        #     if ws_thread and ws_thread.is_alive():
        #         ws_thread.join()  # Wait for the WebSocket thread to finish
        #     break