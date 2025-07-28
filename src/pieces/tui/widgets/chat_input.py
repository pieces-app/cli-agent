"""Chat input widget for message composition."""

from textual.widgets import Input
from textual.message import Message


class ChatInput(Input):
    """Custom input widget for chat messages with enhanced functionality."""

    def __init__(self, **kwargs):
        super().__init__(
            placeholder="Type your message here... (Press Enter to send)", **kwargs
        )
        self.add_class("chat-input")

    class MessageSubmitted(Message):
        """Message sent when user submits a chat message."""

        def __init__(self, text: str):
            super().__init__()
            self.text = text

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        if event.value.strip():
            self.post_message(self.MessageSubmitted(event.value.strip()))
            self.value = ""

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
        self.set_placeholder("Type your message here... (Press Enter to send)")
