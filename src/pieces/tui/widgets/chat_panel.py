"""Enhanced chat panel widget for displaying conversation history with metadata."""

from typing import List, Optional, TYPE_CHECKING
from textual.reactive import reactive
from textual.containers import ScrollableContainer
from textual.widgets import Static
from textual.binding import Binding

from .chat_message import ChatMessage
from pieces.settings import Settings

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.wrapper.basic_identifier.chat import BasicChat
    from pieces._vendor.pieces_os_client.wrapper.basic_identifier.message import (
        BasicMessage,
    )


class ChatPanel(ScrollableContainer):
    """Enhanced chat panel to display conversation messages with metadata."""

    messages: reactive[List[ChatMessage]] = reactive([])
    current_chat: Optional["BasicChat"] = None
    selected_message_index: int = -1

    BINDINGS = [
        Binding("j", "select_next", "Next message", show=False),
        Binding("k", "select_previous", "Previous message", show=False),
        Binding("g g", "jump_to_start", "Jump to start", show=False),
        Binding("G", "jump_to_end", "Jump to end", show=False),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.border_title = "Chat"
        self.add_class("main-chat")
        self.add_class("chat-panel")
        self._streaming_widget: Optional[Static] = None
        self._thinking_widget: Optional[Static] = None

    def load_conversation(self, chat: "BasicChat"):
        """Load an entire conversation with full message history."""
        self.current_chat = chat
        self.clear_messages()

        try:
            # Update border title with chat name
            self.border_title = f"Chat: {chat.name}"

            # Load all messages
            messages = chat.messages()
            for message in messages:
                self._add_message_from_basic(message)

            # Scroll to the end
            self.scroll_end(animate=False)

        except Exception as e:
            Settings.logger.error(f"Error loading conversation: {e}")
            self.add_message("system", f"❌ Error loading conversation: {str(e)}")

    def _add_message_from_basic(self, basic_message: "BasicMessage"):
        """Add a message from a BasicMessage object."""
        try:
            message_widget = ChatMessage.from_basic_message(basic_message)
            self.messages.append(message_widget)
            self.mount(message_widget)
        except Exception as e:
            Settings.logger.error(f"Error adding message: {e}")

    def add_message(self, role: str, content: str, timestamp: Optional[str] = None):
        """Add a new message to the chat panel."""
        # Remove any thinking indicators first
        self._clear_thinking_indicator()

        # Create and add the message
        message_widget = ChatMessage(role=role, content=content, timestamp=timestamp)
        self.messages.append(message_widget)
        self.mount(message_widget)
        self.scroll_end(animate=False)

    def add_thinking_indicator(self):
        """Add a thinking indicator."""
        self._clear_thinking_indicator()

        self._thinking_widget = Static("🤔 Thinking...", classes="message-thinking")
        self.mount(self._thinking_widget)
        self.scroll_end(animate=False)

    def add_streaming_message(self, role: str, content: str):
        """Add a new streaming message (shows with cursor)."""
        # Remove thinking indicator if present
        self._clear_thinking_indicator()

        # Create streaming widget
        self._streaming_widget = Static(
            content + " ▌",
            classes=f"message-content message-content-{role} message-streaming",
        )
        self.mount(self._streaming_widget)
        self.scroll_end(animate=False)

    def update_streaming_message(self, content: str):
        """Update the current streaming message."""
        if self._streaming_widget:
            self._streaming_widget.update(content + " ▌")
            self.scroll_end(animate=False)

    def finalize_streaming_message(self):
        """Convert streaming message to final message."""
        if self._streaming_widget:
            # Get the content without cursor
            content = str(self._streaming_widget.renderable).replace(" ▌", "")

            # Remove streaming widget
            self._streaming_widget.remove()
            self._streaming_widget = None

            # Add final message with current timestamp
            from datetime import datetime

            timestamp = datetime.now().strftime("Today %I:%M %p")

            self.add_message("assistant", content, timestamp=timestamp)

    def _clear_thinking_indicator(self):
        """Remove thinking indicator if present."""
        if self._thinking_widget:
            self._thinking_widget.remove()
            self._thinking_widget = None

    def clear_messages(self):
        """Clear all messages from the chat panel."""
        self.messages.clear()
        self._streaming_widget = None
        self._thinking_widget = None
        self.selected_message_index = -1
        self.remove_children()

    def get_message_count(self) -> int:
        """Get the total number of messages."""
        return len(self.messages)

    def get_last_message(self) -> Optional[ChatMessage]:
        """Get the last message widget."""
        return self.messages[-1] if self.messages else None

    # Navigation methods
    def action_select_next(self):
        """Select the next message."""
        if self.messages:
            self._update_selection(
                min(self.selected_message_index + 1, len(self.messages) - 1)
            )

    def action_select_previous(self):
        """Select the previous message."""
        if self.messages:
            self._update_selection(max(self.selected_message_index - 1, 0))

    def action_jump_to_start(self):
        """Jump to the first message."""
        if self.messages:
            self._update_selection(0)
            self.scroll_to_widget(self.messages[0])

    def action_jump_to_end(self):
        """Jump to the last message."""
        if self.messages:
            self._update_selection(len(self.messages) - 1)
            self.scroll_to_widget(self.messages[-1])

    def _update_selection(self, new_index: int):
        """Update the selected message."""
        # Unhighlight previous
        if 0 <= self.selected_message_index < len(self.messages):
            self.messages[self.selected_message_index].unhighlight()

        # Highlight new
        self.selected_message_index = new_index
        if 0 <= self.selected_message_index < len(self.messages):
            selected = self.messages[self.selected_message_index]
            selected.highlight()
            self.scroll_to_widget(selected)
