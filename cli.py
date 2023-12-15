import argparse
import platform
import sys

from gui import welcome, line, double_line
from api import check_api

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

def main():
    # Directly call the run function on startup
    global message
    is_running, message = check_api()
    if is_running:
        pass
    else:
        double_line("Please start your Pieces OS Server")
        return

    # Create the top-level parser
    parser = argparse.ArgumentParser(description='Pieces CLI Tool')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Subparser for the 'list' command
    list_parser = subparsers.add_parser('list', help='List all assets')
    list_parser.set_defaults(func=list_assets)

    # Subparser for the 'open' command
    open_parser = subparsers.add_parser('open', help='Open an asset')
    open_parser.add_argument('ITEM_INDEX', type=int, help='Index of the item to open')
    open_parser.set_defaults(func=open_asset)

    # Subparser for the 'save' command
    save_parser = subparsers.add_parser('save', help='Save the current asset')
    save_parser.set_defaults(func=save_asset)

    # Subparser for the 'run' command
    run_parser = subparsers.add_parser('run', help='Runs CLI in a loop')
    run_parser.set_defaults(func=loop)

    version_parser = subparsers.add_parser('version', help='Gets version of Pieces OS')
    version_parser.set_defaults(func=version_with_message)

    # Parse the arguments if provided
    if len(sys.argv) > 1:
        args = parser.parse_args()
        # Execute the corresponding function with the parsed arguments
        args.func(**vars(args))

if __name__ == '__main__':
    main()