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
                if not integration.need_repair():
                    console.print(f"✅ {integration} MCP is set up!")
                else:
                    console.print(
                        Markdown(
                            f"🛠️ it looks like {integration} needs to be repaired use `pieces mcp repair --{key}` to repair"
                        )
                    )
            else:
                console.print(
                    Markdown(
                        f"❌ {integration} MCP is not set up, "
                        f"Use `pieces mcp setup --{key}` to set it up."
                    )
                )
    elif already_registered:
        for key, integration in supported_mcps.items():
            if integration.is_set_up():
                if integration.need_repair():
                    console.print(
                        f"🛠️ it looks like {integration} needs to be repaired use `pieces mcp repair --{key}` to repair"
                    )
                else:
                    console.print(f"✅ {integration} MCP is set up")

    elif available_for_setup:
        for key, integration in supported_mcps.items():
            if not integration.is_set_up():
                console.print(
                    Markdown(
                        f"{integration}, Use `pieces mcp setup --{key}` to set it up"
                    )
                )
