from typing import Dict

from ..utils import PiecesSelectMenu
from .integrations import vscode_integration, goose_integration, cursor_integration
from .integration import Integration

# NOTE: the key should be the same as the parameter name in the handle_mcp function
supported_mcps: Dict[str, Integration] = {
    "vscode": vscode_integration,
    "goose": goose_integration,
    "cursor": cursor_integration,
}


def handle_mcp(
    vscode: bool = False,
    cursor: bool = False,
    goose: bool = False,
    **kwargs,
):
    if vscode:
        args = {}
        if kwargs.get("global"):
            args = {"option": "global"}
        elif kwargs.get("local"):
            args = {"option": "local"}
        supported_mcps["vscode"].run(**args)

    if goose:
        supported_mcps["goose"].run()

    if cursor:
        supported_mcps["cursor"].run()

    if not goose and not vscode and not cursor:
        PiecesSelectMenu(
            [(val.readable, {key: True}) for key, val in supported_mcps.items()],
            handle_mcp,
        ).run()
