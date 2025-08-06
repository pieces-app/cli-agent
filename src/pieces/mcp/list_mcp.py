from rich.markdown import Markdown

from pieces.headless.models.mcp import MCPListResponse, create_mcp_list_success
from pieces.mcp.integration import Integration
from pieces.settings import Settings

from .handler import supported_mcps


def print_setup_status(integration: Integration, key: str) -> str:
    if integration.is_set_up():
        if integration.need_repair():
            return (
                f"🔨 It looks like {integration} needs to be repaired. "
                f"Use `pieces mcp repair --ide {key}` to repair it."
            )
        return f"✅ {integration} MCP is set up!"

    if not integration.exists():
        return f"ℹ️ {integration} does not exist."

    return (
        f"❌ {integration} MCP is not set up. "
        f"Use `pieces mcp setup {key}` to set it up."
    )


def handle_list(
    available_for_setup: bool = False, already_registered: bool = False, **kwargs
):
    text = []
    for key, integration in supported_mcps.items():
        if not available_for_setup and not already_registered:
            text.append(print_setup_status(integration, key))
        elif already_registered:
            if integration.is_set_up():
                text.append(print_setup_status(integration, key))
        elif available_for_setup:
            if not integration.is_set_up():
                text.append(f"{integration}, Use `pieces mcp setup {key}` to set it up")
    for t in text:
        Settings.logger.print(Markdown(t))


def get_status(integration: Integration):
    if integration.is_set_up():
        if integration.need_repair():
            return "needs_repair"
        return "activated"
    if not integration.exists():
        return "not_found"
    return "available_to_setup"


def handle_list_headless(**kwargs):
    return create_mcp_list_success(
        [
            MCPListResponse(key, get_status(integration))
            for key, integration in supported_mcps.items()
        ]
    )
