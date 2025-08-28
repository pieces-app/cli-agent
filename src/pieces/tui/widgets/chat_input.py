"""Chat input widget for user message entry."""

from textual.widgets import Input
from ..messages import UserMessages


class ChatInput(Input):
    """Enhanced input widget for chat messages."""

    DEFAULT_CSS = """
    ChatInput {
        width: 100%;
        height: 3;
        background: $surface;
        border: solid $primary;
        padding: 0 1;
        margin: 0 0 1 0;
        dock: bottom;
        
        &:focus {
            border: solid $accent;
            background: $panel;
            border-title-color: $accent;
        }
        
        &:disabled {
            border: solid $primary 50%;
            background: $background;
            color: $text-muted;
        }
    }
    """

    def __init__(self, **kwargs):
        super().__init__(placeholder="Type your message here...", **kwargs)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        if event.value.strip():
            # Check if streaming is active by looking for ChatViewPanel in parent hierarchy
            chat_view_panel = None
            try:
                # Walk up the widget tree to find ChatViewPanel
                parent = self.parent
                while parent:
                    if hasattr(parent, "chat_view_panel") and parent.chat_view_panel:
                        chat_view_panel = parent.chat_view_panel
                        break
                    elif parent.__class__.__name__ == "ChatViewPanel":
                        chat_view_panel = parent
                        break
                    parent = getattr(parent, "parent", None)

                # If we found a chat view panel, check if streaming is active
                if chat_view_panel and hasattr(chat_view_panel, "is_streaming_active"):
                    if chat_view_panel.is_streaming_active():
                        event.stop()
                        return
            except Exception:
                pass

            # Post Textual message that will bubble up to parent handlers
            self.post_message(UserMessages.InputSubmitted(event.value.strip()))

            # Clear the input
            self.value = ""

            # Prevent default handling
            event.stop()

    def on_mount(self) -> None:
        """Focus the input when mounted."""
        self.focus()

    def clear_input(self):
        """Clear the input field."""
        self.value = ""

    def set_placeholder(self, text: str):
        """Update the placeholder text."""
        self.placeholder = text
        self.refresh()

    def disable_input(self):
        """Disable the input field."""
        self.disabled = True
        self.set_placeholder("Please wait...")

    def enable_input(self):
        """Enable the input field."""
        self.disabled = False
        self.set_placeholder("Type your message here...")
