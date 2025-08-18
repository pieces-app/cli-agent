"""Workstream content panel widget for displaying and editing workstream summaries."""

from typing import Optional, TYPE_CHECKING
from textual.reactive import reactive
from textual.containers import ScrollableContainer, Vertical
from textual.widgets import Static, Markdown, TextArea, Button
from textual.binding import Binding
from textual.app import ComposeResult

from pieces.settings import Settings
from ..messages import WorkstreamMessages

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.wrapper.basic_identifier.summary import (
        BasicSummary,
    )


class WorkstreamContentPanel(ScrollableContainer):
    """Panel for displaying and editing workstream summary content."""

    DEFAULT_CSS = """
    WorkstreamContentPanel {
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
    
    WorkstreamContentPanel .content-header {
        height: 3;
        width: 100%;
        margin: 0 0 1 0;
        padding: 0 1;
        background: $surface;
        border-bottom: solid $primary;
    }
    

    
    WorkstreamContentPanel .content-area {
        width: 100%;
        height: 1fr;
        padding: 1;
    }
    
    WorkstreamContentPanel .markdown-content {
        width: 100%;
        height: auto;
        background: transparent;
        padding: 0;
    }
    
    WorkstreamContentPanel .editor-content {
        width: 100%;
        height: 1fr;
        background: $surface;
        border: solid $secondary;
        padding: 1;
        
        &:focus {
            border: solid $accent;
        }
    }
    
    WorkstreamContentPanel .welcome-message {
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

    BINDINGS = [
        Binding("ctrl+e", "toggle_edit_mode", "Toggle Edit Mode"),
        Binding("ctrl+s", "save_content", "Save Content", show=False),
        *[
            Binding(key, "scroll_down", "Scroll down", show=False)
            for key in ["j", "down"]
        ],
        *[Binding(key, "scroll_up", "Scroll up", show=False) for key in ["k", "up"]],
        Binding("d", "scroll_down_half", "Scroll down half page", show=False),
        Binding("u", "scroll_up_half", "Scroll up half page", show=False),
        Binding("gg", "jump_to_start", "Jump to start", show=False),
        Binding("G", "jump_to_end", "Jump to end", show=False),
    ]

    edit_mode: reactive[bool] = reactive(False)
    current_summary: Optional["BasicSummary"] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.border_title = "Workstream Content"
        self._content_area: Optional[ScrollableContainer] = None
        self._markdown_widget: Optional[Markdown] = None
        self._editor_widget: Optional[TextArea] = None
        self._original_content = ""
        self._has_changes = False

    def compose(self) -> ComposeResult:
        """Compose the workstream content panel."""
        # Content area
        self._content_area = ScrollableContainer(
            classes="content-area", id="content-area"
        )
        yield self._content_area

    def on_mount(self) -> None:
        """Initialize the content panel when mounted."""
        self._show_welcome_message()

    def load_workstream_summary(self, summary: "BasicSummary"):
        """Load a workstream summary for display/editing."""
        self.current_summary = summary
        self.border_title = f"Workstream: {summary.name}"

        # Extract content from summary
        content = self._extract_summary_content(summary)
        self._original_content = content
        self._has_changes = False



        # Display content based on current mode
        if self.edit_mode:
            self._show_editor_content(content)
        else:
            self._show_markdown_content(content)

    def _extract_summary_content(self, summary: "BasicSummary") -> str:
        """Extract markdown content from workstream summary."""
        content = f"# {summary.name}\n\n"

        # Add summary ID for reference
        content += f"**Summary ID:** {summary.id}\n\n"

        # Add the raw content if available
        if hasattr(summary, "raw_content") and summary.raw_content:
            content += "## Content\n\n"
            content += summary.raw_content
        else:
            content += "## Summary\n\n"
            content += "*Edit this content to add your workstream summary details.*\n\n"
            content += "Use the Edit mode (Ctrl+E) to modify this content and save changes (Ctrl+S)."

        return content

    def _show_welcome_message(self):
        """Show a welcome message when no summary is selected."""
        if self._content_area:
            self._clear_content_area()

            welcome_text = """🔄 Workstream Activities

