"""Enhanced chat view panel widget for displaying conversation history with metadata."""

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


class ChatViewPanel(ScrollableContainer):
    """Enhanced chat view panel to display conversation messages with metadata."""

    DEFAULT_CSS = """
    ChatViewPanel {
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
    
    ChatViewPanel .message-streaming { 
        border-left: thick $accent;
        text-style: bold;
    }
    
    ChatViewPanel .message-thinking {
        color: $warning;
        text-style: italic bold blink;
        text-align: center;
        background: $surface;
        border: dashed $warning;
        padding: 1;
        margin: 1;
    }
    """

    messages: reactive[List[ChatMessage]] = reactive([])
    current_chat: Optional["BasicChat"] = None

    BINDINGS = [
        Binding("j", "scroll_down", "Scroll down", show=False),
        Binding("k", "scroll_up", "Scroll up", show=False),
        Binding("d", "scroll_down_half", "Scroll down half page", show=False),
        Binding("u", "scroll_up_half", "Scroll up half page", show=False),
        Binding("g g", "jump_to_start", "Jump to start", show=False),
        Binding("G", "jump_to_end", "Jump to end", show=False),
        Binding("ctrl+f", "page_down", "Page down", show=False),
        Binding("ctrl+b", "page_up", "Page up", show=False),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.border_title = "Chat"
        self._streaming_widget: Optional[Static] = None
        self._thinking_widget: Optional[Static] = None
        self._last_message_count = 0  # Track message count for incremental updates

    def load_conversation(self, chat: "BasicChat"):
        """Load an entire conversation with full message history."""
        self.current_chat = chat
        self.clear_messages()

        try:
            # Update border title with chat name
            self.border_title = f"Chat: {chat.name}"

            # Load all messages in exact order from API
            messages = chat.messages()
            Settings.logger.info(
                f"Loading {len(messages)} messages in API order for chat: {chat.name}"
            )

            for i, message in enumerate(messages):
                Settings.logger.debug(
                    f"Message {i}: {message.role} - created: {message.message.created.value if message.message.created else 'None'}"
                )
                self._add_message_from_basic(message)

            # Track message count for incremental updates
            self._last_message_count = len(messages)

            # Scroll to the end
            self.scroll_end(animate=False)

        except Exception as e:
            Settings.logger.error(f"Error loading conversation: {e}")
            self.add_message("system", f"❌ Error loading conversation: {str(e)}")

    def update_conversation_incrementally(self, chat: "BasicChat"):
        """Add only new messages to the conversation without full reload."""
        if not self.current_chat or self.current_chat.id != chat.id:
            # Different chat - do full reload
            self.load_conversation(chat)
            return

        try:
            # Get all messages
            messages = chat.messages()
            current_count = len(messages)
            last_count = getattr(self, "_last_message_count", 0)

            Settings.logger.info(
                f"Incremental update: {last_count} -> {current_count} messages"
            )

            if current_count <= last_count:
                # No new messages or messages were deleted - do full reload for safety
                Settings.logger.info(
                    "No new messages or messages deleted - doing full reload"
                )
                self.load_conversation(chat)
                return

            # Add only the new messages
            new_messages = messages[last_count:]
            Settings.logger.info(
                f"Adding {len(new_messages)} new messages incrementally"
            )

            for i, message in enumerate(new_messages):
                Settings.logger.debug(
                    f"Adding new message {last_count + i}: {message.role}"
                )
                self._add_message_from_basic(message)

            # Update message count
            self._last_message_count = current_count

            # Scroll to show new messages
            self.scroll_end(animate=False)

        except Exception as e:
            Settings.logger.error(f"Error in incremental update: {e}")
            # Fall back to full reload on error
            self.load_conversation(chat)

    def _add_message_from_basic(self, basic_message: "BasicMessage"):
        """Add a message from a BasicMessage object."""
        try:
            message_widget = ChatMessage.from_basic_message(basic_message)
            self.messages.append(message_widget)
            self.mount(message_widget)
        except Exception as e:
            Settings.logger.error(f"Error adding message: {e}")

    def add_message(
        self,
        role: str,
        content: str,
        timestamp: Optional[str] = None,
        message_id: Optional[str] = None,
    ):
        """Add a new message to the chat panel."""
        # Remove any thinking indicators first
        self._clear_thinking_indicator()

        # Create and add the message
        message_widget = ChatMessage(
            role=role, content=content, timestamp=timestamp, message_id=message_id
        )
        self.messages.append(message_widget)
        self.mount(message_widget)
        self.scroll_end(animate=False)

    def add_thinking_indicator(self):
        """Add a thinking indicator at the bottom of the chat."""
        Settings.logger.info("Adding thinking indicator...")
        self._clear_thinking_indicator()

        self._thinking_widget = Static("🤔 Thinking...", classes="message-thinking")
        self.mount(self._thinking_widget)
        
        # Ensure we scroll to bottom after the widget is mounted
        self.call_after_refresh(self._scroll_to_thinking_indicator)
        Settings.logger.info("Thinking indicator added and mounted")
    
    def _scroll_to_thinking_indicator(self):
        """Scroll to the thinking indicator after it's properly mounted."""
        if self._thinking_widget and self._thinking_widget.is_mounted:
            # Scroll to the end to show the thinking indicator
            self.scroll_end(animate=True)
            # Also try scrolling to the specific widget
            try:
                self.scroll_to_widget(self._thinking_widget, animate=True)
            except Exception:
                pass  # Fallback if scroll_to_widget fails

    def add_streaming_message(self, role: str, content: str):
        """Add a new streaming message (shows with cursor) at the bottom."""
        # Remove thinking indicator if present
        self._clear_thinking_indicator()

        # Create streaming widget (always use Static for streaming to show cursor)
        self._streaming_widget = Static(
            content + " ▌",
            classes=f"message-content message-content-{role} message-streaming",
        )
        self.mount(self._streaming_widget)
        
        # Ensure streaming message appears at bottom
        self.call_after_refresh(self._scroll_to_streaming_message)
    
    def _scroll_to_streaming_message(self):
        """Scroll to the streaming message after it's properly mounted."""
        if self._streaming_widget and self._streaming_widget.is_mounted:
            # Scroll to the end to show the streaming message
            self.scroll_end(animate=True)
            # Also try scrolling to the specific widget
            try:
                self.scroll_to_widget(self._streaming_widget, animate=True)
            except Exception:
                pass  # Fallback if scroll_to_widget fails

    def update_streaming_message(self, content: str):
        """Update the current streaming message."""
        if self._streaming_widget:
            self._streaming_widget.update(content + " ▌")
            self.scroll_end(animate=False)

    def finalize_streaming_message(self):
        """Convert streaming message to final message with markdown support."""
        if self._streaming_widget:
            # Get the content without cursor
            content = str(self._streaming_widget.renderable).replace(" ▌", "")

            # Get the role from the CSS class
            role = "assistant"  # Default for streaming messages
            if "message-content-user" in str(self._streaming_widget.classes):
                role = "user"
            elif "message-content-system" in str(self._streaming_widget.classes):
                role = "system"

            # Remove streaming widget
            self._streaming_widget.remove()
            self._streaming_widget = None

            # Add final message with current timestamp and markdown support
            from datetime import datetime

            timestamp = datetime.now().strftime("Today %I:%M %p")

            # Use the regular add_message method which will handle markdown
            self.add_message(role, content, timestamp=timestamp)

    def _clear_thinking_indicator(self):
        """Remove thinking indicator if present."""
        if self._thinking_widget:
            self._thinking_widget.remove()
            self._thinking_widget = None

    def clear_messages(self):
        """Clear all messages from the chat panel."""
        # First remove thinking and streaming widgets safely
        self._clear_thinking_indicator()
        self._clear_streaming_widget()

        # Clear message list
        self.messages.clear()

        # Reset message count tracking for incremental updates
        self._last_message_count = 0

        # Remove ALL children widgets (including welcome messages)
        try:
            # Get all child widgets and remove them
            children_to_remove = list(self.children)
            for child in children_to_remove:
                try:
                    child.remove()
                except (RuntimeError, ValueError):
                    pass  # Widget may already be removed
        except (RuntimeError, AttributeError):
            pass

        # Ensure we're completely clean
        self.remove_children()

    def _clear_streaming_widget(self):
        """Remove streaming widget if present."""
        if self._streaming_widget:
            try:
                self._streaming_widget.remove()
            except (RuntimeError, ValueError):
                pass  # Widget may already be removed
            finally:
                self._streaming_widget = None

    def cleanup(self):
        """Clean up widget resources to prevent memory leaks."""
        try:
            # Clear all messages and widgets
            self.clear_messages()

            # Clear current chat reference
            self.current_chat = None

        except Exception as e:
            Settings.logger.error(f"Error during ChatViewPanel cleanup: {e}")

    def __del__(self):
        """Ensure cleanup is called when widget is destroyed."""
        try:
            self.cleanup()
        except Exception:
            # Ignore errors during cleanup in destructor
            pass

    def get_message_count(self) -> int:
        """Get the total number of messages."""
        return len(self.messages)

    def get_last_message(self) -> Optional[ChatMessage]:
        """Get the last message widget."""
        return self.messages[-1] if self.messages else None

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
