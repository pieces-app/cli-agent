from typing import Dict, Literal, Union, cast
from rich.markdown import Markdown
import urllib.request
import time

from pieces.mcp.utils import get_mcp_latest_url
from pieces.settings import Settings

from pieces.utils import PiecesSelectMenu
from .integrations import (
    vscode_integration,
    goose_integration,
    cursor_integration,
    claude_integration,
    mcp_integration_types,
)
from .integration import Integration

# NOTE: the key should be the same as the parameter name in the handle_mcp function
supported_mcps: Dict[mcp_integration_types, Integration] = {
    "vscode": vscode_integration,
    "goose": goose_integration,
    "cursor": cursor_integration,
    "claude": claude_integration,
}


def handle_mcp(
    vscode: bool = False,
    cursor: bool = False,
    goose: bool = False,
    claude: bool = False,
    stdio: bool = False,
    **kwargs,
):
    # Let's check for the MCP server to see if it is running
    try:
        with urllib.request.urlopen(get_mcp_latest_url(), timeout=1) as response:
            for line in response:
                message = line.decode("utf-8").strip()
                if message:
                    break
    except Exception as e:
        Settings.show_error(f"Pieces MCP server is not running {e}")
        return

    # Getting the args
    args = {}
    if kwargs.get("global"):
        args = {"option": "global"}
    elif kwargs.get("local"):
        args = {"option": "local"}

    if vscode:
        supported_mcps["vscode"].run(stdio, **args)

    if goose:
        supported_mcps["goose"].run(stdio)

    if cursor:
        supported_mcps["cursor"].run(stdio, **args)

    if claude:
        if not stdio:
            Settings.logger.print(
                "[yellow]Warning: Using stdio instead of sse because sse connection is not supported"
            )
        supported_mcps["claude"].run(stdio=True)

    if not any([claude, cursor, vscode, cursor, goose]):
        PiecesSelectMenu(
            [(val.readable, {key: True}) for key, val in supported_mcps.items()],
            handle_mcp,
        ).run()


def handle_mcp_docs(
    ide: Union[mcp_integration_types, Literal["all", "current"]], **kwargs
):
    if ide == "all" or ide == "current":
        for mcp_name, mcp_integration in supported_mcps.items():
            if ide == "current" and not mcp_integration.is_set_up():
                continue
            handle_mcp_docs(mcp_name, **kwargs)
        return
    integration = supported_mcps[ide]
    Settings.logger.print(
        Markdown(f"**{integration.readable}**: `{integration.docs_no_css_selector}`")
    )
    if kwargs.get("open"):
        Settings.open_website(integration.docs_no_css_selector)


def handle_repair(ide: Union[mcp_integration_types, Literal["all"]], **kwargs):
    if ide == "all":
        [handle_repair(integration) for integration in supported_mcps]
        return
    supported_mcps[ide].repair()


def handle_status(**kwargs):
    if supported_mcps["vscode"].check_ltm():
        Settings.logger.print("[green]LTM running[/green]")
    else:
        Settings.logger.print("[red]LTM is not running[/red]")
        return  # Do you we need to check the rest of integration if the ltm is not running?

    Settings.logger.print("[bold]Checking integration[/bold]")

    for key, integration in supported_mcps.items():
        if integration.need_repair():
            response = Settings.logger.confirm(
                f"[yellow]{integration.readable} needs to be repaired. Do you want to repair it?[/yellow]",
            )
            if response:
                handle_repair(cast(Literal["vscode", "goose", "cursor"], key))

    time.sleep(1)
    Settings.logger.print("[bold green]All integrations are checked[/bold green]")
