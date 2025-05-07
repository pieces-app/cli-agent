import sys
from pieces.pieces_argparser import PiecesArgparser
from pieces.settings import Settings
from pieces.logger import Logger

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
    PiecesInstaller,
    open_command,
)
from pieces.autocommit import git_commit
from pieces.copilot import AskStream, conversation_handler, get_conversations
from pieces.mcp import (
    handle_mcp,
    handle_list,
    handle_mcp_docs,
    handle_repair,
    handle_status,
)
from pieces import __version__

ask_stream = AskStream()


class PiecesCLI:
    # TODO: Add some examples for each command (to be more user friendly)
    def __init__(self):
        self.parser = PiecesArgparser(
            description="Pieces CLI for interacting with the PiecesOS",
        )
        self.command_parser = self.parser.add_subparsers(dest="command")
        self.parser.add_argument(
            "--version",
            "-v",
            action="store_true",
            help="Displays the Pieces CLI version",
        )
        self.parser.add_argument(
            "--ignore-onboarding",
            action="store_true",
            help="Ignores the onboarding for the running command",
        )
        self.parser.set_defaults(func=lambda **kwargs: print(__version__))
        self.add_subparsers()
        PiecesArgparser.parser = self.parser

    def add_subparsers(self):
        # Subparser for the 'config' command
        config_parser = self.command_parser.add_parser(
            "config", help="Configure settings"
        )
        config_parser.add_argument(
            "--editor",
            "-e",
            dest="editor",
            type=str,
            help="Set the default code editor",
        )
        config_parser.set_defaults(func=ConfigCommands.config)

        # Subparser for the 'lists' command
        list_parser = self.command_parser.add_parser(
            "list",
            aliases=["drive"],
            help="List materials or apps or models",
            description="Pieces CLI List (Alias for drive)",
        )
        list_parser.add_argument(
            "type",
            nargs="?",
            type=str,
            default="materials",
            help="Type of the list",
            choices=["materials", "apps", "models"],
        )
        list_parser.add_argument(
            "max_snippets",
            nargs="?",
            type=int,
            default=10,
            help="Max number of materials",
        )
        list_parser.add_argument(
            "--editor",
            "-e",
            dest="editor",
            action="store_true",
            default=False,
            help="Open the choosen material in the editor",
        )
        list_parser.set_defaults(func=ListCommand.list_command)

        # Subparser for the 'save' command
        save_parser = self.command_parser.add_parser(
            "save", help="Updates the current material", aliases=["modify"]
        )
        save_parser.set_defaults(func=AssetsCommands.save_asset)

        # Subparser for the 'delete' command
        delete_parser = self.command_parser.add_parser(
            "delete", help="Delete the current material"
        )
        delete_parser.set_defaults(func=AssetsCommands.delete_asset)

        # Subparser for the 'create' command
        create_parser = self.command_parser.add_parser(
            "create", help="Create a new material"
        )
        create_parser.add_argument(
            "-c",
            "--content",
            dest="content",
            action="store_true",
            help="Specify the content of the material",
        )
        create_parser.set_defaults(func=AssetsCommands.create_asset)

        share_parser = self.command_parser.add_parser(
            "share", help="Share the current material"
        )
        share_parser.set_defaults(func=AssetsCommands.share_asset)

        # Subparser for the 'run' command
        run_parser = self.command_parser.add_parser("run", help="Runs CLI in a loop")
        run_parser.set_defaults(func=loop)

        # Subparser for the 'execute' command
        execute_parser = self.command_parser.add_parser(
            "execute", help="Execute shell or bash materials"
        )
        execute_parser.set_defaults(func=ExecuteCommand.execute_command)

        # Subparser for the 'edit' command
        edit_parser = self.command_parser.add_parser(
            "edit", help="Edit an existing materials"
        )
        edit_parser.add_argument(
            "--name",
            "-n",
            dest="name",
            help="New name for the materials",
            required=False,
        )
        edit_parser.add_argument(
            "--classification",
            "-c",
            dest="classification",
            help="Reclassify a material",
            required=False,
        )
        edit_parser.set_defaults(func=AssetsCommands.edit_asset)

        # Subparser for the 'ask' command
        ask_parser = self.command_parser.add_parser(
            "ask", help="Ask a question to the Copilot"
        )
        ask_parser.add_argument(
            "query", type=str, help="Question to be asked to the Copilot"
        )
        ask_parser.add_argument(
            "--files",
            "-f",
            nargs="*",
            type=str,
            dest="files",
            help="Folder or file as a context you can enter an absolute or relative path",
        )
        ask_parser.add_argument(
            "--materials",
            "-m",
            nargs="*",
            type=int,
            dest="materials",
            help="Materials of the question to be asked to the model check list materials",
        )
        ask_parser.set_defaults(func=ask_stream.ask)

        # Subparser for the 'version' command
        version_parser = self.command_parser.add_parser(
            "version", help="Gets version of PiecesOS"
        )
        version_parser.set_defaults(func=version)

        # Subparser for Search
        search_parser = self.command_parser.add_parser(
            "search",
            help="Perform a search for materials using the specified query string",
        )
        search_parser.add_argument(
            "query", type=str, nargs="+", help="Query string for the search"
        )
        search_parser.add_argument(
            "--mode",
            type=str,
            dest="search_type",
            default="fuzzy",
            choices=["fuzzy", "ncs", "fts"],
            help="Type of search",
        )
        search_parser.set_defaults(func=search)

        # Subparser for the 'help' command
        help_parser = self.command_parser.add_parser(
            "help", help="Prints a list of available commands"
        )
        help_parser.set_defaults(func=lambda **kwargs: self.parser.print_help())

        # Subparser for the 'login' command
        login_parser = self.command_parser.add_parser("login", help="Login to PiecesOS")
        login_parser.set_defaults(func=sign_in)

        # Subparser for the 'logout' command
        logout_parser = self.command_parser.add_parser(
            "logout", help="Logout from PiecesOS"
        )
        logout_parser.set_defaults(func=sign_out)

        # Subparser for the 'conversations' command
        conversations_parser = self.command_parser.add_parser(
            "chats", aliases=["conversations"], help="Print all chats"
        )
        conversations_parser.add_argument(
            "max_chats",
            nargs="?",
            type=int,
            default=10,
            help="Max number of chats to show",
        )
        conversations_parser.set_defaults(func=get_conversations)

        # Subparser for the 'conversation' command
        conversation_parser = self.command_parser.add_parser(
            "chat", aliases=["conversation"], help="Select a chat"
        )
        conversation_parser.add_argument(
            "CONVERSATION_INDEX",
            type=int,
            nargs="?",
            default=None,
            help="Index of the chat if None it will get the current conversation.",
        )
        conversation_parser.add_argument(
            "-n", "--new", action="store_true", dest="new", help="Create a new chat"
        )
        conversation_parser.add_argument(
            "-r",
            "--rename",
            dest="rename",
            nargs="?",
            const=True,
            help="Rename the conversation that you are currently. If nothing is specified it will rename the current chat using the llm model",
        )
        conversation_parser.add_argument(
            "-d",
            "--delete",
            action="store_true",
            dest="delete",
            help="Delete the chat that you are currently using in the ask command",
        )
        conversation_parser.set_defaults(func=conversation_handler)

        # Subparser for the 'commit' command
        commit_parser = self.command_parser.add_parser(
            "commit", help="Auto-generate a GitHub commit message and commit changes"
        )
        commit_parser.add_argument(
            "-p",
            "--push",
            dest="push",
            action="store_true",
            help="Push the code to GitHub",
        )
        commit_parser.add_argument(
            "-a",
            "--all",
            dest="all_flag",
            action="store_true",
            help="Stage all the files before committing",
        )
        commit_parser.add_argument(
            "-i",
            "--issues",
            dest="issue_flag",
            action="store_true",
            help="Add issue number in the commit message",
        )
        commit_parser.set_defaults(func=git_commit)

        # Subparser for the 'onboarding' command
        onboarding_parser = self.command_parser.add_parser(
            "onboarding", help="Start the onboarding process"
        )
        onboarding_parser.set_defaults(func=onboarding_command)

        # Subparser for the 'feedback' command
        feedback_parser = self.command_parser.add_parser(
            "feedback", help="Submit feedback"
        )
        feedback_parser.set_defaults(func=feedback)

        # Subparser for the 'contribute' command
        contribute_parser = self.command_parser.add_parser(
            "contribute", help="How to contribute"
        )
        contribute_parser.set_defaults(func=contribute)

        # Subparser for the 'install' command
        install_parser = self.command_parser.add_parser(
            "install", help="Install PiecesOS"
        )
        install_parser.set_defaults(func=lambda **kwargs: PiecesInstaller().run())

        # Subparser for the 'open' command
        open_parser = self.command_parser.add_parser(
            "open", help="Opens PiecesOS or Applet"
        )
        open_parser.add_argument(
            "-p",
            "--pieces_os",
            dest="pos",
            action="store_true",
            help="Opens PiecesOS",
        )
        open_parser.add_argument(
            "-c",
            "--copilot",
            dest="copilot",
            action="store_true",
            help="Opens Pieces Copilot",
        )
        open_parser.add_argument(
            "-d",
            "--drive",
            dest="drive",
            action="store_true",
            help="Opens Pieces Drive",
        )
        open_parser.add_argument(
            "-s",
            "--settings",
            dest="settings",
            action="store_true",
            help="Opens Pieces Settings",
        )
        open_parser.set_defaults(func=open_command)

        mcp_parser = self.command_parser.add_parser(
            "mcp",
            help="setup the MCP server for an integration",
        )

        mcp_parser.set_defaults(func=lambda **kwargs: mcp_parser.print_help())

        mcp_subparser = mcp_parser.add_subparsers(dest="mcp")

        mcp_setup_parser = mcp_subparser.add_parser(
            "setup", help="Sets up a integration"
        )

        mcp_setup_parser.add_argument(
            "--vscode",
            dest="vscode",
            action="store_true",
            help="Set up the MCP for VS Code",
        )
        mcp_setup_parser.add_argument(
            "--globally",
            dest="global",
            action="store_true",
            help="For VS Code or Cursor to set the Global MCP",
        )
        mcp_setup_parser.add_argument(
            "--specific-workspace",
            dest="local",
            action="store_true",
            help="For VS Code or Cursor to set the Local MCP",
        )
        mcp_setup_parser.add_argument(
            "--cursor",
            dest="cursor",
            action="store_true",
            help="Set up the MCP for Cursor",
        )
        mcp_setup_parser.add_argument(
            "--goose",
            dest="goose",
            action="store_true",
            help="Set up the MCP for Goose",
        )
        mcp_setup_parser.set_defaults(func=handle_mcp)

        mcp_list_parser = mcp_subparser.add_parser("list", help="List all MCPs")
        mcp_list_parser.add_argument(
            "--already-registered",
            dest="already_registered",
            action="store_true",
            help="Display the list of the registered MCPs",
        )
        mcp_list_parser.add_argument(
            "--available-for-setup",
            dest="available_for_setup",
            action="store_true",
            help="Display the list of the ready to be registered MCPs",
        )
        mcp_list_parser.set_defaults(func=handle_list)

        mcp_docs_parser = mcp_subparser.add_parser(
            "docs", help="Print the documentations for an integration"
        )
        mcp_docs_parser.add_argument(
            "--ide",
            dest="ide",
            type=str,
            choices=["vscode", "cursor", "goose", "current", "all"],
            default="all",
            help="The IDE to print its documentation",
        )
        mcp_docs_parser.add_argument(
            "--open",
            "-o",
            dest="open",
            action="store_true",
            help="Open the queried docs in the browser",
        )
        mcp_docs_parser.set_defaults(func=handle_mcp_docs)

        mcp_repair_parser = mcp_subparser.add_parser(
            "repair", help="Repair an MCP config settings"
        )
        mcp_repair_parser.add_argument(
            "--ide",
            dest="ide",
            type=str,
            choices=["vscode", "cursor", "goose", "all"],
            default="all",
            help="The IDE to repair",
        )
        mcp_repair_parser.set_defaults(func=handle_repair)

        mcp_setup_parser = mcp_subparser.add_parser(
            "status", help="Show the Status of the LTM and the MCPs"
        )
        mcp_setup_parser.set_defaults(func=handle_status)

    def run(self):
        config = ConfigCommands.load_config()
        Settings.logger = Logger(config.get("debug", False))
        try:
            arg = sys.argv[1]
            if arg == "--ignore-onboarding":
                arg = sys.argv[2]
        except IndexError:  # No command provided
            self.parser.print_help()
            return

        ignore_onboarding = False
        for _arg in sys.argv:
            if _arg == "--ignore-onboarding":
                ignore_onboarding = True

        onboarded = config.get("onboarded", False)

        if (
            not config.get("skip_onboarding", False)
            and not onboarded
            and not ignore_onboarding
        ):
            res = Settings.logger.prompt(
                "It looks like this is your first time using the Pieces CLI."
                "\nWould you like to start onboarding",
                choices=["y", "n", "skip"],
            )
            if res.lower() == "y":
                return onboarding_command()
            elif res.lower() == "skip":
                config["skip_onboarding"] = True
                ConfigCommands.save_config(config)

        # Check if the command needs PiecesOS or not
        if arg not in [
            "help",
            "-v",
            "--version",
            "install",
            "onboarding",
            "feedback",
            "contribute",
            "open",
        ]:
            Settings.startup()

        args = self.parser.parse_args()
        Settings.logger.debug(f"Running command {arg} using: {args}")
        args.func(**vars(args))


def main():
    try:
        cli = PiecesCLI()
        cli.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        Settings.logger.critical(e)
        Settings.show_error("UNKOWN EXCEPTION", e)


if __name__ == "__main__":
    main()
