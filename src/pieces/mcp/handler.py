import json
import time
import urllib.parse
import urllib.request
import webbrowser
from typing import Dict, Literal, Union, cast

from rich.markdown import Markdown

from pieces.headless.models.base import (
    BaseResponse,
    ErrorCode,
    ErrorResponse,
)
from pieces.headless.models.mcp import (
    MCPRepairResult,
    create_mcp_repair_success,
    create_mcp_setup_success,
)
from pieces.mcp.utils import get_mcp_latest_url
from pieces.settings import Settings
from pieces.urls import URLs

from ..utils import PiecesSelectMenu
from .integration import Integration
from pieces.config.schemas.mcp import mcp_integration_types
from .integrations import (
    claude_cli_integration,
    claude_integration,
    cursor_integration,
    goose_integration,
    shortwave_integration,
    validate_project_path,
    vscode_integration,
    kiro_integration,
    warp_instructions,
    warp_sse_json,
    warp_stdio_json,
    windsurf_integration,
    zed_integration,
)

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
    "kiro": kiro_integration,
}


def check_mcp_running():
    try:
        with urllib.request.urlopen(get_mcp_latest_url(), timeout=1) as response:
            for line in response:
                message = line.decode("utf-8").strip()
                if message:
                    break
    except Exception as e:
        Settings.show_error(f"Pieces MCP server is not running {e}")
        return False
    return True


def handle_mcp(
    integration: Union[mcp_integration_types, Literal["raycast", "warp"], None],
    stdio: bool = False,
    **kwargs,
) -> BaseResponse:
    if not check_mcp_running():
        return ErrorResponse(
            "mcp setup",
            ErrorCode.MCP_SERVER_NOT_RUNNING,
            "The stdio or SSE connection to the Pieces MCP server is not available. Please restart PiecesOS.",
        )

    if integration == "raycast":
        if not stdio:
            Settings.logger.print(
                "[yellow]Warning: Using stdio instead of sse because sse connection is not supported"
            )
        handle_raycast()
        return create_mcp_setup_success(
            integration,
            None,
            "Follow the Raycast deeplink to set up Pieces MCP integration.",
            "stdio",
        )
    elif integration == "warp":
        jsn = (
            warp_stdio_json if stdio else warp_sse_json.format(url=get_mcp_latest_url())
        )
        text = warp_instructions.format(json=jsn)
        Settings.logger.print(Markdown(text))
        return create_mcp_setup_success(
            integration, None, text, "stdio" if stdio else "sse"
        )

    integration_instance = supported_mcps[integration] if integration else None
    if integration_instance is None or integration is None:
        menu = [
            (val.readable, {"integration": key, "stdio": stdio})
            for key, val in supported_mcps.items()
            if val.exists()
        ]
        menu.append(
            ("Raycast", {"integration": "raycast", "stdio": stdio})
        )  # append raycast
        menu.append(("Warp", {"integration": "warp", "stdio": stdio}))  # append warp
        return PiecesSelectMenu(
            menu,
            handle_mcp,
        ).run()  # type: ignore[reportReturnType]

    args = {}
    # Run the setup and check if it was successful
    if integration in ["vscode", "cursor"]:
        # Getting the args
        if kwargs.get("local"):
            args = {"option": "local"}
            local_workspace = kwargs.get("local")
            if isinstance(local_workspace, str) and integration:
                dot_file = ".cursor" if integration == "cursor" else ".vscode"
                readable = "Cursor" if integration == "cursor" else "VS Code"
                validate_path, message = validate_project_path(
                    local_workspace,
                    dot_file=dot_file,
                    readable=readable,
                )
                if not validate_path:
                    Settings.logger.print(message)
                    return ErrorResponse(
                        "mcp setup",
                        ErrorCode.INVALID_PATH,
                        "Invalid project path provided.",
                    )
                args["mcp_path"] = message

        elif kwargs.get("global") or Settings.headless_mode:
            args = {"option": "global"}

        success = integration_instance.run(stdio, **args)
    else:
        success = integration_instance.run(stdio)

    if success:
        stdio_text = "stdio" if stdio else "sse"
        if not integration_instance.support_sse:
            stdio_text = "stdio"
        return create_mcp_setup_success(
            integration,
            args.get("mcp_path") or integration_instance.get_settings_path(**args),
            integration_instance.text_end,
            stdio_text,
            location_type=cast(
                Literal["local", "global"], args.get("option", "global")
            ),
        )
    else:
        return ErrorResponse(
            "mcp setup",
            ErrorCode.MCP_SETUP_FAILED,
            integration_instance.error_text,
        )


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
    Settings.logger.print("Deeplink opened follow up in Raycast")


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
        readable = "Warp"
        docs = URLs.WARP_MCP_DOCS.value
    else:
        integration = supported_mcps[ide]
        readable = integration.readable
        docs = integration.docs_no_css_selector
    Settings.logger.print(Markdown(f"**{readable}**: `{docs}`"))
    if kwargs.get("open"):
        URLs.open_website(docs)


def handle_repair(
    ide: Union[mcp_integration_types, Literal["all"]], **kwargs
) -> BaseResponse:
    """
    Repair MCP configuration for a specific IDE or all IDEs.

    Args:
        ide: The IDE to repair or 'all' to repair all IDEs
        **kwargs: Additional arguments

    Returns:
        BaseResponse in headless mode, None otherwise
    """
    repair_results = []

    def repair_single_integration(
        integration_name: mcp_integration_types,
    ) -> MCPRepairResult:
        try:
            integration = supported_mcps[integration_name]
            needs_repair = integration.need_repair()

            if needs_repair:
                integration.repair()
                return MCPRepairResult(
                    integration_name=integration_name,
                    status="repaired",
                    configuration_path=integration.get_settings_path(),
                )
            else:
                return MCPRepairResult(
                    integration_name=integration_name,
                    status="healthy",
                    configuration_path=integration.get_settings_path(),
                )

        except Exception as e:
            error_msg = str(e)
            if Settings.headless_mode:
                raise e
            else:
                Settings.logger.error(
                    f"Failed to repair {integration_name}: {error_msg}"
                )
                Settings.show_error(f"Failed to repair {integration_name}: {error_msg}")
                return MCPRepairResult(
                    integration_name=integration_name,
                    status="failed",
                    configuration_path=None,
                )

    if ide == "all":
        for integration_name in supported_mcps:
            result = repair_single_integration(integration_name)
            repair_results.append(result)
    else:
        result = repair_single_integration(ide)
        repair_results.append(result)

    # In interactive mode, just print summary
    total = len(repair_results)
    repaired = len([r for r in repair_results if r.status == "repaired"])
    healthy = len([r for r in repair_results if r.status == "healthy"])
    failed = len([r for r in repair_results if r.status == "failed"])

    if total > 1:
        Settings.logger.print("\nRepair Summary:")
        Settings.logger.print(f"Total integrations checked: {total}")
        if repaired > 0:
            Settings.logger.print(f"[green]Repaired: {repaired}[/green]")
        if healthy > 0:
            Settings.logger.print(f"[blue]Already healthy: {healthy}[/blue]")
        if failed > 0:
            Settings.logger.print(f"[red]Failed: {failed}[/red]")
    return create_mcp_repair_success(repair_results)


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
                _default=True,
            )
            if response:
                handle_repair(key)

    time.sleep(1)
    Settings.logger.print("[bold green]All integrations are checked[/bold green]")
