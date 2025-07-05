import sys
import platform
import shlex
from prompt_toolkit import PromptSession
import os
import subprocess
from typing import List, Tuple
from pieces import __version__
from pieces.gui import welcome, print_instructions, double_space, double_line
from pieces.pieces_argparser import PiecesArgparser
from pieces.settings import Settings


def loop(**kwargs):
    """Run the CLI loop."""
    from pieces._vendor.pieces_os_client.wrapper.websockets.conversations_ws import ConversationWS
    from pieces._vendor.pieces_os_client.wrapper.websockets.assets_identifiers_ws import (
        AssetsIdentifiersWS,
    )

    Settings.run_in_loop = True

    # Start WebSockets
    AssetsIdentifiersWS(Settings.pieces_client).start()
    ConversationWS(Settings.pieces_client).start()

    # Initial setup
    welcome()
    appl = (
        Settings.pieces_client.application.name.value
        if Settings.pieces_client.application
        else "Unknown"
    )
    Settings.logger.print(
        f"Operating System: {platform.platform()}\n",
        f"Python Version: {sys.version.split()[0]}\n",
        f"PiecesOS Version: {Settings.pieces_os_version}\n",
        f"Pieces CLI Version: {__version__}\n",
        f"Application: {appl}",
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


def extract_text(user_input: str) -> Tuple[str, str, List[str]]:
    """Extract command and arguments from user input safely."""
    try:
        command_parts = shlex.split(user_input)
        if not command_parts:
            return user_input, "", []

        command_name = command_parts[0].lower()
        command_args = command_parts[1:]
        return user_input, command_name, command_args
    except ValueError as e:
        # Handle unclosed quotes or other parsing errors
        Settings.logger.error(f"Failed to parse input: {e}")
        # Fallback to simple split
        parts = user_input.split()
        command_name = parts[0].lower() if parts else ""
        command_args = parts[1:] if len(parts) > 1 else []
        return user_input, command_name, command_args


def run_cli(user_input: str, command_name: str, command_args: List[str]):
    """Run the CLI loop, handling user input and routing to the appropriate functions."""
    if user_input.lower() == "clear":
        clear_screen()
        return

    if user_input == "exit":
        from pieces._vendor.pieces_os_client.wrapper.websockets.base_websocket import BaseWebsocket

        double_space("Exiting...")
        BaseWebsocket.close_all()
        Settings.run_in_loop = False
        return True

    if command_name.isdigit():
        command_name = "drive"
        command_args = []

    run_command(user_input, command_name, command_args)


def run_command(user_input: str, command_name: str, command_args: List[str]) -> None:
    """Execute a command with proper error handling."""
    if command_name in ["run", "onboarding"] and Settings.run_in_loop:
        if command_name == "onboarding":
            Settings.logger.print(
                "Cannot run onboarding while in loop mode. Please exit first."
            )
        return

    Settings.logger.debug(
        f"Running {user_input} with {command_name} and {command_args}"
    )

    try:
        # Create a new argument list for the parser
        argv = [command_name] + command_args

        # Parse the arguments using the main parser
        args = PiecesArgparser.parser.parse_args(argv)

        # Execute the command function if it exists
        if hasattr(args, "func"):
            args.func(**vars(args))
        else:
            Settings.logger.print(f"No handler found for command: {command_name}")
            suggest_similar_command(command_name)

    except SystemExit as e:
        # argparse calls sys.exit on error - catch and handle gracefully
        # Settings.logger.print(f"Invalid arguments for command: {command_name}")
        Settings.logger.error(f"Invalid arguments for command: {command_name}, {e}")
    except Exception as e:
        Settings.logger.error(f"Error executing {command_name}: {str(e)}")
        Settings.show_error(f"Command failed: {command_name}", str(e))


def suggest_similar_command(command_name: str) -> None:
    """Suggest a similar command based on user input."""
    Settings.logger.print(f"Unknown command: {command_name}")
    # Get available commands - use public API if available, otherwise fallback
    commands = ["exit"]
    try:
        # Try to get commands from parser if possible
        if (
            hasattr(PiecesArgparser.parser, "_subparsers")
            and PiecesArgparser.parser._subparsers
        ):
            commands.extend(
                list(
                    PiecesArgparser.parser._subparsers._group_actions[0].choices.keys()
                )
            )
    except Exception as e:
        # Fallback to known commands
        Settings.logger.error(f"No commands found, {e}")
        commands.extend(
            ["list", "create", "ask", "search", "help", "clear", "exit", "mcp"]
        )

    # Remove commands that shouldn't be suggested in loop mode
    if Settings.run_in_loop and "run" in commands:
        commands.remove("run")
    if Settings.run_in_loop and "onboarding" in commands:
        commands.remove("onboarding")

    most_similar_command = PiecesArgparser.find_most_similar_command(
        commands, command_name
    )
    Settings.logger.print(f"Did you mean {most_similar_command}")


def clear_screen():
    """Clear the terminal screen safely."""
    if os.name == "nt":
        # Windows
        subprocess.run(["cls"], shell=True, check=False)
    else:
        # Unix/Linux/Mac - use ANSI escape codes
        print("\033[2J\033[H", end="")
