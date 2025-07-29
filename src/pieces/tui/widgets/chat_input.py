"""Chat input widget for user message entry."""

from textual.widgets import Input
from ..messages import UserMessages


class ChatInput(Input):
    """Enhanced input widget for chat messages."""

    def __init__(self, **kwargs):
        super().__init__(placeholder="Type your message here...", **kwargs)
        self.add_class("chat-input")
        self.add_class("input-container")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        if event.value.strip():
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
