from gui import *
from api import *
import platform
import sys

pieces_os_version = None

def set_pieces_os_version(version):
    global pieces_os_version
    pieces_os_version = version

def version(**kwargs):
    global pieces_os_version
    if pieces_os_version:
        print(pieces_os_version)
    else:
        print("No message available")

def list_assets(**kwargs):
    # Logic to list assets
    print("list") 
    pass

def open_asset(**kwargs):
    # Logic to open an asset
    item_index = kwargs.get('ITEM_INDEX')
    print(f"open {item_index}")
    pass

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
    
    # Check Versions and Ensure Server is Running
    os_info = platform.platform()
    python_version = sys.version.split()[0]
    os_running, os_version = check_api()
  
    print_response(f"Operating System: {os_info}", f"Python Version: {python_version}", f"Pieces OS Version: {os_version if os_running else 'Not available'}")
    print_instructions()
        
    # Start the loop
    while True:
        is_running, message = check_api()
        if not is_running:
            double_line("Server no longer available. Exiting loop.")
            break

        user_input = input("User: ").strip().lower()
        if user_input == 'exit':
            double_space("Exiting...")
            break

        # Check if the input is a command and call the corresponding function
        if user_input in commands:
            print()
            print("Response: ")
            command = commands[user_input]
            command(**kwargs)
            print()
        else:
            print(f"Unknown command: {user_input}")

commands = {
        "list": list_assets,
        "open": open_asset,
        "save": save_asset,
        "version": version,
        "help": help
    }