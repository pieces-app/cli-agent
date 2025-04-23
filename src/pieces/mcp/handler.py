from typing import Callable, List, Literal, Tuple, Optional
from rich.console import Console
from rich.markdown import Markdown

from ..utils import PiecesSelectMenu

from .vscode import handle_vscode
from .gooose import handle_goose
from .cursor import handle_cursor


class Integration:
    def __init__(
        self,
        fn: Callable,
        options: List[Tuple],
        text_success: str,
        readable: str,
        docs: str,
        error_text: Optional[str] = None,
    ) -> None:
        self.fn = fn
        self.options = options
        self.text_end = text_success
        self.readable = readable
        self.error_text = error_text or (
            "Something went wrong. "
            f"Please refer to the documentation: `{docs.split('#')[0]}`" # remove the css selector
        )
        self.docs = docs

    def run(self, **kwargs):
        console = Console()
        try:
            if self.options and not kwargs:
                PiecesSelectMenu(self.options, self.fn).run()
            else:
                self.fn(**kwargs)

            console.print(
                Markdown(f"✅ Pieces MCP is now enabled for {self.readable}!")
            )
            console.print(
                Markdown(
                    f"For more information please refer to the docs: `{self.docs}`"
                )
            )
            console.print(Markdown(self.text_end))
        except:  # noqa: E722
            console.print(Markdown(self.error_text))


text_success_vscode = """
### Using Pieces LTM in VS Code

1. **Open Copilot Chat:**

       ⌘+Ctrl+I (macOS)
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
3. Ask a question like:
   > What was I working on yesterday?
4. Click **Use Tool** when prompted

> Ensure PiecesOS is running & LTM is enabled
"""

# NOTE: the key should be the same as the parameter name in the handle_mcp function
supported_mcps = {
    "vscode": Integration(
        handle_vscode,
        options=[
            (
                "Global (Set the MCP to run globally for all your projects) ",
                {"option": "global"},
            ),
            ("Local (Set the MCP to run for a specific Project)", {"option": "local"}),
        ],
        text_success=text_success_vscode,
        readable="VS Code",
        docs="https://docs.pieces.app/products/mcp/github-copilot#using-pieces-mcp-server-in-github-copilot",
    ),
    "goose": Integration(
        handle_goose,
        options=[],
        text_success=text_success_goose,
        readable="Goose",
        docs="https://docs.pieces.app/products/mcp/goose#using-pieces-mcp-with-goose",
    ),
    "cursor": Integration(
        handle_cursor,
        options=[],
        text_success=text_success_cursor,
        docs="https://docs.pieces.app/products/mcp/cursor#using-pieces-mcp-server-in-cursor",
        readable="Cursor",
    ),
}


def handle_mcp(
    vscode: Optional[Literal["global", "local", True]] = None,
    cursor: bool = False,
    goose: bool = False,
    **kwargs,
):
    if vscode:
        args = {}
        if vscode in ["global", "local"]:
            args = {"option": vscode}
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
