from rich.console import Console
from rich.markdown import Markdown

from .handler import supported_mcps


def handle_list(
    available_for_setup: bool = False, already_registered: bool = False, **kwargs
):
    console = Console()
    if not available_for_setup and not already_registered:
        for key, integration in supported_mcps.items():
            if integration.is_set_up():
                console.print(f"✅ {integration} MCP is set up!")
            else:
                console.print(
                    Markdown(
                        f"❌ {integration} MCP is not set up\n"
                        f"Use `pieces mcp setup --{key}` to set it up."
                    )
                )
    elif already_registered:
        for integration in supported_mcps.values():
            if integration.is_set_up():
                console.print(integration)
    elif available_for_setup:
        for key, integration in supported_mcps.items():
            if not integration.is_set_up():
                console.print(
                    Markdown(
                        f"{integration}, Use `pieces mcp setup --{key}` to set it up"
                    )
                )
