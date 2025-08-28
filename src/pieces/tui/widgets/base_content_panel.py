"""Base content panel widget with common scrolling and styling functionality."""

from abc import abstractmethod
from textual.containers import ScrollableContainer
from textual.widgets import Static, Markdown
from textual.binding import Binding
from textual.app import ComposeResult

from pieces.settings import Settings
from ..utils import LinkHandler


class BaseContentPanel(ScrollableContainer):
    """Base class for content panels with common scrolling and styling."""

    DEFAULT_CSS = """
    BaseContentPanel {
        border: solid $primary;
        border-title-color: $primary;
        border-title-style: bold;
        scrollbar-background: $surface;
        scrollbar-color: $primary;
        scrollbar-color-hover: $accent;
        overflow-y: auto;
        overflow-x: hidden;
        
        &:focus {
            border: solid $accent;
            border-title-color: $accent;
            border-title-style: bold;
        }
    }
    
    BaseContentPanel .welcome-message {
        text-align: center;
        margin: 4 2;
        padding: 3;
        border: dashed $primary;
        background: $primary 10%;
        color: $text;
        width: 100%;
        height: auto;
    }
    """

    # Common scroll bindings for all content panels
    BINDINGS = [
        *[
            Binding(key, "scroll_down", "Scroll down", show=False)
            for key in ["j", "down"]
        ],
        *[Binding(key, "scroll_up", "Scroll up", show=False) for key in ["k", "up"]],
        Binding("d", "scroll_down_half", "Scroll down half page", show=False),
        Binding("u", "scroll_up_half", "Scroll up half page", show=False),
        Binding("gg", "jump_to_start", "Jump to start", show=False),
        Binding("G", "jump_to_end", "Jump to end", show=False),
        *[
            Binding(key, "page_down", "Page down", show=False)
            for key in ["ctrl+f", "page_down"]
        ],
        *[
            Binding(key, "page_up", "Page up", show=False)
            for key in ["ctrl+b", "page_up"]
        ],
    ]

    def __init__(self, panel_title: str = "Content", **kwargs):
        super().__init__(**kwargs)
        self.border_title = panel_title

    def compose(self) -> ComposeResult:
        """Compose the content panel."""
        return []

    def on_mount(self) -> None:
        """Initialize the content panel when mounted."""
        self._show_welcome_message()

    @abstractmethod
    def _show_welcome_message(self):
        """Show a welcome message when no content is loaded."""
        pass

    def _clear_content(self):
        """Clear all content from the panel."""
        try:
            children_to_remove = list(self.children)
            Settings.logger.info(
                f"BaseContentPanel: Clearing {len(children_to_remove)} child widgets"
            )
            for child in children_to_remove:
                try:
                    if child.is_mounted:
                        Settings.logger.info(
                            f"BaseContentPanel: Removing widget {child}"
                        )
                        child.remove()
                except (RuntimeError, ValueError, AttributeError):
                    pass
        except (RuntimeError, AttributeError):
            pass

    def _show_static_content(self, content: str, classes: str = ""):
        """Show static text content."""
        # Clear content first
        self._clear_content()

        Settings.logger.info(
            f"BaseContentPanel: Creating new static widget with classes='{classes}'"
        )
        widget = Static(content, classes=classes)
        self.mount(widget)
        Settings.logger.info(f"BaseContentPanel: Mounted widget {widget}")

    def _show_error_message(self, error: str):
        """Show an error message."""
        error_text = f"❌ Error: {error}"
        self._show_static_content(error_text, classes="error-message")

    def cleanup(self):
        """Clean up content panel resources."""
        try:
            self._clear_content()
        except Exception as e:
            Settings.logger.error(f"Error during content panel cleanup: {e}")

    # Navigation methods
    def action_scroll_down(self):
        """Scroll down one line."""
        self.scroll_relative(y=1)

    def action_scroll_up(self):
        """Scroll up one line."""
        self.scroll_relative(y=-1)

    def action_scroll_down_half(self):
        """Scroll down half a page."""
        self.scroll_relative(y=self.size.height // 2)

    def action_scroll_up_half(self):
        """Scroll up half a page."""
        self.scroll_relative(y=-(self.size.height // 2))

    def action_page_down(self):
        """Page down."""
        self.scroll_relative(y=self.size.height)

    def action_page_up(self):
        """Page up."""
        self.scroll_relative(y=-self.size.height)

    def action_jump_to_start(self):
        """Jump to the start of the conversation."""
        self.scroll_home(animate=False)

    def action_jump_to_end(self):
        """Jump to the end of the conversation."""
        self.scroll_end(animate=False)

    def _process_file_links(self, content: str) -> str:
        """Convert file:// protocol links to proper relative paths for Textual."""
        return LinkHandler.process_file_links(content)

    async def on_markdown_link_clicked(self, event: Markdown.LinkClicked) -> None:
        """Handle clicks on markdown links."""
        await LinkHandler.handle_link_click(event, self.app)
