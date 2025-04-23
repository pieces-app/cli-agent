import os
import json
import platform
from typing import Literal

from pieces.settings import Settings


def handle_vscode(option: Literal["global", "local"]):
    if option == "global":
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
    elif option == "local":
        path = input("Enter the path to the VS Code project: ")
        path = os.path.abspath(os.path.expanduser(path))

        while not os.path.exists(path):
            print("Invalid Path: The directory does not exist")
            path = input("Enter a valid path for the VS Code project: ")
            path = os.path.abspath(os.path.expanduser(path))

        settings_path = os.path.join(path, ".vscode", "settings.json")

    try:
        with open(settings_path, "r") as f:
            settings = json.load(f)
    except FileNotFoundError:
        settings = {}
    except json.JSONDecodeError:
        print("Error parsing settings.json - it may be malformed")
        raise ValueError
    servers = settings.get("mcp", {}).get("servers", {})
    servers["Pieces"] = {
        "type": "see",
        # TODO: @bishoy-at-pieces Update the sdks to get access to the MCP API
        "url": "http://localhost:39300/model_context_protocol/2024-11-05/sse",
    }
    settings["mcp"] = settings.get("mcp", {})
    settings["mcp"]["servers"] = servers
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=4)
