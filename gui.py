
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
    print("  run     - Starts a looped version of the CLI that only requires you to type the flag")
    print("  list    - List all assets")
    print("  open    - Open an asset")
    print("  save    - Save the current asset")
    print("  version - Gets version of Pieces OS")
    print("  help    - Show this help message")
    print()
