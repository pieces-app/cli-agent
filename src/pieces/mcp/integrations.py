from typing import Literal
import yaml
import platform
import os
import json

from .integration import Integration, MCPProperties
from ..settings import Settings
from ..urls import URLs

goose_config_path = os.path.expanduser("~/.config/goose/config.yaml")
windsurf_config_path = os.path.expanduser("~/.codeium/windsurf/mcp_config.json")
# TODO: We might need to add local config like vscode and cursor for local projects
# Link: https://zed.dev/docs/configuring-zed#settings-files
zed_config_path = os.path.join(
    os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")),
    "zed",
    "settings.json",
)


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


claude_cli_path = os.path.expanduser("~/.claude.json")


def get_shortwave_path():
    sys = platform.system()

    if sys == "Windows":
        return os.path.join(os.environ["APPDATA"], "Shortwave", "mcp.json")
    elif sys == "Darwin":
        return os.path.expanduser("~/Library/Application Support/Shortwave/mcp.json")
    elif sys == "Linux":
        return os.path.expanduser("~/.config/Shortwave/mcp.json")
    else:
        Settings.show_error(f"Unsupported platform {sys}")
        raise ValueError


def validate_project_path(path, dot_file=".vscode", readable: str = "VS Code"):
    """Validate that the path is a legitimate VS Code or cursor project with security checks."""
    if not path or path.isspace():
        return False, ""

    # Expand user home and convert to absolute path
    abs_path = os.path.abspath(os.path.expanduser(path))

    # Security check: Ensure path doesn't escape allowed directories
    # Allow paths within current working directory or user's home directory
    current_dir = os.getcwd()
    home_dir = os.path.expanduser("~")

    if not (abs_path.startswith(current_dir) or abs_path.startswith(home_dir)):
        return (
            False,
            f"Path '{path}' is outside allowed directories. Projects must be within your home directory or current working directory",
        )

    # Check if directory exists
    if not os.path.isdir(abs_path):
        return False, "The specified path is not a directory"

    # Check for .vscode folder or specific VS Code files
    dot_dir = os.path.join(abs_path, dot_file)
    if not os.path.isdir(dot_dir):
        return (
            False,
            f"No {dot_file} directory found - this may not be a {readable} project",
        )

    return True, dot_dir


def input_local_path(dot_file: str, name: str) -> str:
    path = input(f"Enter the path to the {name} project: ")
    is_valid, m = validate_project_path(path, dot_file, name)

    while not is_valid:
        print(m)
        path = input(f"Enter a valid path for the {name} project: ")
        is_valid, m = validate_project_path(path, dot_file, name)
    settings_path = m

    return settings_path


def get_vscode_path(option: Literal["global", "local"] = "global"):
    if option == "global":
        settings_path = get_global_vs_settings()
    elif option == "local":
        settings_path = input_local_path(".vscode", "VS Code")
        settings_path = os.path.join(
            settings_path, "settings.json"
        )  # Add the settings.json to the settings path to edit
    create_config(settings_path)
    return settings_path


def create_config(path: str):
    # Create the MCP file if not exists
    dir = os.path.dirname(path)
    if os.path.exists(dir) and not os.path.exists(path):
        with open(path, "w") as file:
            json.dump({}, file)


def get_cursor_path(option: Literal["global", "local"] = "global"):
    if option == "global":
        config_path = os.path.expanduser(os.path.join("~", ".cursor", "mcp.json"))
    elif option == "local":
        config_path = input_local_path(".cursor", "Cursor")
        config_path = os.path.join(
            config_path, "mcp.json"
        )  # Add the settings.json to the settings path to edit
    create_config(config_path)

    return config_path


def get_claude_path():
    system = platform.system()

    if system == "Windows":
        settings_path = os.path.join(
            os.environ["APPDATA"], "Claude", "claude_desktop_config.json"
        )
    elif system in "Darwin":
        settings_path = os.path.expanduser(
            "~/Library/Application Support/Claude/claude_desktop_config.json"
        )
    elif system == "Linux":
        settings_path = os.path.expanduser(
            "~/.config/Claude/claude_desktop_config.json"
        )
    else:
        Settings.show_error(f"Unsupported platform {system}")
        raise ValueError

    settings_dir = os.path.dirname(settings_path)
    if os.path.isdir(settings_dir):
        if not os.path.isfile(settings_path):
            with open(settings_path, "w") as f:
                json.dump({}, f, indent=4)  # Create the json file if it does not exists
    return settings_path


text_success_vscode = """
### Using Pieces LTM in VS Code

1. **Open Copilot Chat:**

       ⌘+⌃+I (macOS)
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
3. **Ask a prompt:**

       What was I working on yesterday?
       Summarize it with 5 bullet points and timestamps.

4. Click **Use Tool** when prompted

> Ensure PiecesOS is running & LTM is enabled
"""

text_success_claude = """
### Use Pieces LTM in Claude desktop

1. Open Claude desktop (make sure to restart it if it was running)
2. **Ask a prompt:**

        What I was working on yesterday?
        Summarize it with 5 bullet points and timestamps.

> Ensure PiecesOS is running & LTM is enabled
"""

text_success_zed = """
### Use Pieces LTM in Zed

1. Open Zed
2. **Ask a prompt:**
    What I was working on yesterday?
    Summarize it with 5 bullet points and timestamps.

> Ensure PiecesOS is running & LTM is enabled
"""

text_success_claude_cli = """
### Use Pieces LTM in Claude CLI

1. Open Claude CLI (typing claude in your terminal)
2. **Ask a prompt:**

    claude> What I was working on yesterday?
    claude> Summarize it with 5 bullet points and timestamps

> Ensure PiecesOS is running & LTM is enabled
"""

