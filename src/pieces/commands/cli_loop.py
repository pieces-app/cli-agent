import sys
import platform
import shlex
from prompt_toolkit import PromptSession
import os
from typing import List
from pieces import __version__
from pieces.gui import welcome, print_instructions, double_space, double_line
from pieces.pieces_argparser import PiecesArgparser
from pieces.settings import Settings


def loop(**kwargs):
    """Run the CLI loop."""
    from pieces.wrapper.websockets.conversations_ws import ConversationWS
    from pieces.wrapper.websockets.assets_identifiers_ws import AssetsIdentifiersWS

    Settings.run_in_loop = True

    # Start WebSockets
    AssetsIdentifiersWS(Settings.pieces_client).start()
    ConversationWS(Settings.pieces_client).start()

    # Initial setup
    welcome()
    appl = Settings.pieces_client.application.name.value if Settings.pieces_client.application else 'Unknown'
    Settings.logger.print(
        f"Operating System: {platform.platform()}\n",
        f"Python Version: {sys.version.split()[0]}\n",
        f"PiecesOS Version: {Settings.pieces_os_version}\n",
        f"Pieces CLI Version: {__version__}\n",
        f"Application: {appl}"
    )
    print_instructions()
    session = PromptSession()
    # Start the loop
    while Settings.run_in_loop:
        try:
            if not Settings.pieces_client.is_pieces_running():
                double_line("Server no longer available. Exiting loop.")
                break

            if run_cli(*add_input(session)):
                break
        except KeyboardInterrupt:
            run_cli("exit", "", [])
            return False


def add_input(session: PromptSession):
    """Add input to the session."""
    while True:
        user_input = session.prompt("User: ").strip()
        if user_input:
            break
    return extract_text(user_input)


def extract_text(user_input):
    command_parts = shlex.split(user_input)
    command_name = command_parts[0].lower()
    command_args = command_parts[1:]
    return user_input, command_name, command_args


def run_cli(user_input: str, command_name: str, command_args: List[str]):
    """Run the CLI loop, handling user input and routing to the appropriate functions."""
    if user_input.lower() == 'clear':
        clear_screen()
        return

    if user_input == 'exit':
        from pieces.wrapper.websockets.base_websocket import BaseWebsocket
        double_space("Exiting...")
        BaseWebsocket.close_all()
        Settings.run_in_loop = False
        return True

    if command_name.isdigit():
        command_name = "drive"
        command_args = []

    run_command(user_input, command_name, command_args)


def run_command(user_input, command_name, command_args):
    if command_name in ["run", "onboarding"] and Settings.run_in_loop:
        if command_name == "onboarding":
            Settings.logger.print("If you want to run the onboarding please exit the run command")
        return # Avoid running multiple instance in the same "loop"
    Settings.logger.debug(f"Running {user_input} with {command_name} and {command_args}")
    # Find the main command first
    if command_name in PiecesArgparser.parser._subparsers._group_actions[0].choices:
        main_parser = PiecesArgparser.parser._subparsers._group_actions[0].choices[command_name]

        if (hasattr(main_parser, '_subparsers') and main_parser._subparsers and 
            command_args and command_args[0] in main_parser._subparsers._group_actions[0].choices):

            subcommand = command_args[0]
            subcommand_args = command_args[1:]
            subparser = main_parser._subparsers._group_actions[0].choices[subcommand]
            command_func = subparser.get_default('func')

            if command_func:
                try:
                    args = subparser.parse_args(subcommand_args)
                    command_func(**vars(args))
                except SystemExit:
                    Settings.logger.print(f"Invalid arguments for subcommand: {command_name} {subcommand}")
                except Exception as e:
                    Settings.show_error(
                        f"Error in subcommand: {command_name} {subcommand}", str(e))
            else:
                Settings.logger.print(f"No function associated with subcommand: {command_name} {subcommand}")
        else:
            # Handle main command with no subcommands
            command_func = main_parser.get_default('func')
            if command_func:
                try:
                    args = main_parser.parse_args(command_args)
                    command_func(**vars(args))
                except SystemExit:
                    Settings.logger.print(f"Invalid arguments for command: {command_name}")
                except Exception as e:
                    Settings.show_error(
                        f"Error in command: {command_name}", str(e))
            else:
                Settings.logger.print(f"No function associated with command: {command_name}")
    else:
        Settings.logger.print(f"Unknown command: {command_name}")
        commands = list(
            PiecesArgparser.parser._subparsers._group_actions[0].choices.keys())
        commands.append("exit")
        commands.remove("run")
        commands.remove("onboarding")
        most_similar_command = PiecesArgparser.find_most_similar_command(
            commands, user_input)
        Settings.logger.print(f"Did you mean {most_similar_command}")


def clear_screen():  # clear terminal method
    if os.name == 'nt':  # for window
        os.system('cls')
    else:               # for other os
        os.system('clear')
