"""Workstream content panel widget for displaying and editing workstream summaries."""

from typing import Optional, TYPE_CHECKING
from textual.reactive import reactive
from textual.widgets import Markdown, TextArea
from textual.binding import Binding
from textual.app import ComposeResult
from textual.events import Key

from .base_content_panel import BaseContentPanel
from pieces.settings import Settings
from ..messages import WorkstreamMessages

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.wrapper.basic_identifier.summary import (
        BasicSummary,
    )


class WorkstreamContentPanel(BaseContentPanel):
    """Panel for displaying and editing workstream summary content."""

    DEFAULT_CSS = """
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
    
    """

    BINDINGS = BaseContentPanel.BINDINGS + [
        Binding("ctrl+e", "toggle_edit_mode", "Edit Mode"),
        Binding("ctrl+s", "save_content", "Save Content"),
    ]

    edit_mode: reactive[bool] = reactive(False, bindings=True)
    current_summary: Optional["BasicSummary"] = None

    def __init__(self, **kwargs):
        super().__init__(panel_title="Workstream Content", **kwargs)
        self._markdown_widget: Optional[Markdown] = None
        self._editor_widget: Optional[TextArea] = None
        self._original_content = ""
        self._has_changes = False

    def compose(self) -> ComposeResult:
        """Compose the workstream content panel."""
        return []

    def on_mount(self) -> None:
        """Initialize the content panel when mounted."""
        pass

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
        content = ""

        if summary.raw_content:
            content += summary.raw_content
        else:
            content += "## Summary\n\n"
            content += "*Edit this content to add your workstream summary details.*\n\n"
            content += "\nUse the Edit mode (Ctrl+E) to modify this content and save changes (Ctrl+S)."

        return content

    def _show_welcome_message(self):
        """Show a welcome message when no summary is selected."""
        Settings.logger.info("WorkstreamContentPanel: Showing welcome message")
        welcome_text = """🔄 Workstream Activities

Select a workstream activity from the left panel to view or edit its content.

• Use 📖 Read mode to view formatted markdown
• Use ✏️ Edit mode to modify the content  
• Press Ctrl+E to toggle between modes
• Press Ctrl+S to save changes

Ready to manage your workstream activities!"""

        self._show_static_content(welcome_text, classes="welcome-message")

    def _show_markdown_content(self, content: str):
        """Show content in read mode (markdown)."""
        self._clear_content()

        # Convert file:// links to proper relative paths for Textual
        processed_content = self._process_file_links(content)

        self._markdown_widget = Markdown(processed_content, classes="markdown-content")
        self.mount(self._markdown_widget)

    def _show_editor_content(self, content: str):
        """Show content in edit mode (text editor)."""
        self._clear_content()

        self._editor_widget = TextArea.code_editor(
            text=content,
            language="markdown",
            classes="editor-content",
            id="content-editor",
        )
        self.mount(self._editor_widget)
        self._editor_widget.focus()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """Check if an action may run."""
        if action == "toggle_edit_mode" and self.edit_mode:
            return None
        if action == "save_content" and not self.edit_mode:
            return False
        return True

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
        """Get the current content"""
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

            # Post save message
            self.post_message(WorkstreamMessages.ContentSaved(new_content))
            Settings.logger.info(
                f"Saved workstream summary content for: {self.current_summary.name}"
            )
        self.action_toggle_edit_mode()

    async def on_text_area_changed(self, event: TextArea.Changed) -> None:
        """Handle text area content changes."""
        if event.text_area.id == "content-editor":
            # Check if content has changed
            current_content = event.text_area.text
            has_changes = current_content != self._original_content

            if has_changes != self._has_changes:
                self._has_changes = has_changes

    def clear_content(self, show_welcome: bool = True):
        """Clear the current content."""
        self.current_summary = None
        self.border_title = "Workstream Content"
        self._original_content = ""
        self._has_changes = False

        if show_welcome:
            self._show_welcome_message()

    def has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes in the editor buffer."""
        return self._has_changes and self.edit_mode and self._editor_widget is not None

    def get_editor_content(self) -> str:
        """Get the current content from the editor."""
        if self.edit_mode and self._editor_widget:
            return self._editor_widget.text
        return self._original_content

    def cleanup(self):
        """Clean up widget resources."""
        try:
            self.clear_content()
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
