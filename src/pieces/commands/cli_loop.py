import sys
import platform
import shlex
from prompt_toolkit import PromptSession
import os
from pieces import __version__
from pieces.gui import *
from pieces.pieces_argparser import PiecesArgparser
from pieces.settings import Settings


def loop(**kwargs):
    from pieces.wrapper.websockets.base_websocket import BaseWebsocket
    from pieces.wrapper.websockets.conversations_ws import ConversationWS
    from pieces.wrapper.websockets.assets_identifiers_ws import AssetsIdentifiersWS
    
    Settings.run_in_loop = True

    # Start the assets websocket identifiers
    AssetsIdentifiersWS(Settings.pieces_client).start()
    ConversationWS(Settings.pieces_client).start()
    # Initial setup
    os_info = platform.platform()
    python_version = sys.version.split()[0] 
    welcome()

    print_response(f"Operating System: {os_info}", f"Python Version: {python_version}",
                   f"Pieces OS Version: {Settings.pieces_os_version}",
                   f"Pieces CLI Version: {__version__}",
                   f"Application: {Settings.pieces_client.application.name.value if Settings.pieces_client.application else 'Unknown'}")
    print_instructions()

    # Create a prompt session, which will maintain the history of inputs
    session = PromptSession()

    # Start the loop
    while Settings.run_in_loop:
        is_running = Settings.pieces_client.is_pieces_running()

        if not is_running:
            double_line("Server no longer available. Exiting loop.")
            break

        try:
            # Use the session to prompt the user, enabling history navigation
            user_input = session.prompt("User: ").strip()
            command_parts = shlex.split(user_input)
            if command_parts:
                command_name = command_parts[0].lower()  # Lowercase only the command name
                command_args = command_parts[1:]  # Keep the arguments in their original case
            else:
                continue  # Skip if the input is empty
            
            if user_input.lower() == 'clear':  # this method is used for clear a terminal 
                clear_screen()
                continue
            if user_input == 'exit':
                double_space("Exiting...")
                BaseWebsocket.close_all()
                break

            # Check if the input is a number and treat it as an index for 'open' command
            if user_input.isdigit():
                command_name = 'open'
                command_args = [user_input]
            else:
                # Use shlex to split the input into command and arguments
                split_input = shlex.split(user_input)
                if not split_input:
                    continue  # Skip if the input is empty

                command_name, *command_args = split_input

            command_name = command_name.lower()

            if command_name in PiecesArgparser.parser._subparsers._group_actions[0].choices:
                subparser = PiecesArgparser.parser._subparsers._group_actions[0].choices[command_name]
                command_func = subparser.get_default('func')  # Get the function associated with the command

                if command_func:
                    # Parse the arguments using the subparser
                    try:
                        args = subparser.parse_args(command_args)
                        command_func(**vars(args))
                    except SystemExit:
                        # Handle the case where the argument parsing fails
                        print(f"Invalid arguments for command: {command_name}")
                else:
                    print(f"No function associated with command: {command_name}")
            else:
                print(f"Unknown command: {command_name}")
                commands = list(PiecesArgparser.parser._subparsers._group_actions[0].choices.keys())
                commands.append("exit")
                most_similar_command = PiecesArgparser.find_most_similar_command(commands, user_input)
                print(f"Did you mean {most_similar_command}")
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt caught. Returning to the main loop.")
            print("to exit the terminal use : exit")
            continue
        except Exception as e:
            show_error(f"An error occurred:", {e})  #TODO: Handle by the argparser not a try/except


def clear_screen(): # clear terminal method
    if os.name == 'nt': # for window
        os.system('cls')
    else:               # for other os 
        os.system('clear')