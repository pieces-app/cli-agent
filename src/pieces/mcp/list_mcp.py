from rich.console import Console
from rich.markdown import Markdown
from typing import List

from .integration import Integration
from .integrations import vscode_inetgration, cursor_inetgration, goose_integration


integrations: List[Integration] = [
    vscode_inetgration,
    cursor_inetgration,
    goose_integration,
]


def handle_list(
    available_for_setup: bool = False, already_registered: bool = False, **kwargs
):
    console = Console()
    if not available_for_setup and not already_registered:
        for integration in integrations:
            if integration.is_setted_up():
                console.print(f"✅ {integration} MCP is setted!")
            else:
                console.print(
                    Markdown(
                        f"❌ {integration} MCP is not setted\n"
                        f"Use `pieces mcp setup --{integration}` to set it up."
                    )
                )
    elif already_registered:
        for integration in integrations:
            if integration.is_setted_up():
                console.print(integration)
    elif available_for_setup:
        for integration in integrations:
            if not integration.is_setted_up():
                console.print(
                    Markdown(
                        f"{integration} use `pieces mcp setup --{integration}` to set it up"
                    )
                )
