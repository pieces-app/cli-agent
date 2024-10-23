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
    print("Please make sure Pieces OS is running and up-to-date")
    print()
    print("Or, to install Pieces OS, please visit this link:")
    print_pieces_os_link()
    print()
    print("############################")
    print()


def print_version_details(pos_version,cli_version):
    print(f"Pieces OS Version: {pos_version}")
    print(f"CLI Version: {cli_version}")

def print_pieces_os_link():
    print("https://docs.pieces.app/installation-getting-started/what-am-i-installing")


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
    print("  run             - Starts a looped version of the CLI that only requires you to type the flag")
    print()
    print("  list            - Lists all the assets that the user have")
    print("  list apps       - List all registered applications")
    print("  list models     - List all registered AI models")
    print()
    print("  save            - Save the current asset content after you edit it in the editor")
    print("  edit            - Edit the current asset name or classification you can use -n and -c for name and classification respectively")
    print("  delete          - Deletes the current or most recent asset.")
    print("  create          - Creates a new asset based on what you've copied to your clipboard")
    print("  execute         - Execute a Pieces bash snippet")
    print("  clear           - to clear the terminal")
    print()
    print("  config          - View current configuration")
    print("  config editor=x - Set the editor to 'x' in the configuration")
    print()
    print("  ask \"ask\"       - Asks a single question to the model selected in change model. Default timeout set to 10 seconds")
    print("  --snippets,-s   - Add a certain snippet or snippets using the index check list assets command to the ask command")
    print("  --file,-f       - Add a certain files or folders to the ask command it can be absolute or relative path")
    print()
    print("  conversations   - List all the conversations. The green conversation shows the currently using one in the ask command")
    print("  conversation    - Show the messages of the currently using conversation in the ask command")
    print("  conversation x  - List all the messages in a certain conversation and switch to it in the ask command")
    print("  -n,--new        - To create a new conversation in the ask command")
    print("  -d,--delete     - Deletes the current conversation")
    print("  -r,--rename     - Rename the current conversation. If no value given it will let the model rename it for you")
    print()
    print("  commit          - Commits the changes to github and auto generate the message, you can use -p or --push to push")
    print()
    print("  search q        - Does a fuzzy search for your query")
    print("  --mode ncs      - Does a neural code search for your query")
    print("  --mode fts      - Does a full text search for your query")
    print("                  - Example search openai --type ncs")
    print()
    print("  Login           - Login to pieces")
    print("  Logout          - Logout from pieces")
    print()
    print("  version         - Gets version of Pieces OS and the version of the cli tool")
    print("  help            - Show this help message")
    print("  onboarding      - Start the onboarding process")
    print("  feedback        - Send feedback to Pieces")
    print("  contribute      - Contribute to Pieces CLI")
    print("  install         - Install Pieces OS")
    print()

def print_asset_details(asset:"BasicAsset"):
    print(f"Name: {asset.name}")
    print(f"Created: {asset.created_at}")
    print(f"Updated: {asset.updated_at}")
    print(f"Type: {asset.type.value}")
    print(f"Language: {asset.classification.value}")
    print()

def delete_most_recent():
    print("This is your most recent asset. Are you sure you want to delete it? This action cannot be undone.")
    print("type 'delete' to confirm")

def no_assets_in_memory():
    print()
    print("No Asset is Currently Saved in Memory")
    print("Please choose from the list or use 'find'")
    print()

def open_from_command_line():
    print()
    print("No active search results or lists open")
    print("or you typed an invalid option.")
    print()
    print("Opening most recent asset:")
    print()

def deprecated(command,instead):
    """
    Decorator
        command(str): which is the command that is deprated
        instead(str): which command should we use instead
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if kwargs.get("show_warning",True):
                print(f"\033[93m WARNING: `{command}` is deprecated and will be removed in later versions\nPlease use `{instead}` instead \033[0m")
            func(*args,**kwargs)
        return wrapper
    return decorator
