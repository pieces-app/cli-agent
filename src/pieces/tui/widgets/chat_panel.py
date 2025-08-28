"""Chat view panel widget for displaying conversation history."""

from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
import threading
from textual.reactive import reactive
from textual.widgets import Static, Markdown
from textual.css.query import NoMatches
from textual.types import NoActiveAppError
from textual.message import Message

from .base_content_panel import BaseContentPanel
from .chat_message import ChatMessage
from pieces.settings import Settings

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.wrapper.basic_identifier.chat import BasicChat
    from pieces._vendor.pieces_os_client.wrapper.basic_identifier.message import (
        BasicMessage,
    )


class AddMessageFromBasic(Message):
    """Message to add a BasicMessage to the UI from background thread."""

    def __init__(self, basic_message: "BasicMessage") -> None:
        super().__init__()
        self.basic_message = basic_message


class FinalizeLoading(Message):
    """Message to finalize loading process from background thread."""

    def __init__(self, message_count: int) -> None:
        super().__init__()
        self.message_count = message_count


class ShowError(Message):
    """Message to show error from background thread."""

    def __init__(self, error_message: str) -> None:
        super().__init__()
        self.error_message = error_message


class ChatViewPanel(BaseContentPanel):
    """Chat view panel to display conversation messages."""

    DEFAULT_CSS = """
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

    def __init__(self, **kwargs):
        super().__init__(panel_title="Chat", **kwargs)
        self._streaming_widget: Optional[ChatMessage] = None
        self._thinking_widget: Optional[Static] = None
        self._last_message_count = 0

    def load_conversation(self, chat: "BasicChat"):
        """Load a conversation from a BasicChat object."""
        self.current_chat = chat
        self.clear_messages()
        self.border_title = f"Chat: {chat.name}"
        threading.Thread(target=self.load_messages, args=(chat,), daemon=True).start()

    def load_messages(self, chat: "BasicChat"):
        """Load messages in background thread with proper UI updates via message system."""
        try:
            messages = chat.messages()
            Settings.logger.info(
                f"Loading {len(messages)} messages for chat: {chat.name}"
            )

            for i, message in enumerate(messages):
                Settings.logger.debug(
                    f"Message {i}: {message.role} - created: {message.message.created.value if message.message.created else 'None'}"
                )
                # Send message to main thread to add this message
                self.post_message(AddMessageFromBasic(message))

            # Send message to finalize loading
            self.post_message(FinalizeLoading(len(messages)))

        except Exception as e:
            Settings.logger.error(f"Error loading conversation: {e}")
            # Send error message to main thread
            self.post_message(ShowError(f"❌ Error loading conversation: {str(e)}"))

    def update_conversation_incrementally(self, chat: "BasicChat"):
        """Add new messages to the conversation without full reload."""
        if not self.current_chat or self.current_chat.id != chat.id:
            self.load_conversation(chat)
            return

        try:
            messages = chat.messages()
            current_count = len(messages)
            last_count = getattr(self, "_last_message_count", 0)

            Settings.logger.info(
                f"Incremental update: {last_count} -> {current_count} messages"
            )

            if current_count <= last_count:
                Settings.logger.info(
                    "No new messages or messages deleted - doing full reload"
                )
                self.load_conversation(chat)
                return

            # Don't defer updates when streaming/thinking - just be smart about duplicates
            # The manual user message and finalized streaming message already incremented the count

            new_messages = messages[last_count:]
            Settings.logger.info(
                f"Adding {len(new_messages)} new messages incrementally"
            )

            for i, message in enumerate(new_messages):
                Settings.logger.debug(
                    f"Adding new message {last_count + i}: {message.role}"
                )
                self._add_message_from_basic(message)

            self._last_message_count = current_count
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

    def on_add_message_from_basic(self, event: AddMessageFromBasic) -> None:
        """Handle message to add a BasicMessage from background thread."""
        self._add_message_from_basic(event.basic_message)

    def on_finalize_loading(self, event: FinalizeLoading) -> None:
        """Handle message to finalize loading from background thread."""
        self._last_message_count = event.message_count
        self.scroll_end(animate=False)

    def on_show_error(self, event: ShowError) -> None:
        """Handle message to show error from background thread."""
        self.add_message("system", event.error_message)

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
        """Scroll to the thinking indicator."""
        if self._thinking_widget and self._thinking_widget.is_mounted:
            self.scroll_end(animate=False)
            try:
                self.scroll_to_widget(self._thinking_widget, animate=False)
            except (ValueError, RuntimeError):
                pass

    def add_streaming_message(self, role: str, content: str):
        """Add a streaming message with markdown support and cursor indicator."""
        self._clear_thinking_indicator()

        # Check if streaming widget already exists and warn about potential race condition
        if self._streaming_widget:
            Settings.logger.info(
                "Streaming widget already exists when trying to add new streaming message - potential race condition"
            )
            self._clear_streaming_widget()

        # Create a streaming ChatMessage widget for markdown support
        timestamp = datetime.now().strftime("Today %I:%M %p")

        self._streaming_widget = ChatMessage(
            role=role,
            content=content + " ▌",  # Add cursor
            timestamp=timestamp,
            classes="message-streaming",
        )
        self.mount(self._streaming_widget)
        self.call_after_refresh(self._scroll_to_streaming_message)

    def _scroll_to_streaming_message(self):
        """Scroll to the streaming message."""
        if self._streaming_widget and self._streaming_widget.is_mounted:
            self.scroll_end(animate=False)
            try:
                self.scroll_to_widget(self._streaming_widget, animate=False)
            except (ValueError, RuntimeError):
                # Widget may not be mounted or visible
                pass

    def update_streaming_message(self, content: str):
        """Update the streaming message content with markdown support."""
        if self._streaming_widget:
            content_with_cursor = content + " ▌"
            self._streaming_widget.content = content_with_cursor
            self.call_after_refresh(
                lambda: self._update_streaming_after_refresh(content_with_cursor)
            )

    def finalize_streaming_message(self):
        """Convert streaming message to permanent message."""
        if self._streaming_widget:
            # Get the final content without cursor from the ChatMessage
            content = self._streaming_widget.content.replace(" ▌", "")
            role = self._streaming_widget.role
            timestamp = self._streaming_widget.timestamp

            # Remove streaming widget
            self._streaming_widget.remove()
            self._streaming_widget = None

            self.add_message(role, content, timestamp=timestamp)
            self.increment_message_count()

    def _clear_thinking_indicator(self):
        """Remove thinking indicator if present."""
        if self._thinking_widget:
            self._thinking_widget.remove()
            self._thinking_widget = None

    def _show_welcome_message(self):
        """Show a welcome message when no chat is loaded."""
        welcome_text = """💬 Pieces Copilot

