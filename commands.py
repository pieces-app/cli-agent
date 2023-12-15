from gui import *
from api import *
import platform
import sys
import shlex

# Globals
pieces_os_version = None
run_in_loop = False
asset_ids = {}
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

    item_index = kwargs.get('ITEM_INDEX')
    asset_id = asset_ids.get(item_index)
    if asset_id:
        print(f"Opening asset with ID: {asset_id}")
    else:
        print(f"No asset found for index: {item_index}")

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