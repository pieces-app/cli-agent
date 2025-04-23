import json
import os
import platform
from ..settings import Settings


def handle_cursor():
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

    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            current_config = json.load(f)
    else:
        current_config = {}

    if "mcpServers" not in current_config:
        current_config["mcpServers"] = {}

    current_config["mcpServers"]["Pieces"] = {
        "url": "http://localhost:39300/model_context_protocol/2024-11-05/sse"
    }

    try:
        with open(config_path, "w") as f:
            json.dump(current_config, f, indent=2)
        print(f"Successfully updated {config_path} with Pieces configuration")
    except Exception as e:
        print("Error writing cursor config")
        raise e
