from gui import welcome, line, double_line
from api import *
import platform
import sys

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
    print("save")
    pass

def version(message):
    print(message)

def version_with_message(**kwargs):
    global message
    version(message)

def check():
    # Check if Pieces is Running
    is_running, message = check_api()
    if is_running:
        print("Pieces OS is Running")
        line()
    else:
        double_line("Please start your Pieces OS Server")
    return is_running

def loop(**kwargs):
    # Logic to return operating system and Python version
    welcome()
    os_info = platform.platform()
    python_version = sys.version.split()[0]
    print(f"Operating System: {os_info}")
    print(f"Python Version: {python_version}")

    # Check Pieces OS version
    os_running, os_version = check_api()
    print(f"Pieces OS Version: {os_version if os_running else 'Not available'}")
    print()
    print("Enter command (type 'exit' to quit)")
    print(f"Ready...")
    line()
    
    # Start the loop
    while True:
        is_running, message = check_api()
        if not is_running:
            double_line("Server no longer available. Exiting loop.")
            break

        user_input = input()
        if user_input.strip().lower() == 'exit':
            print("Exiting...")
            break

        print(user_input)