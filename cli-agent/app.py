import argparse
import sys
from commands import *
from commands import pieces_os_version

def main():
    # Ensure the Server is running and store Pieces OS version
    is_running, message, application = check_api()
    if is_running:
        # Update the version_message in commands.py
        set_pieces_os_version(message)
        set_application(application)
        # print(application)
        pass
    else:
        double_line("Please start your Pieces OS Server")
        return
    
    # Create the top-level parser
    parser = argparse.ArgumentParser(description='Pieces CLI Tool')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Passes the Parser to commands.py
    set_parser(parser)

    # Subparser for the 'list' command
    list_parser = subparsers.add_parser('list', help='List all assets')
    list_parser.add_argument('max', type=int, nargs='?', default=None, help='(Optional) Maximum number of results to return')
    list_parser.add_argument('--max', dest='max_flag', type=int, help='Maximum number of results to return')
    list_parser.set_defaults(func=list_assets)
    
    # Subparser for the 'open' command
    open_parser = subparsers.add_parser('open', help='Open an asset')
    open_parser.add_argument('ITEM_INDEX', type=int, nargs='?', default=None, help='Index of the item to open (optional)')
    open_parser.set_defaults(func=open_asset)

    # Subparser for the 'save' command
    save_parser = subparsers.add_parser('save', help='Save the current asset')
    save_parser.set_defaults(func=save_asset)

    # Subparser for the 'save' command
    save_parser = subparsers.add_parser('create', help='Create a new asset')
    save_parser.set_defaults(func=create_asset)

    # Subparser for the 'run' command
    run_parser = subparsers.add_parser('run', help='Runs CLI in a loop')
    run_parser.set_defaults(func=loop)

    # Subparser for the 'version' command
    version_parser = subparsers.add_parser(
    'version',
    help='Gets version of Pieces OS',
    description='This command displays the current version of Pieces OS. It does not require any additional arguments.'
    )
    version_parser.set_defaults(func=version)

    # Subparser for the 'help' command
    help_parser = subparsers.add_parser('help', help='Prints a list of available commands')
    help_parser.set_defaults(func=help)

    # Parse the arguments if provided
    if len(sys.argv) > 1:
        args = parser.parse_args()
        # Execute the corresponding function with the parsed arguments
        args.func(**vars(args))

if __name__ == '__main__':
    main()