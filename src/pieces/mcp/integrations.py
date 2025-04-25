from queue import Empty
from typing import Literal
import yaml
import platform
import os

from .integration import Integration
from ..settings import Settings

goose_config_path = os.path.expanduser("~/.config/goose/config.yaml")


def get_global_vs_settings():
    system = platform.system()

    if system == "Windows":
        settings_path = os.path.join(
            os.environ["APPDATA"], "Code", "User", "settings.json"
        )
    elif system == "Darwin":  # macOS
        settings_path = os.path.expanduser(
            "~/Library/Application Support/Code/User/settings.json"
        )
    elif system == "Linux":
        settings_path = os.path.expanduser("~/.config/Code/User/settings.json")
    else:
        Settings.show_error(f"Unsupported platform {system}")
        raise ValueError
    return settings_path


def validate_vscode_project(path):
    """Validate that the path is a legitimate VS Code project."""
    if not path or path.isspace():
        return False, ""
    path = os.path.abspath(os.path.expanduser(path))

    # Check if directory exists
    if not os.path.isdir(path):
        return False, "The specified path is not a directory"

    # Check for .vscode folder or specific VS Code files
    vscode_dir = os.path.join(path, ".vscode")
    if not os.path.isdir(vscode_dir):
        return False, "No .vscode directory found - this may not be a VS Code project"

    return True, path


def get_vscode_path(option: Literal["global", "local"] = "global"):
    if option == "global":
        settings_path = get_global_vs_settings()

    elif option == "local":
        path = input("Enter the path to the VS Code project: ")
        is_valid, m = validate_vscode_project(path)

        while not is_valid:
            print(m)
            path = input("Enter a valid path for the VS Code project: ")
            is_valid, m = validate_vscode_project(path)
        settings_path = m

    return settings_path


def get_cursor_path():
    system = platform.system()
    if system == "Darwin":  # macOS
        config_path = os.path.expanduser(
            "~/Library/Application Support/Cursor/User/mcp.json"
        )
    elif system == "Windows":
        config_path = os.path.join(os.environ["APPDATA"], "Cursor", "User", "mcp.json")
    elif system == "Linux":
        config_path = os.path.expanduser("~/.config/Cursor/User/mcp.json")
    else:
        Settings.show_error(f"Unsupported platform {system}")
        raise ValueError

    return config_path


text_success_vscode = """
### Using Pieces LTM in VS Code

1. **Open Copilot Chat:**

       ⌘+Ctrl+I (macOS)
       Ctrl+Alt+I (Windows/Linux)

2. **Switch to Agent Mode**

3. **Ask a prompt:**

       What was I working on yesterday?
       Summarize it with 5 bullet points and timestamps.

> Ensure PiecesOS is running & LTM is enabled
"""

text_success_goose = """
### Using Pieces LTM in Goose

1. **Start a Goose chat:**

       goose

2. **Ask a prompt:**

       What was I working on yesterday?
       Summarize in 5 bullet points with timestamps.

> Ensure PiecesOS is running & LTM is enabled
"""

text_success_cursor = """
### Use Pieces LTM in Cursor

1. Open chat panel: `⌘+i` (Mac) / `Ctrl+i` (Win)
2. Switch to **Agent Mode**
3. Ask a question like:
   > What was I working on yesterday?
4. Click **Use Tool** when prompted

> Ensure PiecesOS is running & LTM is enabled
"""

cursor_integration = Integration(
    options=[],
    text_success=text_success_cursor,
    docs="https://docs.pieces.app/products/mcp/cursor#using-pieces-mcp-server-in-cursor",
    readable="Cursor",
    get_settings_path=get_cursor_path,
    path_to_mcp_settings=["mcp_servers", "Pieces"],
    mcp_settings={},
)
vscode_integration = Integration(
    options=[
        (
            "Global (Set the MCP to run globally for all your projects) ",
            {"option": "global"},
        ),
        ("Local (Set the MCP to run for a specific Project)", {"option": "local"}),
    ],
    text_success=text_success_vscode,
    readable="VS Code",
    docs="https://docs.pieces.app/products/mcp/github-copilot#using-pieces-mcp-server-in-github-copilot",
    get_settings_path=get_vscode_path,
    path_to_mcp_settings=["mcp", "servers", "Pieces"],
    mcp_settings={
        "type": "see",
    },
)
goose_integration = Integration(
    options=[],
    text_success=text_success_goose,
    readable="Goose",
    docs="https://docs.pieces.app/products/mcp/goose#using-pieces-mcp-with-goose",
    get_settings_path=lambda: goose_config_path,
    mcp_settings={
        "bundled": None,
        "description": "Pieces MPC",
        "enabled": True,
        "env_keys": [],
        "envs": {},
        "name": "Pieces",
        "timeout": 300,
        "type": "sse",
    },
    saver=yaml.dump,
    loader=yaml.safe_load,
    path_to_mcp_settings=["extensions", "pieces"],
    url_property_name="uri",
)
