import argparse
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

def run(**kwargs):
    # Logic to return operating system and Python version
    os_info = platform.platform()
    python_version = sys.version.split()[0]
    print(f"Operating System: {os_info}")
    print(f"Python Version: {python_version}")

def main():
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
    run_parser = subparsers.add_parser('run', help='Run the system diagnostics')
    run_parser.set_defaults(func=run)

    # Parse the arguments
    args = parser.parse_args()

    # Execute the corresponding function with the parsed arguments
    args.func(**vars(args))

if __name__ == '__main__':
    main()