Select a workstream activity from the left panel to view or edit its content.

• Use 📖 Read mode to view formatted markdown
• Use ✏️ Edit mode to modify the content  
• Press Ctrl+E to toggle between modes
• Press Ctrl+S to save changes

Ready to manage your workstream activities!"""

            welcome_widget = Static(
                welcome_text, classes="welcome-message", id="welcome-message"
            )
            self._content_area.mount(welcome_widget)

    def _show_markdown_content(self, content: str):
        """Show content in read mode (markdown)."""
        if self._content_area:
            self._clear_content_area()

            self._markdown_widget = Markdown(content, classes="markdown-content")
            self._content_area.mount(self._markdown_widget)

    def _show_editor_content(self, content: str):
        """Show content in edit mode (text editor)."""
        if self._content_area:
            self._clear_content_area()

            self._editor_widget = TextArea(
                text=content,
                language="markdown",
                theme="monokai",
                classes="editor-content",
                id="content-editor",
            )
            self._content_area.mount(self._editor_widget)

    def _clear_content_area(self):
        """Clear the content area."""
        if self._content_area:
            try:
                children_to_remove = list(self._content_area.children)
                for child in children_to_remove:
                    try:
                        child.remove()
                    except (RuntimeError, ValueError):
                        pass
            except (RuntimeError, AttributeError):
                pass

    def watch_edit_mode(self, edit_mode: bool) -> None:
        """Handle edit mode changes."""
        # Update content display
        if self.current_summary:
            content = self._get_current_content()
            if edit_mode:
                self._show_editor_content(content)
            else:
                self._show_markdown_content(content)

        # Post message about mode change
        self.post_message(WorkstreamMessages.EditModeToggled(edit_mode))

    def _get_current_content(self) -> str:
        """Get the current content (from editor if in edit mode, otherwise original)."""
        if self.edit_mode and self._editor_widget:
            return self._editor_widget.text
        return self._original_content

    def action_toggle_edit_mode(self):
        """Toggle between read and edit modes."""
        self.edit_mode = not self.edit_mode

    def action_save_content(self):
        """Save the current content."""
        if not self.edit_mode or not self._editor_widget or not self.current_summary:
            return

        new_content = self._editor_widget.text
        if new_content != self._original_content:
            self._original_content = new_content
            self._has_changes = False

            if self._save_button:
                self._save_button.disabled = True

            # Post save message
            self.post_message(WorkstreamMessages.ContentSaved(new_content))
            Settings.logger.info(
                f"Saved workstream summary content for: {self.current_summary.name}"
            )



    async def on_text_area_changed(self, event: TextArea.Changed) -> None:
        """Handle text area content changes."""
        if event.text_area.id == "content-editor":
            # Check if content has changed
            current_content = event.text_area.text
            has_changes = current_content != self._original_content

            if has_changes != self._has_changes:
                self._has_changes = has_changes

    def clear_content(self):
        """Clear the current content."""
        self.current_summary = None
        self.border_title = "Workstream Content"
        self._original_content = ""
        self._has_changes = False

        self._show_welcome_message()

    # Navigation methods (similar to ChatViewPanel)
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

    def action_jump_to_start(self):
        """Jump to the start of the content."""
        self.scroll_home(animate=False)

    def action_jump_to_end(self):
        """Jump to the end of the content."""
        self.scroll_end(animate=False)

    def cleanup(self):
        """Clean up widget resources."""
        try:
            self.clear_content()
            self._content_area = None
            self._markdown_widget = None
            self._editor_widget = None
        except Exception as e:
            Settings.logger.error(f"Error during WorkstreamContentPanel cleanup: {e}")

    def __del__(self):
        """Ensure cleanup is called when widget is destroyed."""
        try:
            self.cleanup()
        except (RuntimeError, ValueError, AttributeError):
            pass
