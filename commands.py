from gui import *
from api import *
import platform
import sys
import shlex
from bs4 import BeautifulSoup
import os
import re

# Globals
pieces_os_version = None
run_in_loop = False
asset_ids = {}
current_asset = {}
parser = None

def set_parser(p):
    global parser
    parser = p

def set_pieces_os_version(version):
    global pieces_os_version
    pieces_os_version = version

def version(**kwargs):
    global pieces_os_version
    if pieces_os_version:
        print(pieces_os_version)
    else:
        print("No message available")

def sanitize_filename(name):
    """ Sanitize the filename by removing or replacing invalid characters. """
    # Replace spaces with underscores
    name = name.replace(" ", "_")
    # Remove invalid characters
    name = re.sub(r'[\\/*?:"<>|]', '', name)
    return name
        
def list_assets(max=None, max_flag=None, **kwargs):
    # Determine which max value to use
    # If max_flag is provided (i.e., not None), use it; otherwise, use max
    global run_in_loop, asset_ids
    
    default_max_results = 5
    
    if max_flag is not None:
        max_results = max_flag
    elif max is not None:
        max_results = max
    else:
        max_results = default_max_results  # Use the default if neither max nor max_flag is provided

    ids = get_asset_ids(max=max_results)
    names = get_asset_names(ids)
    
    for i, name in enumerate(names, start=1):
        print(f"{i}: {name}")
        if i >= max_results:
            break

    if run_in_loop:
        asset_ids = {i: id for i, id in enumerate(ids, start=1)}


def open_asset(**kwargs):
    global asset_ids
    global current_asset

    item_index = kwargs.get('ITEM_INDEX')
    asset_id = asset_ids.get(item_index)

    current_asset = get_asset_details(asset_id)

    if asset_id:
        print(f"Loading...")
        print()
        # print(current_asset.get('name'))
        name = current_asset.get('name')
        created_readable = current_asset.get('created', {}).get('readable')
        updated_readable = current_asset.get('updated', {}).get('readable')
        type = current_asset.get('preview', {}).get('base', {}).get('reference', {}).get('classification', {}).get('generic')
        language = current_asset.get('preview', {}).get('base', {}).get('reference', {}).get('classification', {}).get('specific')
        # Assuming current_asset is your JSON object
        formats = current_asset.get('formats', {})
        string = None
        
        if formats:
            iterable = formats.get('iterable', [])
            if iterable:
                first_item = iterable[0] if len(iterable) > 0 else None
                if first_item:
                    fragment_string = first_item.get('fragment', {}).get('string').get('raw')
                    if fragment_string:
                        raw = fragment_string
                        string = extract_code_from_markdown(raw, name)


        # Printing the values with descriptive text
        if name:
            print(f"{name}")
        if created_readable:
            print(f"Created: {created_readable}")
        if updated_readable:
            print(f"Updated: {updated_readable}")
        if type:
            print(f"Type: {type}")
        if language:
            print(f"Language: {language}")
        if formats:
            print(f"Code: {string}")

    else:
        print(f"No asset found for index: {item_index}")

def extract_code_from_markdown(markdown, name):
    # Sanitize the name to ensure it's a valid filename
    filename = sanitize_filename(name)

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
    file_path = os.path.join(directory, f'{filename}.py')

    # Writing the extracted code to a new file
    with open(file_path, 'w') as file:
        file.write(extracted_code)

    return file_path

def save_asset(**kwargs):
    # Logic to save an asset
    print("Saving the File")
    pass

def check():
    # Check if Pieces is Running
    is_running, message = check_api()
    if is_running:
        print("Pieces OS is Running")
        line()
    else:
        double_line("Please start your Pieces OS Server")
    return is_running

def help(**kwargs):
    print_help()
    pass

def loop(**kwargs):
    # Logic to return operating system and Python version
    welcome()
    global run_in_loop, parser

    run_in_loop = True
    
    # Check Versions and Ensure Server is Running
    os_info = platform.platform()
    python_version = sys.version.split()[0]
    os_running, os_version = check_api()
  
    print_response(f"Operating System: {os_info}", f"Python Version: {python_version}", f"Pieces OS Version: {os_version if os_running else 'Not available'}")
    print_instructions()
        
    # Start the loop
    while run_in_loop:
        is_running, message = check_api()
        if not is_running:
            double_line("Server no longer available. Exiting loop.")
            break

        user_input = input("User: ").strip().lower()
        if user_input == 'exit':
            double_space("Exiting...")
            break

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
        
        print()