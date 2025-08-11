"""Main TUI application for Pieces CLI."""

from typing import Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Header, Static
from textual.css.query import NoMatches

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
from pieces._vendor.pieces_os_client.wrapper.streamed_identifiers import (
    ConversationsSnapshot,
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
                self.call_later(self._show_welcome_message)

    def _load_chats(self):
        """Load chats into the chats panel."""
        if not self.chat_list_panel or not self.event_hub:
            Settings.logger.info(
                "Cannot load chats: missing chat_list_panel or event_hub"
            )
            return

        try:
            chats = Settings.pieces_client.copilot.chats()
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
        """Handle user input submission - delegates to backend, no UI updates."""
        Settings.logger.info(f"App: User submitted question: {message.text[:50]}...")
        if not self.event_hub:
            Settings.logger.info("Missing event_hub for user input")
            return

        # Remove welcome message and show user input immediately for feedback
        if self.chat_view_panel:
            try:
                welcome_widget = self.chat_view_panel.query_one("#welcome-static")
                if welcome_widget:
                    await welcome_widget.remove()
            except NoMatches:
                pass  # Welcome message not found, that's fine

            # Show user message immediately for instant feedback
            from datetime import datetime

            timestamp = datetime.now().strftime("Today %I:%M %p")
            self.chat_view_panel.add_message("user", message.text, timestamp=timestamp)
            # Increment the expected message count to avoid duplicates
            self.chat_view_panel.increment_message_count()
            Settings.logger.info(
                f"Added user message immediately for feedback: {message.text[:50]}..."
            )

        # Simply delegate to backend - let it handle chat creation and all updates
        Settings.logger.info("Sending question to EventHub...")
        self.event_hub.ask_question(message.text)

    async def on_chat_messages_switched(self, message: ChatMessages.Switched) -> None:
        """Handle chat switch event from backend."""
        if self.chat_view_panel:
            Settings.logger.info(
                f"Updating conversation: {message.chat.id} - {message.chat.name}"
            )
            if message.chat:
                Settings.pieces_client.copilot.chat = message.chat
                # Check if we're in the middle of streaming - if so, don't reload yet
                has_streaming_widget = (
                    hasattr(self.chat_view_panel, "_streaming_widget")
                    and self.chat_view_panel._streaming_widget
                )
                has_thinking_widget = (
                    hasattr(self.chat_view_panel, "_thinking_widget")
                    and self.chat_view_panel._thinking_widget
                )

                if has_streaming_widget or has_thinking_widget:
                    Settings.logger.info(
                        "In middle of streaming/thinking, deferring conversation load"
                    )
                    self.chat_view_panel.border_title = f"Chat: {message.chat.name}"
                else:
                    # Normal case - load the full conversation
                    Settings.logger.info("Loading full conversation")
                    self.chat_view_panel.load_conversation(message.chat)
            else:
                # None chat means new chat - show welcome message
                self.chat_view_panel.clear_messages()
                self.chat_view_panel.border_title = "Chat: New Conversation"
                await self._show_welcome_message()

        # Update the active chat in the sidebar
        if self.chat_list_panel and message.chat:
            self.chat_list_panel.set_active_chat(message.chat)

        if self.chat_input:
            self.chat_input.focus()

    async def on_chat_messages_updated(self, message: ChatMessages.Updated) -> None:
        """Handle chat update event from backend."""
        if not message.chat:
            Settings.logger.info("Received chat update with None chat - ignoring")
            return

        if self.chat_list_panel:
            try:
                message.chat.id
            except AttributeError:
                return  # Chat is deleted or not valid
            chat_exists = message.chat.id in self.chat_list_panel._chat_widgets

            title = message.chat.name
            summary = message.chat.summary or ""

            if chat_exists:
                self.chat_list_panel.update_chat(message.chat, title, summary)
            else:
                if ConversationsSnapshot.first_shot:
                    self.chat_list_panel.add_chat(message.chat, title, summary)
                else:
                    # New chat created - add at top
                    self.chat_list_panel.add_chat_at_top(message.chat, title, summary)
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
        """Handle chat deletion event from backend."""
        if self.chat_list_panel:
            active_chat_id = None
            try:
                if self.chat_list_panel.active_chat:
                    active_chat_id = self.chat_list_panel.active_chat.id
            except (AttributeError, RuntimeError):
                pass

            self.chat_list_panel.remove_chat(message.chat_id)

            # If this was the active chat, clear the view
            if active_chat_id == message.chat_id:
                if self.chat_view_panel:
                    self.chat_view_panel.clear_messages()
                    self.chat_view_panel.border_title = "Chat"
                    await self._show_welcome_message()

    async def on_model_messages_changed(self, message: ModelMessages.Changed) -> None:
        """Handle model change."""
        self._update_status_model(message.new_model)
        self._show_status_message(f"🤖 Model changed to {message.new_model.name}")

    async def on_connection_messages_established(
        self, _: ConnectionMessages.Established
    ) -> None:
        """Handle connection established."""
        self._show_status_message("✅ Connected")

    async def on_connection_messages_lost(self, _: ConnectionMessages.Lost) -> None:
        """Handle connection lost."""
        self._show_status_message("❌ Connection lost", 5)

    async def on_copilot_messages_thinking_started(
        self, _: CopilotMessages.ThinkingStarted
    ) -> None:
        """Handle copilot thinking started."""
        Settings.logger.info("App: Received thinking started for question:")
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
        self, _: CopilotMessages.StreamCompleted
    ) -> None:
        """Handle copilot stream completion."""
        # Finalize the streaming message to convert it to a permanent message
        if self.chat_view_panel:
            self.chat_view_panel.finalize_streaming_message()

    async def on_copilot_messages_stream_error(
        self, message: CopilotMessages.StreamError
    ) -> None:
        """Handle copilot stream error."""
        if self.chat_view_panel:
            self.chat_view_panel.add_message("system", f"❌ Error: {message.error}")

    async def on_chat_messages_new_requested(
        self, _: ChatMessages.NewRequested
    ) -> None:
        """Handle new chat request from button."""
        await self.action_new_chat()

    async def on_context_messages_cleared(
        self, message: ContextMessages.Cleared
    ) -> None:
        """Handle context cleared."""
        self._show_status_message(f"🗑️ Cleared {message.count} context items")

    async def action_new_chat(self):
        """Request creation of a new chat."""
        if self.event_hub:
            # Create new chat through EventHub - let backend handle everything
            self.event_hub.create_new_chat()

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

    async def _show_welcome_message(self):
        """Show a welcoming help message as static centered text."""
        welcome_text = """🎯 Pieces TUI

Type your message below to start chatting, or use these shortcuts:

• Ctrl+N - New conversation  • Ctrl+S - Toggle sidebar
• Ctrl+R - Refresh

Ready to assist with code, questions, and more!"""

        if self.chat_view_panel:
            # Remove any existing welcome message first to prevent duplicates
            try:
                existing_welcome = self.chat_view_panel.query_one("#welcome-static")
                if existing_welcome:
                    await existing_welcome.remove()
            except NoMatches:
                # No existing welcome message found, that's fine
                pass

            # Always add a fresh welcome message
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
        except (RuntimeError, ValueError, AttributeError):
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
