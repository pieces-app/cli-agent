import sys
from pieces_os_client.api.os_api import OSApi


from pieces.gui import print_help
from pieces.pieces_argparser import PiecesArgparser
from pieces.settings import Settings


from pieces.commands import *
from pieces.autocommit import *
from pieces.copilot import *
from pieces.assets import *

class PiecesCLI:
    def __init__(self):
        self.parser = PiecesArgparser(description="CLI for interacting with the pieces library",add_help=False)
        self.command_parser = self.parser.add_subparsers(dest='command', required=True)
        self.add_subparsers()
        PiecesArgparser.parser = self.parser

    def add_subparsers(self):

        # Subparser for the 'config' command
        config_parser = self.command_parser.add_parser('config', help='Configure settings')
        config_parser.add_argument('--editor',"-e",dest="editor", type=str, help='Set the default code editor')
        config_parser.set_defaults(func=ConfigCommands.config)

        # Subparser for the 'lists' command
        list_parser = self.command_parser.add_parser('list', help='List the assets or apps or models')
        list_parser.add_argument('type', nargs='?', type=str ,default="assets", help='type of the list',choices=["assets","apps","models"])
        list_parser.add_argument('max_assets', nargs='?', type=int ,default=10, help='Max number of assets')
        list_parser.add_argument("--editor","-e",dest="editor",action="store_true" ,default=False, help="Open the choosen asset in the editor")
        list_parser.set_defaults(func=ListCommand.list_command)


        # Subparser for the 'open' command
        open_parser = self.command_parser.add_parser('open', help='Open an asset')
        open_parser.add_argument('ITEM_INDEX', type=int, nargs='?', default=None, help='Index of the item to open (optional)')
        open_parser.set_defaults(func=AssetsCommands.open_asset)

        # Subparser for the 'save' command
        save_parser = self.command_parser.add_parser('save', help='Updates the current asset')
        save_parser.set_defaults(func=AssetsCommands.update_asset)

        # Subparser for the 'delete' command
        delete_parser = self.command_parser.add_parser('delete', help='Delete the current asset')
        delete_parser.set_defaults(func=AssetsCommands.delete_asset)

        # Subparser for the 'create' command
        create_parser = self.command_parser.add_parser('create', help='Create a new asset')
        create_parser.set_defaults(func=AssetsCommands.create_asset)

        # Subparser for the 'run' command
        run_parser = self.command_parser.add_parser('run', help='Runs CLI in a loop')
        run_parser.set_defaults(func=loop)

        # Subparser for the 'execute' command
        execute_parser = self.command_parser.add_parser('execute', help='Execute shell or bash assets')
        execute_parser.add_argument('max_assets', nargs='?', type=int, default=10, help='Max number of assets to display')
        execute_parser.set_defaults(func=ExecuteCommand.execute_command)

        # Subparser for the 'edit' command
        edit_parser = self.command_parser.add_parser('edit', help='Edit an existing asset')
        edit_parser.add_argument('--name',"-n",dest='name', help='New name for the asset', required=False)
        edit_parser.add_argument('--classification',"-c",dest='classification', help='reclassify the asset', required=False)
        edit_parser.set_defaults(func=AssetsCommands.edit_asset)

        # Subparser for the 'ask' command
        ask_parser = self.command_parser.add_parser('ask', help='Ask a question to a model')
        ask_parser.add_argument('query', type=str, help='Question to be asked to the model')
        ask_parser.add_argument('--files','-f', nargs='*', type=str,dest='files', help='Folder or file as a relevance you can enter an absolute or relative path')
        ask_parser.add_argument('--snippets','-s', nargs='*', type=int,dest='snippets', help='Snippet of the question to be asked to the model check list assets')
        ask_parser.set_defaults(func=ask)

        # Subparser for the 'version' command
        version_parser = self.command_parser.add_parser('version', help='Gets version of Pieces OS')
        version_parser.set_defaults(func=version)

        # Subparser for Search
        search_parser = self.command_parser.add_parser('search', help='Search with a query string')
        search_parser.add_argument('query', type=str, nargs='+', help='Query string for the search')
        search_parser.add_argument('--mode', type=str, dest='search_type', default='assets', choices=['assets', 'ncs', 'fts'], help='Type of search')
        search_parser.set_defaults(func=search)


        # Subparser for the 'help' command
        help_parser = self.command_parser.add_parser('help', help='Prints a list of available commands')
        help_parser.set_defaults(func=lambda **kwargs: print_help())


        # Subparser for the 'change_model' command
        change_model_parser = self.command_parser.add_parser('change_model', help='Change the model that you are using in the ask')
        change_model_parser.add_argument('MODEL_INDEX', type=int, nargs='?', default=None, help='Index of the model to use (optional)')
        change_model_parser.set_defaults(func=change_model)

        # Subparser for the 'login' command
        login_parser = self.command_parser.add_parser('login', help='Login to pieces os')
        login_parser.set_defaults(func=lambda **kwargs: print(f'Logged in as {OSApi(Settings.api_client).sign_into_os().name}'))

        # Subparser for the 'logout' command
        logout_parser = self.command_parser.add_parser('logout', help='Logout from pieces os')
        logout_parser.set_defaults(func=lambda **kwargs:print("Logged out successfully") if sign_out() else print('Failed to logout out'))


        # Subparser for the 'conversations' command
        conversations_parser = self.command_parser.add_parser('conversations', help='print all conversations')
        conversations_parser.set_defaults(func=get_conversations)
        

        # Subparser for the 'conversation' command
        conversation_parser = self.command_parser.add_parser('conversation', help='print all conversations')
        conversation_parser.add_argument('CONVERSATION_INDEX', type=int, nargs='?', default=None, help='Index of the conversation if None it will get the current conversation.')
        conversation_parser.add_argument("-n","--new",action="store_true",dest="new", help="Create a new conversation")
        conversation_parser.add_argument("-r","--rename",dest="rename",nargs='?', const=True,
                            help="Rename the conversation that you are currently. If nothing is specified it will rename the current conversation using the llm model")
        conversation_parser.add_argument("-d","--delete",action="store_true", dest="delete", help="Delete the conversation that you are currently using in the ask command")
        conversation_parser.set_defaults(func=conversation_handler)


        # Subparser for the 'commit' command
        commit_parser = self.command_parser.add_parser('commit', help='Auto generate a github commit messaage and commit changes')
        commit_parser.add_argument("-p","--push",dest="push",action="store_true", help="push the code to github")
        commit_parser.add_argument("-a","--all",dest="all_flag",action="store_true", help="stage all the files before commiting")
        commit_parser.add_argument("-i","--issues",dest="issue_flag",action="store_true", help="add issue number in the commit message")
        commit_parser.set_defaults(func=git_commit)

    def run(self):
        try:
            arg = sys.argv[1]
        except IndexError: # No command provided
            print_help()
            return

        # Check if the 'run' or 'help' command is explicitly provided
        if arg not in ['help']:
            Settings.startup()

        args = self.parser.parse_args()
        args.func(**vars(args))

def main():
    cli = PiecesCLI()
    cli.run()

if __name__ == "__main__":
    main()
