"""Main TUI application for Pieces CLI."""

from typing import Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Header, Static

from pieces.settings import Settings
from .widgets import ChatViewPanel, ChatInput, ChatListPanel, StatusBar
from .controllers import EventHub
from .messages import (
    ChatMessages,
    UserMessages,
    ModelMessages,
    CopilotMessages,
    ConnectionMessages,
    ContextMessages,
)


class PiecesTUI(App):
    """Main TUI application for Pieces CLI."""

    DEFAULT_CSS = """
    Screen {
        background: $background;
        color: $text;
    }
    
    .chat-container {
        dock: top;
        height: 1fr;
    }
    
    .input-container {
        dock: bottom;
        height: 3;
        background: $surface;
        border-top: solid $primary;
    }
    
    .chat-layout {
        width: 100%;
        height: 100%;
    }
    
    .chat-layout-with-sidebar .chat-view {
        width: 75%;
    }
    
    .chat-layout-with-sidebar .chat-list {
        width: 25%;
    }
    
    .chat-layout-no-sidebar .chat-view {
        width: 100%;
    }
    
    .chat-layout-no-sidebar .chat-list {
        display: none;
    }
    
    .hidden {
        display: none;
    }
    
    .highlighted {
        background: $accent;
        color: $text;
    }
    
    .error {
        color: $error;
        text-style: bold;
    }
    
    .success {
        color: $success;
        text-style: bold;
    }
    
    .warning {
        color: $warning;
        text-style: bold;
    }
    
    .welcome-message {
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
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+n", "new_chat", "New Chat"),
        Binding("ctrl+r", "refresh", "Refresh"),
        Binding("ctrl+s", "toggle_sidebar", "Toggle Sidebar"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chat_view_panel: Optional[ChatViewPanel] = None
        self.chat_list_panel: Optional[ChatListPanel] = None
        self.chat_input: Optional[ChatInput] = None
        self.status_bar: Optional[StatusBar] = None
        self.event_hub: Optional[EventHub] = None
        self.sidebar_visible = True  # Track sidebar state
        self.main_layout: Optional[Horizontal] = None

    # Status bar helper methods to reduce code duplication
    def _update_status_connection(self, is_connected: bool):
        """Update connection status in status bar."""
        if self.status_bar:
            self.status_bar.update_connection_status(is_connected=is_connected)

    def _update_status_model(self, model_info):
        """Update model info in status bar."""
        if self.status_bar:
            self.status_bar.update_model_info(model_info)

    def _show_status_message(self, message: str, duration: int = 3):
        """Show temporary message in status bar."""
        if self.status_bar:
            self.status_bar.show_temporary_message(message, duration)

    def compose(self) -> ComposeResult:
        """Compose the main application layout."""
        yield Header(name="Pieces Copilot")

        # Main content area - chat list on left, chat view on right
        self.main_layout = Horizontal(classes="chat-layout chat-layout-with-sidebar")
        with self.main_layout:
            # Chat list panel (25% width)
            self.chat_list_panel = ChatListPanel(classes="chat-list")
            yield self.chat_list_panel

            # Main chat view panel (75% width)
            self.chat_view_panel = ChatViewPanel(classes="chat-view")
            yield self.chat_view_panel

        yield self.main_layout

        # Input area at bottom (above status bar)
        self.chat_input = ChatInput()
        yield self.chat_input

        self.status_bar = StatusBar()
        yield self.status_bar

    def on_mount(self) -> None:
        """Initialize the application when mounted."""
        self.title = "Pieces CLI - TUI Mode"

        # Initialize event hub (which manages all controllers)
        self.event_hub = EventHub(self)
        self.event_hub.initialize()

        # Update initial status using EventHub convenience methods
        # Connection status
        self._update_status_connection(is_connected=self.event_hub.is_connected())

        # Model info
        current_model = self.event_hub.get_current_model()
        self._update_status_model(current_model)

        # Load chats
        self._load_chats()

        # Load current chat if exists
        current_chat = self.event_hub.get_current_chat()
        if current_chat and self.chat_view_panel:
            self.chat_view_panel.load_conversation(current_chat)
        else:
            # Add welcome message for new chat - not as system role
            if self.chat_view_panel:
                self._show_welcome_message()

    def _load_chats(self):
        """Load chats into the chats panel."""
        if not self.chat_list_panel or not self.event_hub:
            Settings.logger.info(
                "Cannot load chats: missing chat_list_panel or event_hub"
            )
            return

        try:
            chats = self.event_hub.get_chats()
            Settings.logger.info(f"Found {len(chats)} chats to load")
            self.chat_list_panel.load_chats(chats)

            # Set active chat if there's a current one
            current_chat = self.event_hub.get_current_chat()
            if current_chat:
                self.chat_list_panel.set_active_chat(current_chat)
                Settings.logger.info(f"Set active chat: {current_chat.name}")

        except Exception as e:
            Settings.logger.critical(f"Error loading chats: {e}")

    async def on_user_messages_input_submitted(
        self, message: UserMessages.InputSubmitted
    ) -> None:
        """Handle user input submission."""
        Settings.logger.info(f"App: User submitted question: {message.text[:50]}...")
        if not self.chat_view_panel or not self.event_hub:
            Settings.logger.info("Missing chat_view_panel or event_hub for user input")
            return

        # Remove welcome message if it exists
        try:
            welcome_widget = self.chat_view_panel.query_one("#welcome-static", Static)
            if welcome_widget:
                welcome_widget.remove()
        except:
            pass  # Welcome message not found, that's fine

        # Add user message to chat with timestamp
        from datetime import datetime

        timestamp = datetime.now().strftime("Today %I:%M %p")
        self.chat_view_panel.add_message("user", message.text, timestamp=timestamp)

        # Send to copilot through EventHub
        Settings.logger.info("Sending question to EventHub...")
        self.event_hub.ask_question(message.text)

    async def on_chat_messages_new_requested(
        self, message: ChatMessages.NewRequested
    ) -> None:
        """Handle new chat request."""
        self.action_new_chat()

    async def on_chat_messages_selected(self, message: ChatMessages.Selected) -> None:
        """Handle chat selection - this will trigger a Switched message."""
        pass

    async def on_chat_messages_switched(self, message: ChatMessages.Switched) -> None:
        """Handle chat switched."""
        if self.chat_view_panel:
            if message.chat:
                # Load existing conversation
                self.chat_view_panel.load_conversation(message.chat)
            else:
                # None chat means new chat - show welcome message
                self.chat_view_panel.clear_messages()
                self.chat_view_panel.border_title = "Chat: New Conversation"
                self._show_welcome_message()

        if self.chat_input:
            self.chat_input.focus()

    async def on_chat_messages_updated(self, message: ChatMessages.Updated) -> None:
        """Handle chat updated from backend."""
        if not message.chat:
            # None chat in update message doesn't make sense, log and return
            Settings.logger.info("Received chat update with None chat - ignoring")
            return

        if self.chat_list_panel:
            # Check if this chat already exists in our list
            chat_exists = any(
                chat.id == message.chat.id for chat, _, _ in self.chat_list_panel.chats
            )

            title = message.chat.name
            summary = message.chat.summary or ""

            if chat_exists:
                # Update existing chat efficiently
                self.chat_list_panel.update_chat(message.chat, title, summary)
            else:
                # This is a new chat - add it to the list
                self.chat_list_panel.add_chat(message.chat, title, summary)
                self._show_status_message(f"📝 New chat: {title}")

            # If this is the active chat, update the view panel incrementally
            if (
                self.chat_view_panel
                and self.chat_list_panel.active_chat == message.chat
            ):
                Settings.logger.info(
                    f"Using incremental update for active chat: {message.chat.name}"
                )
                self.chat_view_panel.update_conversation_incrementally(message.chat)

    async def on_chat_messages_deleted(self, message: ChatMessages.Deleted) -> None:
        """Handle chat deleted from backend."""
        if self.chat_list_panel:
            # Remove the chat from the list efficiently
            self.chat_list_panel.remove_chat(message.chat)

            # If this was the active chat, clear the view and switch to another
            if self.chat_list_panel.active_chat == message.chat:
                if self.chat_view_panel:
                    self.chat_view_panel.clear_messages()
                    self.chat_view_panel.border_title = "Chat"

                # Try to switch to the first available chat
                if self.chat_list_panel.chats:
                    first_chat = self.chat_list_panel.chats[0][0]
                    self.chat_list_panel.set_active_chat(first_chat)
                    if self.chat_view_panel:
                        self.chat_view_panel.load_conversation(first_chat)
                else:
                    self.chat_list_panel.set_active_chat(None)

    async def on_model_messages_changed(self, message: ModelMessages.Changed) -> None:
        """Handle model change."""
        self._update_status_model(message.new_model)
        self._show_status_message(f"🤖 Model changed to {message.new_model.name}")

    async def on_connection_messages_established(
        self, message: ConnectionMessages.Established
    ) -> None:
        """Handle connection established."""
        self._update_status_connection(is_connected=True)
        self._show_status_message(f"✅ Connected to {message.endpoint}")

    async def on_connection_messages_lost(
        self, message: ConnectionMessages.Lost
    ) -> None:
        """Handle connection lost."""
        self._update_status_connection(is_connected=False)
        reason = f": {message.reason}" if message.reason else ""
        self._show_status_message(f"❌ Connection lost{reason}", 5)

    async def on_copilot_messages_thinking_started(
        self, message: CopilotMessages.ThinkingStarted
    ) -> None:
        """Handle copilot thinking started."""
        Settings.logger.info(
            f"App: Received thinking started for question: {message.question[:50]}..."
        )
        if self.chat_view_panel:
            self.chat_view_panel.add_thinking_indicator()
        else:
            Settings.logger.info("No chat_view_panel available for thinking indicator")

    async def on_copilot_messages_stream_started(
        self, message: CopilotMessages.StreamStarted
    ) -> None:
        """Handle copilot stream started."""
        if self.chat_view_panel:
            self.chat_view_panel.add_streaming_message("assistant", message.text)

    async def on_copilot_messages_stream_chunk(
        self, message: CopilotMessages.StreamChunk
    ) -> None:
        """Handle copilot stream chunk."""
        if self.chat_view_panel:
            self.chat_view_panel.update_streaming_message(message.full_text)

    async def on_copilot_messages_stream_completed(
        self, message: CopilotMessages.StreamCompleted
    ) -> None:
        """Handle copilot stream completed."""
        if self.chat_view_panel:
            self.chat_view_panel.finalize_streaming_message()

    async def on_copilot_messages_stream_error(
        self, message: CopilotMessages.StreamError
    ) -> None:
        """Handle copilot stream error."""
        if self.chat_view_panel:
            self.chat_view_panel.add_message("system", f"❌ Error: {message.error}")

    async def on_context_messages_added(self, message: ContextMessages.Added) -> None:
        """Handle context added."""
        pass

    async def on_context_messages_removed(
        self, message: ContextMessages.Removed
    ) -> None:
        """Handle context removed."""
        pass

    async def on_context_messages_cleared(
        self, message: ContextMessages.Cleared
    ) -> None:
        """Handle context cleared."""
        self._show_status_message(f"🗑️ Cleared {message.count} context items")

    def action_new_chat(self):
        """Create a new chat."""
        if self.event_hub:
            # Create new chat through EventHub
            self.event_hub.create_new_chat()

        # Check if chat panel is already empty/new
        if self.chat_view_panel:
            # If there are no messages (except maybe welcome), this is already a new chat
            has_real_messages = len(self.chat_view_panel.messages) > 0

            # Clear the chat panel
            self.chat_view_panel.clear_messages()
            self.chat_view_panel.border_title = "Chat: New Conversation"

            # Only show welcome if there were actual messages before (not already new)
            if has_real_messages:
                self._show_welcome_message()

        # Clear active chat in sidebar
        if self.chat_list_panel:
            self.chat_list_panel.set_active_chat(None)

        # Focus the input
        if self.chat_input:
            self.chat_input.focus()

    def action_refresh(self):
        """Refresh the chats list."""
        self._load_chats()

        # Trigger connection check through EventHub
        if self.event_hub:
            self.event_hub.connection.reconnect()

        self._show_status_message("✅ Refreshed")

    def action_toggle_sidebar(self):
        """Toggle the sidebar visibility and adjust layout accordingly."""
        if self.chat_list_panel and self.main_layout:
            self.sidebar_visible = not self.sidebar_visible

            if self.sidebar_visible:
                # Show sidebar and adjust layout
                self.main_layout.remove_class("chat-layout-no-sidebar")
                self.main_layout.add_class("chat-layout-with-sidebar")
                status = "visible"
            else:
                # Hide sidebar and expand chat view
                self.main_layout.remove_class("chat-layout-with-sidebar")
                self.main_layout.add_class("chat-layout-no-sidebar")
                status = "hidden"

            self._show_status_message(f"📁 Sidebar {status}")

    def _show_welcome_message(self):
        """Show a welcoming help message as static centered text."""
        welcome_text = """🎯 Pieces TUI

