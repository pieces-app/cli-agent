import argparse
import sys
from commands import *
from commands import pieces_os_version

def main():
    # Call check_api and store its return value
    api_response = check_api()

    # Check the length of the response and if the server is running with an application
    if len(api_response) == 3 and api_response[0] and api_response[2]:
        is_running, message, application = api_response

        # Update the version_message in commands.py
        set_pieces_os_version(message)
        set_application(application)
    
        # Create the top-level parser
        parser = argparse.ArgumentParser(description='Pieces CLI Tool')
        subparsers = parser.add_subparsers(dest='command', required=True)

        # Passes the Parser to commands.py
        set_parser(parser)

        # Subparser for the 'list' command
        list_parser = subparsers.add_parser('list', help='List assets or applications')
        list_parser.add_argument('list_type_or_max', nargs='?', default='assets', help='Specify "apps" to list applications or a number for maximum assets to list, defaults to listing assets')
        list_parser.set_defaults(func=list_assets)
        
        # Subparser for the 'open' command
        open_parser = subparsers.add_parser('open', help='Open an asset')
        open_parser.add_argument('ITEM_INDEX', type=int, nargs='?', default=None, help='Index of the item to open (optional)')
        open_parser.set_defaults(func=open_asset)

        # Subparser for the 'save' command
        save_parser = subparsers.add_parser('save', help='Updates the current asset')
        save_parser.set_defaults(func=save_asset)

        # Subparser for the 'delete' command
        save_parser = subparsers.add_parser('delete', help='Delete the current asset')
        save_parser.set_defaults(func=delete_asset)

        # Subparser for the 'create' command
        save_parser = subparsers.add_parser('create', help='Create a new asset')
        save_parser.set_defaults(func=create_asset)

        # Subparser for the 'run' command
        run_parser = subparsers.add_parser('run', help='Runs CLI in a loop')
        run_parser.set_defaults(func=loop)

        # Subparser for the 'edit' command
        run_parser = subparsers.add_parser('edit', help='Runs CLI in a loop')
        run_parser.set_defaults(func=edit_asset)

        # Subparser for the 'version' command
        version_parser = subparsers.add_parser(
        'version',
        help='Gets version of Pieces OS',
        description='This command displays the current version of Pieces OS. It does not require any additional arguments.'
        )
        version_parser.set_defaults(func=version)

        # Subparser for the 'search' command
        # search_parser = subparsers.add_parser('search', help='Search with a query string')
        # search_parser.add_argument('query', type=str, nargs='+', help='Query string for the search')
        # search_parser.set_defaults(func=search)
        search_parser = subparsers.add_parser('search', help='Search with a query string')
        search_parser.add_argument('query', type=str, nargs='+', help='Query string for the search')
        search_parser.add_argument('--type', type=str, dest='search_type', default='assets', choices=['assets', 'ncs', 'fts'], help='Type of search (assets, ncs, fts)')
        search_parser.set_defaults(func=search)




        # Subparser for the 'help' command
        help_parser = subparsers.add_parser('help', help='Prints a list of available commands')
        help_parser.set_defaults(func=help)

        # Parse the arguments if provided
        if len(sys.argv) > 1:
            args = parser.parse_args()
            # Execute the corresponding function with the parsed arguments
            args.func(**vars(args))

    else:
        # Display the message if the server is not running or application is not present
        double_line("Please start your Pieces OS Server")

if __name__ == '__main__':
    main()