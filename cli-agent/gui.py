
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

def double_space(text):
    print()
    print(text)
    print()

def print_response(*args):
    for arg in args:
        print(arg)

def print_instructions():
    print()
    print("Enter command:")
    print(f"  'help' to see all commands")
    print(f"  '-h' after a command to see detailed help")
    print(f"  'exit' to quit")
    print()
    print(f"Ready...")
    line()

def print_help():
    print()
    print("Available Commands:")
    print("  run        - Starts a looped version of the CLI that only requires you to type the flag")
    print("  list       - List all assets")
    print("  list x     - Lists maximum of x number of assets")
    print("  list apps  - List all registered applications")
    print("  open       - Opens your current or most recent asset")
    print("  open x     - Open an asset in a list. The CLI must be running")
    print(f"  save       - Save the current asset (not currently functional)")
    print("  delete     - Deletes the current or most recent asset")
    print("  delete x   - Deletes an asset in a list. The CLI must be running")
    print("  create     - Creates a new asset based on what you've copied to your clipboard")
    print("  version    - Gets version of Pieces OS")
    print("  help       - Show this help message")
    print()

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
