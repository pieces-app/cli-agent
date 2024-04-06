import argparse
from pieces.commands import *
import sys
from pieces.gui import show_error,print_help
from pieces.api.config import pos_client, api_client
from pieces.api.api_functions import sign_out

class PiecesCli(argparse.ArgumentParser): # subclassing the ArgumentParser class to modify the error messages
    def error(self, message):
        if 'invalid choice' in message:
            try:
                invalid_command = message.split("'")[1]
                suggestion_text = f"Did you mean '{find_most_similar_command(list(self._subparsers._group_actions[0].choices.keys()),invalid_command)}'?"
                # Custom error message for invalid command choices
                print(f"Invalid command '{invalid_command}'\n{suggestion_text}")
            except IndexError:
                suggestion_text = ""
                invalid_command = "Unknown"
                # Custom error message for invalid command choices
                print(f"Invalid command '{invalid_command}'\n{suggestion_text}")
            except AttributeError:
                show_error("Error occured",message)
            
            
        else:
            # Default error message for other types of errors
            show_error("Error occured",message)
        sys.exit(2)



def main():
    # Create the top-level parser
    parser = PiecesCli(description='Pieces CLI Tool')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Passes the Parser to commands.py
    set_parser(parser)

    # Subparser for the 'lists' command
    list_parser = subparsers.add_parser('list', help='List the assets or apps or models')
    list_parser.add_argument('type', nargs='?', type=str ,default="assets", help='type of the list',choices=["assets","apps","models"])
    list_parser.add_argument('max_assets', nargs='?', type=int ,default=10, help='Max number of assets')
    list_parser.set_defaults(func=list_command)


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
    ask_parser.add_argument('--file','-f', nargs='?', type=str,dest='file', help='Folder or file as a relevance you can enter a absolute or relative path')
    #ask_parser.add_argument("")
    ask_parser.set_defaults(func=ask)

    # Subparser for the 'version' command
    version_parser = subparsers.add_parser('version', help='Gets version of Pieces OS')
    version_parser.set_defaults(func=version)

    # Subparser for Search
    search_parser = subparsers.add_parser('search', help='Search with a query string')
    search_parser.add_argument('query', type=str, nargs='+', help='Query string for the search')
    search_parser.add_argument('--mode', type=str, dest='search_type', default='assets', choices=['assets', 'ncs', 'fts'], help='Type of search')
    search_parser.set_defaults(func=search)


    # Subparser for the 'help' command
    help_parser = subparsers.add_parser('help', help='Prints a list of available commands')
    help_parser.set_defaults(func=lambda **kwargs: print_help())


    # Subparser for the 'change_model' command
    change_model_parser = subparsers.add_parser('change_model', help='Change the model that you are using in the ask')
    change_model_parser.add_argument('MODEL_INDEX', type=int, nargs='?', default=None, help='Index of the model to use (optional)')
    change_model_parser.set_defaults(func=change_model)

    # Subparser for the 'login' command
    login_parser = subparsers.add_parser('login', help='Login to pieces os')
    login_parser.set_defaults(func=lambda **kwargs: print(f'Logged in as {pos_client.OSApi(api_client).sign_into_os().name}'))

    # Subparser for the 'logout' command
    logout_parser = subparsers.add_parser('logout', help='Logout from pieces os')
    logout_parser.set_defaults(func=lambda **kwargs:print("Logged out successfully") if sign_out() else print('Failed to logout out'))


    # Subparser for the 'conversations' command
    conversations_parser = subparsers.add_parser('conversations', help='print all conversations')
    conversations_parser.set_defaults(func=get_conversations)
    

    # Subparser for the 'conversation' command
    conversation_parser = subparsers.add_parser('conversation', help='print all conversations')
    conversation_parser.add_argument('CONVERSATION_INDEX', type=int, nargs='?', default=None, help='Index of the conversation if None it will get the current conversation.')
    conversation_parser.add_argument("-n","--new",action="store_true",dest="new", help="Create a new conversation")
    conversation_parser.set_defaults(func=conversation_handler)


    # Subparser for the 'commit' command
    commit_parser = subparsers.add_parser('commit', help='Auto generate a github commit messaage and commit changes')
    commit_parser.add_argument("-p","--push",action="store_true", help="push the code to github")
    commit_parser.set_defaults(func=git_commit)


    try:
        arg = sys.argv[1]
    except IndexError: # No command provided
        print_help()
        return

    # Check if the 'run' or 'help' command is explicitly provided
    if not arg in ['help', 'run']:
        startup()

    args = parser.parse_args()
    args.func(**vars(args))


if __name__ == '__main__':
    main()