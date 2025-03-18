from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from pieces.wrapper.basic_identifier.asset import BasicAsset


def welcome():
    print()
    print("############################")
    print()
    print("Pieces CLI Started")
    print()
    print("############################")
    print()


def line():
    print()
    print("############################")
    print()


def double_line(text):
    print()
    print("############################")
    print()
    print(text)
    print()
    print("############################")
    print()


def server_startup_failed():
    print()
    print("############################")
    print()
    print("Please make sure PiecesOS is running (\"pieces open\") and up-to-date")
    print()
    print("Or, to install PiecesOS, use the \"pieces install\" command")
    print()
    print("############################")
    print()


def print_version_details(pos_version, cli_version):
    print(f"PiecesOS Version: {pos_version}")
    print(f"CLI Version: {cli_version}")


def print_pieces_os_link():
    print("https://docs.pieces.app/products/meet-pieces/fundamentals")


def double_space(text):
    print()
    print(text)
    print()


def space_below(text):
    print(text)
    print()


def print_instructions():
    print()
    print("Enter command:")
    print("  'help' to see all commands")
    print("  '-h' after a command to see detailed help")
    print("  'exit' to quit")
    print()
    print("Ready...")
    line()


def print_help():
    print()
    print("Available Commands:")
    print("  run               - Starts a looped version of the CLI that only requires you to type the flag")
    print()
    print("  list              - Lists all the materials in your Pieces Drive (alias: 'drive')")
    print("  list apps         - List all registered applications")
    print("  list models       - List all registered AI models and change the AI model that you are using the ask command")
    print()
    print("  modify            - Modify the current material content after you edit it in the editor")
    print("  edit              - Edit the current material name or classification you can use -n and -c for name and classification respectively")
    print("  delete            - Deletes the current or most recent material.")
    print("  create            - Creates a new material based on what you've copied to your clipboard")
    print("  execute           - Execute a Pieces bash material")
    print("  clear             - to clear the terminal")
    print()
    print("  config            - View current configuration")
    print("  config --editor x - Set the editor to 'x' in the configuration")
    print()
    print("  ask \"ask\"       - Asks a single question to the model selected in change model. Default timeout set to 10 seconds")
    print("  --materials,-m    - Add material(s) by index. Separate materials with spaces. Run 'drive' to find material indexes")
    print("  --file,-f         - Add a certain files or folders to the ask command it can be absolute or relative path")
    print()
    print("  chats             - List all the chats. The green chat shows the currently using one in the ask command")
    print("  chat              - Show the messages of the currently using chat in the ask command")
    print("  chat x            - List all the messages in a certain chat and switch to it in the ask command")
    print("  -n,--new          - To create a new chat in the ask command")
    print("  -d,--delete       - Deletes the current chat")
    print("  -r,--rename       - Rename the current chat. If no value given it will let the model rename it for you")
    print()
    print("  commit            - Commits the changes to github and auto generate the message, you can use -p or --push to push")
    print()
    print("  search q          - Does a fuzzy search for your query")
    print("  --mode ncs        - Does a neural code search for your query")
    print("  --mode fts        - Does a full text search for your query")
    print()
    print("  login             - Login to pieces")
    print("  logout            - Logout from pieces")
    print()
    print("  version           - Gets version of PiecesOS and the version of the cli tool")
    print("  help              - Show this help message")
    print("  onboarding        - Start the onboarding process")
    print("  feedback          - Send feedback to Pieces")
    print("  contribute        - Contribute to Pieces CLI")
    print("  install           - Install PiecesOS")
    print("  open              - Opens PiecesOS")
    print()


def print_asset_details(asset: "BasicAsset"):
    print(f"Name: {asset.name}")
    print(f"Created: {asset.created_at}")
    print(f"Updated: {asset.updated_at}")
    print(f"Type: {asset.type.value}")
    print(f"Language: {asset.classification.value}")
    print()


def delete_most_recent():
    print("This is your most recent material. Are you sure you want to delete it? This action cannot be undone.")
    print("type 'delete' to confirm")


def no_assets_in_memory():
    print()
    print("No material is Currently Saved in Memory")
    print("Please choose from the list or use 'find'")
    print()


def open_from_command_line():
    print()
    print("No active search results or lists open")
    print("or you typed an invalid option.")
    print()
    print("Opening most recent material:")
    print()


def deprecated(command, instead):
    """
    Decorator
        command(str): which is the command that is deprated
        instead(str): which command should we use instead
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if kwargs.get("show_warning", True):
                print(f"\033[93m WARNING: `{command}` is deprecated and will"
                      f" be removed in later versions\nPlease use `{instead}` instead \033[0m")
            func(*args, **kwargs)
        return wrapper
    return decorator
