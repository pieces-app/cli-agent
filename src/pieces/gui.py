
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
    print("Please start your Pieces OS Server")
    print()
    print("Or to install pieces OS: ")
    print("https://docs.pieces.app/installation-getting-started/what-am-i-installing")
    print()
    print("############################")
    print()

def double_space(text):
    print()
    print(text)
    print()

def space_below(text):
    print(text)
    print()

def print_response(*args):
    for arg in args:
        print(arg)
        
def print_asset_details(asset_details, title, search_type):
    # Map search_type to descriptive text
    search_type_map = {
        'ncs': 'Neural Code Search',
        'fts': 'Full Text Search',
        'assets': 'Fuzzy Search'
    }
    search_type_text = search_type_map.get(search_type, 'Search')

    print(f"\n{search_type_text}\n")
    print(title)
    for index, (_, asset_name) in enumerate(asset_details, start=1):
        print(f"{index}: {asset_name}")
    print()


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
    print("  run          - Starts a looped version of the CLI that only requires you to type the flag")
    print()
    print("  list         - List all assets")
    print("  list x       - Lists maximum of x number of assets")
    print("  list apps    - List all registered applications")
    print("  list models  - List all registered AI models")
    print()
    print("  open         - Opens your current or most recent asset")
    print("  open x       - Open an asset in a list. The CLI must be running")
    print("  save         - Save the current asset (not currently functional)")
    print("  delete       - Deletes the current or most recent asset.")
    print("  create       - Creates a new asset based on what you've copied to your clipboard")
    print()
    print("  ask \"ask\"    - Asks a single question to GPT 3.5 for now. Default timeout set to 10 seconds")
    print()
    print("  search q     - Does a fuzzy search for your query")
    print("  --mode ncs   - Does a neural code search for your query")
    print("  --mode fts   - Does a full text search for your query")
    print("               - Example search openai --type ncs")
    print()
    print("  version      - Gets version of Pieces OS")
    print("  help         - Show this help message")
    print()

def print_model_details(name, created_readable, updated_readable, type, language, code_snippet):
    print(f"Name: {name}")
    print(f"Created: {created_readable}")
    print(f"Updated: {updated_readable}")
    print(f"Type: {type}")
    print(f"Language: {language}")
    print(f"Code: {code_snippet}")
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