Welcome to your AI-powered coding assistant!

• Select a chat from the left panel to continue a conversation
• Press Ctrl+N to start a new chat
• Type your questions in the input field below
• Use Ctrl+Shift+M to change AI models

Ready to help with your coding tasks!"""

        self._show_static_content(welcome_text, classes="welcome-message")

    def clear_messages(self):
        """Clear all messages from the chat panel."""
        self._clear_thinking_indicator()
        self._clear_streaming_widget()

        self.messages.clear()
        self._last_message_count = 0

        try:
            children_to_remove = list(self.children)
            for child in children_to_remove:
                try:
                    child.remove()
                except (RuntimeError, ValueError):
                    pass  # Widget may already be removed
        except (RuntimeError, AttributeError):
            pass

        # Ensure we're completely clean - but only if app context is available
        try:
            self.remove_children()
        except NoActiveAppError:
            pass

    def _clear_streaming_widget(self):
        """Remove streaming widget if present."""
        if self._streaming_widget:
            try:
                self._streaming_widget.remove()
            except (RuntimeError, ValueError):
                pass  # Widget may already be removed
            finally:
                self._streaming_widget = None

    def _update_streaming_after_refresh(self, content: str):
        """Update markdown and scroll after widget refresh."""
        if self._streaming_widget:
            # Update markdown content
            try:
                markdown_widget = self._streaming_widget.query_one("Markdown")
                if markdown_widget and isinstance(markdown_widget, Markdown):
                    markdown_widget.update(content)
            except (ValueError, AttributeError, RuntimeError, NoMatches):
                # Markdown widget not found or not ready, ignore
                pass

            # Handle scrolling
            self.scroll_end(animate=False)
            if self._streaming_widget.is_mounted:
                try:
                    self.scroll_to_widget(self._streaming_widget, animate=False)
                except (ValueError, RuntimeError):
                    # Widget may not be mounted or visible
                    pass

    def clear_streaming_widget(self):
        """Public method to clear streaming widget."""
        self._clear_streaming_widget()

    def increment_message_count(self):
        """Increment the expected message count to avoid duplicates."""
        self._last_message_count += 1
        Settings.logger.debug(
            f"Incremented message count to {self._last_message_count}"
        )

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
        except (RuntimeError, ValueError, AttributeError):
            # Ignore errors during cleanup in destructor
            pass

    def get_message_count(self) -> int:
        """Get the total number of messages."""
        return len(self.messages)

    def get_last_message(self) -> Optional[ChatMessage]:
        """Get the last message widget."""
        return self.messages[-1] if self.messages else None

    def is_streaming_active(self) -> bool:
        """Check if streaming or thinking is currently active."""
        return (self._streaming_widget is not None) or (
            self._thinking_widget is not None
        )
