import sys
from pieces.gui import print_help
from pieces.pieces_argparser import PiecesArgparser
from pieces.settings import Settings

from pieces.commands import (
    loop,
    version,
    search,
    sign_out,
    sign_in,
    ListCommand,
    ConfigCommands,
    ExecuteCommand,
    AssetsCommands,
    onboarding_command,
    feedback,
    contribute,
    PiecesInsertaller
)
from pieces.autocommit import git_commit
from pieces.copilot import (AskStream, conversation_handler, get_conversations)

from pieces import __version__
ask_stream = AskStream()


class PiecesCLI:
    def __init__(self):
        self.parser = PiecesArgparser(
            description="Pieces CLI for interacting with the PiecesOS",
            add_help=False)
        self.command_parser = self.parser.add_subparsers(dest='command')
        self.parser.add_argument(
            "--version", "-v", action="store_true",
            help="Displays the Pieces CLI version")
        self.parser.set_defaults(func=lambda **kwargs: print(__version__))
        self.add_subparsers()
        PiecesArgparser.parser = self.parser

    def add_subparsers(self):

        # Subparser for the 'config' command
        config_parser = self.command_parser.add_parser(
            'config', help='Configure settings')
        config_parser.add_argument(
            '--editor', "-e", dest="editor", type=str,
            help='Set the default code editor')
        config_parser.set_defaults(func=ConfigCommands.config)

        # Subparser for the 'lists' command
        list_parser = self.command_parser.add_parser(
            'list', aliases=["drive"], help='List materials or apps or models')
        list_parser.add_argument('type', nargs='?', type=str,
                                 default="materials",
                                 help='type of the list',
                                 choices=["materials", "apps", "models"])
        list_parser.add_argument(
            'max_snippets', nargs='?', type=int, default=10,
            help='Max number of materials')
        list_parser.add_argument("--editor", "-e", dest="editor",
                                 action="store_true",
                                 default=False,
                                 help="Open the choosen material in the editor")
        list_parser.set_defaults(func=ListCommand.list_command)

        # Subparser for the 'save' command
        save_parser = self.command_parser.add_parser(
            'save', help='Updates the current material', aliases=["modify"])
        save_parser.set_defaults(func=AssetsCommands.save_asset)

        # Subparser for the 'delete' command
        delete_parser = self.command_parser.add_parser(
            'delete', help='Delete the current material')
        delete_parser.set_defaults(func=AssetsCommands.delete_asset)

        # Subparser for the 'create' command
        create_parser = self.command_parser.add_parser(
            'create', help='Create a new material')
        create_parser.set_defaults(func=AssetsCommands.create_asset)

        # Subparser for the 'run' command
        run_parser = self.command_parser.add_parser(
            'run', help='Runs CLI in a loop')
        run_parser.set_defaults(func=loop)

        # Subparser for the 'execute' command
        execute_parser = self.command_parser.add_parser(
            'execute', help='Execute shell or bash materials')
        execute_parser.set_defaults(func=ExecuteCommand.execute_command)

        # Subparser for the 'edit' command
        edit_parser = self.command_parser.add_parser(
            'edit', help='Edit an existing materials')
        edit_parser.add_argument(
            '--name', "-n", dest='name', help='New name for the materials',
            required=False)
        edit_parser.add_argument('--classification', "-c",
                                 dest='classification',
                                 help='reclassify a material', required=False)
        edit_parser.set_defaults(func=AssetsCommands.edit_asset)

        # Subparser for the 'ask' command
        ask_parser = self.command_parser.add_parser(
            'ask', help='Ask a question to the Copilot')
        ask_parser.add_argument(
            'query', type=str, help='Question to be asked to the Copilot')
        ask_parser.add_argument('--files', '-f', nargs='*', type=str,
                                dest='files',
                                help='Folder or file as a context you can enter an absolute or relative path')
        ask_parser.add_argument('--materials', '-m', nargs='*', type=int,
                                dest='materials',
                                help='Materials of the question to be asked to the model check list materials')
        ask_parser.set_defaults(func=ask_stream.ask)

        # Subparser for the 'version' command
        version_parser = self.command_parser.add_parser(
            'version', help='Gets version of PiecesOS')
        version_parser.set_defaults(func=version)

        # Subparser for Search
        search_parser = self.command_parser.add_parser(
            'search', help='Perform a search for materials using the specified query string')
        search_parser.add_argument(
            'query', type=str, nargs='+', help='Query string for the search')
        search_parser.add_argument('--mode', type=str, dest='search_type',
                                   default='fuzzy',
                                   choices=['fuzzy', 'ncs', 'fts'],
                                   help='Type of search')
        search_parser.set_defaults(func=search)

        # Subparser for the 'help' command
        help_parser = self.command_parser.add_parser(
            'help', help='Prints a list of available commands')
        help_parser.set_defaults(func=lambda **kwargs: print_help())

        # Subparser for the 'login' command
        login_parser = self.command_parser.add_parser(
            'login', help='Login to PiecesOS')
        login_parser.set_defaults(func=sign_in)

        # Subparser for the 'logout' command
        logout_parser = self.command_parser.add_parser(
            'logout', help='Logout from PiecesOS')
        logout_parser.set_defaults(func=sign_out)

        # Subparser for the 'conversations' command
        conversations_parser = self.command_parser.add_parser(
            'chats', aliases=['conversations'], help='print all chats')
        conversations_parser.add_argument(
            'max_chats', nargs='?', type=int,
            default=10, help='Max number of chats to show')
        conversations_parser.set_defaults(func=get_conversations)

        # Subparser for the 'conversation' command
        conversation_parser = self.command_parser.add_parser(
            'chat', aliases=['conversation'], help='Select a chat')
        conversation_parser.add_argument('CONVERSATION_INDEX', type=int,
                                         nargs='?', default=None,
                                         help='Index of the chat if None it will get the current conversation.')
        conversation_parser.add_argument(
            "-n", "--new", action="store_true", dest="new",
            help="Create a new chat")
        conversation_parser.add_argument("-r", "--rename", dest="rename",
                                         nargs='?', const=True,
                                         help="Rename the conversation that you are currently. If nothing is specified it will rename the current chat using the llm model")
        conversation_parser.add_argument("-d", "--delete", action="store_true",
                                         dest="delete",
                                         help="Delete the chat that you are currently using in the ask command")
        conversation_parser.set_defaults(func=conversation_handler)

        # Subparser for the 'commit' command
        commit_parser = self.command_parser.add_parser(
            'commit',
            help='Auto-generate a GitHub commit message and commit changes')
        commit_parser.add_argument(
            "-p", "--push", dest="push", action="store_true",
            help="Push the code to GitHub")
        commit_parser.add_argument("-a", "--all", dest="all_flag",
                                   action="store_true",
                                   help="Stage all the files before committing")
        commit_parser.add_argument("-i", "--issues", dest="issue_flag",
                                   action="store_true",
                                   help="Add issue number in the commit message")
        commit_parser.set_defaults(func=git_commit)

        # Subparser for the 'onboarding' command
        onboarding_parser = self.command_parser.add_parser(
            'onboarding', help='Start the onboarding process')
        onboarding_parser.set_defaults(func=onboarding_command)

        # Subparser for the 'feedback' command
        feedback_parser = self.command_parser.add_parser(
            'feedback', help='Submit feedback')
        feedback_parser.set_defaults(func=feedback)

        # Subparser for the 'contribute' command
        contribute_parser = self.command_parser.add_parser(
            'contribute', help='How to contribute')
        contribute_parser.set_defaults(func=contribute)

        # Subparser for the 'install' command
        install_parser = self.command_parser.add_parser(
            'install', help='Install PiecesOS')
        install_parser.set_defaults(
            func=lambda **kwargs: PiecesInsertaller().run())

        # Subparser for the 'open' command
        open_parser = self.command_parser.add_parser(
            'open', help='Opens PiecesOS')
        open_parser.set_defaults(
            func=lambda **kwargs: Settings.pieces_client.open_pieces_os())

    def run(self):
        try:
            arg = sys.argv[1]
        except IndexError:  # No command provided
            print_help()
            return

        config = ConfigCommands.load_config()

        onboarded = config.get("onboarded", False)

        if not config.get("skip_onboarding", False) and not onboarded:
            res = input(
                "It looks like this is your first time using the Pieces CLI."
                "\nWould you like to start onboarding (y/n/skip)? ")
            if res.lower() == "y":
                return onboarding_command()
            elif res.lower() == "skip":
                config["skip_onboarding"] = True
                ConfigCommands.save_config(config)

        # Check if the command needs PiecesOS or not
        if arg not in ['help', "-v", "--version",
                       "install", "onboarding",
                       "feedback", "contribute", "open"]:
            Settings.startup()

        args = self.parser.parse_args()
        args.func(**vars(args))


def main():
    cli = PiecesCLI()
    cli.run()


if __name__ == "__main__":
    main()
