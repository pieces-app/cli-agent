import sys
import platform
from pieces.gui import *
import platform
import sys
import shlex
from prompt_toolkit import PromptSession
from .commands_functions import check, print_instructions, print_response, welcome,ws_manager,parser



def levenshtein_distance(s1, s2):
    # If s1 is shorter than s2, swap them to minimize the number of operations
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    # If one of the strings is empty, the distance is the length of the other string
    if len(s2) == 0:
        return len(s1)

    # Initialize the previous row of distances
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        # Initialize the current row, starting with the deletion distance
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # Calculate the cost of insertions, deletions, and substitutions
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            # Append the minimum cost of the operations to the current row
            current_row.append(min(insertions, deletions, substitutions))
        # Set the current row as the previous row for the next iteration
        previous_row = current_row
    
    # The last element of the previous row contains the levenshtein distance
    return previous_row[-1]


def find_most_similar_command(valid_commands, user_input):
    # Calculate the Levenshtein distance between the user input and each valid command
    distances = {cmd: levenshtein_distance(user_input, cmd) for cmd in valid_commands}
    # Find the command with the smallest Levenshtein distance to the user input
    most_similar_command = min(distances, key=distances.get)
    return most_similar_command

def loop(**kwargs):
    global run_in_loop, parser, pieces_os_version, cli_version, application

    run_in_loop = True


    # Initial setup
    os_info = platform.platform()
    python_version = sys.version.split()[0]

    try:
        os_running, os_version, this_application = check()
        if not os_running:
            raise RuntimeError("Server not running")
    except Exception as e:
        # print(f"Error during startup: {e}")
        sys.exit(1)  # Exit the program

    welcome()

    # Placeholder values
    placeholder_cli_version = "0.1.0"

    pieces_os_version = os_version
    cli_version = placeholder_cli_version
    application = this_application

    print_response(f"Operating System: {os_info}", f"Python Version: {python_version}",
                   f"Pieces OS Version: {pieces_os_version}",
                   f"Pieces CLI Version: {placeholder_cli_version}",
                   f"Application: {application.name.name if application else 'Unknown'}")
    print_instructions()

    # Create a prompt session, which will maintain the history of inputs
    session = PromptSession()

    # Start the loop
    while run_in_loop:
        try:
            is_running, message, application = check()
            if not is_running:
                raise RuntimeError("Server no longer available")
        except Exception as e:
            show_error(f"Error in loop:", {e})
            break

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

            if user_input == 'exit':
                double_space("Exiting...")
                ws_manager.close_websocket_connection()  # Close using the ws_manager instance

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

            if command_name in parser._subparsers._group_actions[0].choices:
                subparser = parser._subparsers._group_actions[0].choices[command_name]
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
                most_similar_command = find_most_similar_command(list(parser._subparsers._group_actions[0].choices.keys()), user_input)
                print(f"Did you mean {most_similar_command}")
        except Exception as e:
            show_error(f"An error occurred:", {e})

        print()
