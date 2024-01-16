import argparse
import sys
from commands import *

def main():
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
    delete_parser = subparsers.add_parser('delete', help='Delete the current asset')
    delete_parser.set_defaults(func=delete_asset)

    # Subparser for the 'create' command
    create_parser = subparsers.add_parser('create', help='Create a new asset')
    create_parser.set_defaults(func=create_asset)

    # Subparser for the 'run' command
    run_parser = subparsers.add_parser('run', help='Runs CLI in a loop')
    run_parser.set_defaults(func=loop)

    # Subparser for the 'edit' command
    edit_parser = subparsers.add_parser('edit', help='Edit an existing asset')
    edit_parser.set_defaults(func=edit_asset)

    # Subparser for the 'ask' command
    ask_parser = subparsers.add_parser('ask', help='Ask a question to a model')
    ask_parser.add_argument('query', type=str, help='Question to be asked to the model')
    ask_parser.set_defaults(func=ask)

    # Subparser for the 'version' command
    version_parser = subparsers.add_parser('version', help='Gets version of Pieces OS')
    version_parser.set_defaults(func=version)

    # Subparser for Search
    search_parser = subparsers.add_parser('search', help='Search with a query string')
    search_parser.add_argument('query', type=str, nargs='+', help='Query string for the search')
    search_parser.add_argument('--mode', type=str, dest='search_type', default='assets', choices=['assets', 'ncs', 'fts'], help='Type of search (assets, ncs, fts)')
    search_parser.set_defaults(func=search)

    # TEMP Subparser for listing models
    models_parser = subparsers.add_parser('list_models', help='List available models')
    models_parser.set_defaults(func=list_all_models)

    # Subparser for the 'help' command
    help_parser = subparsers.add_parser('help', help='Prints a list of available commands')
    help_parser.set_defaults(func=help)

    # Check if the 'run' command is explicitly provided
    if len(sys.argv) > 1 and sys.argv[1] in ['help', 'run']:
        args = parser.parse_args()
        args.func(**vars(args))
    else:
        # Call check_api and store its return value
        api_response = check_api()

        # Check the length of the response and if the server is running with an application
        if len(api_response) == 3 and api_response[0] and api_response[2]:
            is_running, message, application = api_response

            # Update the version_message in commands.py
            set_pieces_os_version(message)
            set_application(application)

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