text_success_windsurf = """
### Use Pieces LTM in Windsurf 

1. Open Windsurf
2. **Ask a prompt:**

        What I was working on yesterday?
        Summarize it with 5 bullet points and timestamps.

> Ensure PiecesOS is running & LTM is enabled
"""

warp_instructions = """
### Use Pieces LTM in Warp

1. From `Settings > AI > Manage MCP servers`

2. Click on the add button

3. Then paste the following Json

```json
{json}
```

> Ensure PiecesOS is running & LTM is enabled
"""

warp_stdio_json = """
{
    "Pieces": {
        "command": "pieces",
        "args": ["mcp", "start"],
        "env": {},
        "working_directory": null,
        "start_on_launch": true
    }
}
"""

warp_sse_json = """
{{
    "Pieces": {{
        "serverUrl": "{url}"
    }}
}}
"""

text_success_short_wave = """
### Use Pieces LTM in Shortwave

1. Restart Shortwave
2. **Ask a prompt:**

        What I was working on yesterday?
        Summarize it with 5 bullet points and timestamps.

> Ensure PiecesOS is running & LTM is enabled
"""

options = [
    (
        "Globally (Set the MCP to run globally for all your workspaces) ",
        {"option": "global"},
    ),
    ("Workspace (Set the MCP to run for a specific workspace)", {"option": "local"}),
]

cursor_integration = Integration(
    options=options,
    text_success=text_success_cursor,
    docs=URLs.CURSOR_MCP_DOCS.value,
    readable="Cursor",
    get_settings_path=get_cursor_path,
    mcp_properties=MCPProperties(
        stdio_property={},
        stdio_path=["mcpServers", "Pieces"],
        sse_path=["mcpServers", "Pieces"],
        sse_property={},
    ),
)
vscode_integration = Integration(
    options=options,
    text_success=text_success_vscode,
    readable="VS Code",
    docs=URLs.VS_CODE_MCP_DOCS.value,
    get_settings_path=get_vscode_path,
    mcp_properties=MCPProperties(
        stdio_property={"type": "stdio"},
        stdio_path=["mcp", "servers", "Pieces"],
        sse_property={"type": "sse"},
        sse_path=["mcp", "servers", "Pieces"],
    ),
)
goose_integration = Integration(
    options=[],
    text_success=text_success_goose,
    readable="Goose",
    docs=URLs.GOOSE_MCP_DOCS.value,
    get_settings_path=lambda: goose_config_path,
    mcp_properties=MCPProperties(
        stdio_property={
            "bundled": None,
            "description": "Pieces for developers MPC stdio",
            "enabled": True,
            "env_keys": [],
            "envs": {},
            "name": "Pieces stdio",
            "timeout": 3000,
            "type": "stdio",
        },
        stdio_path=["extensions", "pieces"],
        sse_property={
            "bundled": None,
            "description": "Pieces for developers MPC",
            "enabled": True,
            "env_keys": [],
            "envs": {},
            "name": "Pieces",
            "timeout": 3000,
            "type": "sse",
        },
        sse_path=["extensions", "pieces"],
        url_property_name="uri",
        command_property_name="cmd",
    ),
    saver=yaml.dump,
    loader=yaml.safe_load,
)

claude_integration = Integration(
    options=[],
    text_success=text_success_claude,
    readable="Claude Desktop",
    get_settings_path=get_claude_path,
    docs=URLs.CLAUDE_MCP_DOCS.value,
    mcp_properties=MCPProperties(
        stdio_property={},
        stdio_path=["mcpServers", "Pieces"],
        sse_path=[
            "mcpServers",
            "Pieces",
        ],  ## SSE Connection is not supported in claude!
        sse_property={},
    ),
    id="claude",
)

windsurf_integration = Integration(
    options=[],
    text_success=text_success_windsurf,
    readable="Windsurf",
    get_settings_path=lambda: windsurf_config_path,
    docs=URLs.WINDSURF_MCP_DOCS.value,
    mcp_properties=MCPProperties(
        stdio_property={},
        stdio_path=["mcpServers", "Pieces"],
        sse_path=[
            "mcpServers",
            "Pieces",
        ],
        sse_property={},
        url_property_name="serverUrl",
    ),
)

zed_integration = Integration(
    options=[],
    text_success=text_success_zed,
    readable="Zed",
    get_settings_path=lambda: zed_config_path,
    docs=URLs.ZED_MCP_DOCS.value,
    mcp_properties=MCPProperties(
        stdio_path=["context_servers", "Pieces", "command"],
        sse_path=["context_servers", "Pieces", "command"],
        sse_property={},
        stdio_property={},
        command_property_name="path",
    ),
    # We might need to add better abstraction for all the MCPs that do not support SSE.
    # As far as I know, SSE is not supported on Zed. We are going to use stdio only like Claude
)

shortwave_integration = Integration(
    options=[],
    text_success=text_success_short_wave,
    readable="Shortwave",
    get_settings_path=get_shortwave_path,
    docs=URLs.SHORT_WAVE_MCP_DOCS.value,
    mcp_properties=MCPProperties(
        stdio_path=["mcpServers", "Pieces"],
        sse_path=["mcp", "Pieces", "command"],
        sse_property={},
        stdio_property={},
    ),
)


claude_cli_integration = Integration(
    options=[],  # TODO: Add local and global options
    text_success=text_success_claude_cli,
    readable="Claude Code",
    docs=URLs.CLAUDE_CLI_MCP_DOCS.value,
    get_settings_path=lambda: claude_cli_path,
    mcp_properties=MCPProperties(
        stdio_path=["mcpServers", "Pieces"],
        sse_path=["mcpServers", "Pieces"],
        sse_property={},
        stdio_property={},
    ),
)