Type your message below to start chatting, or use these shortcuts:

• Ctrl+N - New conversation  • Ctrl+S - Toggle sidebar
• Ctrl+R - Refresh

Ready to assist with code, questions, and more!"""

        if self.chat_view_panel:
            # Remove any existing welcome message first to prevent duplicates
            try:
                existing_welcome = self.chat_view_panel.query_one(
                    "#welcome-static", Static
                )
                if existing_welcome:
                    existing_welcome.remove()
            except:
                pass  # No existing welcome message, that's fine

            # Add welcome as a static widget, not a message
            welcome_widget = Static(
                welcome_text, classes="welcome-message", id="welcome-static"
            )
            self.chat_view_panel.mount(welcome_widget)

    def on_unmount(self):
        """Clean up when app is unmounted."""
        try:
            # Clean up event hub and controllers
            if self.event_hub:
                self.event_hub.cleanup()
                self.event_hub = None

            # Clean up widgets
            if self.chat_view_panel:
                self.chat_view_panel.cleanup()

            # Clear widget references
            self.chat_view_panel = None
            self.chat_list_panel = None
            self.chat_input = None
            self.status_bar = None

        except Exception as e:
            Settings.logger.error(f"Error during app cleanup: {e}")

    def __del__(self):
        """Ensure cleanup is called when app is destroyed."""
        try:
            self.on_unmount()
        except Exception:
            # Ignore errors during cleanup in destructor
            pass


def run_tui():
    """Run the TUI application."""
    from pieces import __version__

    if __version__ == "dev":
        # In dev when we are running 'textual run --dev pieces.tui.app:run_tui' the cli needs to be initialized
        # Because we skip the main cli entry point
        Settings.startup()
    app = PiecesTUI()
    app.run()


if __name__ == "__main__":
    run_tui()
