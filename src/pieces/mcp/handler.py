from typing import Dict, Literal, Union, cast
from rich.markdown import Markdown
import urllib.request
import time
import json
import urllib.parse
import webbrowser

from pieces.mcp.utils import get_mcp_latest_url
from pieces.settings import Settings
from pieces.urls import URLs

from ..utils import PiecesSelectMenu
from .integrations import (
    vscode_integration,
    goose_integration,
    cursor_integration,
    claude_integration,
    windsurf_integration,
    zed_integration,
    shortwave_integration,
    claude_cli_integration,
    warp_instructions,
    warp_sse_json,
    warp_stdio_json,
)
from .integration import Integration, mcp_integration_types

# NOTE: the key should be the same as the parameter name in the handle_mcp function
supported_mcps: Dict[mcp_integration_types, Integration] = {
    "vscode": vscode_integration,
    "goose": goose_integration,
    "cursor": cursor_integration,
    "claude": claude_integration,
    "windsurf": windsurf_integration,
    "zed": zed_integration,
    "shortwave": shortwave_integration,
    "claude_code": claude_cli_integration,
}


def handle_mcp(
    vscode: bool = False,
    cursor: bool = False,
    goose: bool = False,
    claude: bool = False,
    zed: bool = False,
    windsurf: bool = False,
    raycast: bool = False,
    warp: bool = False,
    shortwave: bool = False,
    claude_code: bool = False,
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

    if claude or zed or raycast or claude_code or shortwave:
        if not stdio:
            Settings.logger.print(
                "[yellow]Warning: Using stdio instead of sse because sse connection is not supported"
            )
        if raycast:
            handle_raycast()
            return
        if claude:
            mcp = "claude"
        elif zed:
            mcp = "zed"
        elif claude_code:
            mcp = "claude_code"
        elif shortwave:
            mcp = "shortwave"
        else:
            return
        supported_mcps[mcp].run(stdio=True)
        return

    if windsurf:
        supported_mcps["windsurf"].run(stdio)

    if warp:
        jsn = (
            warp_stdio_json if stdio else warp_sse_json.format(url=get_mcp_latest_url())
        )
        text = warp_instructions.format(json=jsn)
        Settings.logger.print(Markdown(text))

    if not any(
        [claude, cursor, vscode, goose, zed, windsurf, raycast, warp, shortwave]
    ):
        menu = [
            (val.readable, {key: True, "stdio": stdio})
            for key, val in supported_mcps.items()
        ]
        menu.append(("Raycast", {"raycast": True, "stdio": stdio}))  # append raycast
        menu.append(("Warp", {"warp": True, "stdio": stdio}))  # append warp
        PiecesSelectMenu(
            menu,
            handle_mcp,
        ).run()


def handle_raycast():
    config = {
        "name": "Pieces",
        "type": "stdio",
        "command": "pieces",
        "args": ["mcp", "start"],
    }
    config_json = json.dumps(config)
    encoded_config = urllib.parse.quote(config_json)
    raycast_url = f"raycast://mcp/install?{encoded_config}"
    webbrowser.open(raycast_url)
    print("Deeplink opened follow up in Raycast")


def handle_mcp_docs(
    ide: Union[mcp_integration_types, Literal["all", "current", "raycast", "warp"]],
    **kwargs,
):
    if ide == "all" or ide == "current":
        for mcp_name, mcp_integration in supported_mcps.items():
            if ide == "current" and not mcp_integration.is_set_up():
                continue
            handle_mcp_docs(mcp_name, **kwargs)
        return
    if ide == "raycast":
        readable = "Raycast"
        docs = URLs.RAYCAST_MCP_DOCS.value
    elif ide == "warp":
        readable = "Wrap"
        docs = URLs.WRAP_MCP_DOCS.value
    else:
        integration = supported_mcps[ide]
        readable = integration.readable
        docs = integration.docs_no_css_selector
    Settings.logger.print(Markdown(f"**{readable}**: `{docs}`"))
    if kwargs.get("open"):
        URLs.open_website(docs)


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
