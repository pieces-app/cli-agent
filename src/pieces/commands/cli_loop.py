import sys
import platform
import shlex
from prompt_toolkit import PromptSession
import os
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
    print(
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
            run_cli("exit", "", "")
            return False


def add_input(session: PromptSession):
    """Add input to the session."""
    user_input = session.prompt("User: ").strip()
    if not user_input:
        return
    return extract_text(user_input)


def extract_text(user_input):
    command_parts = shlex.split(user_input)
    command_name = command_parts[0].lower()
    command_args = command_parts[1:]
    return user_input, command_name, command_args


def run_cli(user_input: str, command_name: str, command_args: str):
    """Run the CLI loop, handling user input and routing to the appropriate functions."""
    if user_input.lower() == 'clear':
        clear_screen()
        return

    if user_input == 'exit':
        from pieces.wrapper.websockets.base_websocket import BaseWebsocket
        double_space("Exiting...")
        BaseWebsocket.close_all()
        return True

    if command_name.isdigit():
        command_name = 'list'
        command_args = [command_name, "materials"]

    run_command(user_input, command_name, command_args)


def run_command(user_input, command_name, command_args):
    if command_name in PiecesArgparser.parser._subparsers._group_actions[0].choices:
        subparser = PiecesArgparser.parser._subparsers._group_actions[0].choices[command_name]
        command_func = subparser.get_default('func')
        if command_func:
            try:
                args = subparser.parse_args(command_args)
                command_func(**vars(args))
            except SystemExit:
                print(f"Invalid arguments for command: {command_name}")
            except Exception as e:
                Settings.show_error(
                    f"Error in command: {command_name}", str(e))
        else:
            print(f"No function associated with command: {command_name}")
    else:
        print(f"Unknown command: {command_name}")
        commands = list(
            PiecesArgparser.parser._subparsers._group_actions[0].choices.keys())
        commands.append("exit")
        most_similar_command = PiecesArgparser.find_most_similar_command(
            commands, user_input)
        print(f"Did you mean {most_similar_command}")


def clear_screen():  # clear terminal method
    if os.name == 'nt':  # for window
        os.system('cls')
    else:               # for other os
        os.system('clear')
