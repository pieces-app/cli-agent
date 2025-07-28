"""Main TUI application for Pieces CLI."""

from typing import Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.widgets import Header

from pieces.settings import Settings
from .styles import FULL_CSS
from .widgets import ChatPanel, ChatInput, ChatsPanel, StatusBar
from .widgets.chats_panel import ChatMessages
from .controllers import EventHub, EventType


class PiecesTUI(App):
    """Main TUI application for Pieces CLI."""

    CSS = FULL_CSS

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+n", "new_chat", "New Chat"),
        Binding("ctrl+l", "focus_chats", "Focus Chats"),
        Binding("ctrl+r", "refresh", "Refresh"),
        Binding("ctrl+s", "toggle_sidebar", "Toggle Sidebar"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chat_panel: Optional[ChatPanel] = None
        self.chats_panel: Optional[ChatsPanel] = None
        self.chat_input: Optional[ChatInput] = None
        self.status_bar: Optional[StatusBar] = None
        self.event_hub: Optional[EventHub] = None

    def compose(self) -> ComposeResult:
        """Compose the main application layout."""
        yield Header(name="Pieces Copilot")

        # Main content area - chats on left, chat on right
        with Horizontal():
            # Chats panel (25% width)
            self.chats_panel = ChatsPanel()
            yield self.chats_panel

            # Main chat panel (75% width)
            self.chat_panel = ChatPanel()
            yield self.chat_panel

        # Input area at bottom
        self.chat_input = ChatInput()
        yield self.chat_input

        # Status bar
        self.status_bar = StatusBar()
        yield self.status_bar

    def on_mount(self) -> None:
        """Initialize the application when mounted."""
        self.title = "Pieces CLI - TUI Mode"

        # Initialize event hub
        self.event_hub = EventHub(self)
        self.event_hub.initialize()
        self._setup_event_listeners()

        # Update initial status
        if self.status_bar:
            # Connection status
            self.status_bar.update_connection_status(
                is_connected=self.event_hub.connection.is_connected()
            )
            # Model info
            current_model = self.event_hub.model.get_current_model()
            self.status_bar.update_model_info(current_model)

        # Load chats
        self._load_chats()

        # Load current chat if exists
        current_chat = self.event_hub.copilot.get_current_chat()
        if current_chat and self.chat_panel:
            self.chat_panel.load_conversation(current_chat)
            if self.status_bar:
                self.status_bar.update_chat_info(current_chat)
        else:
            # Add welcome message for new chat
            if self.chat_panel:
                self.chat_panel.add_message(
                    "system",
                    "Welcome to Pieces CLI TUI! Type your questions below or press ? for help.",
                )
            if self.status_bar:
                self.status_bar.update_chat_info(None)

    def _load_chats(self):
        """Load chats into the chats panel."""
        if not self.chats_panel or not self.event_hub:
            return

        try:
            chats = self.event_hub.chat.get_chats()
            self.chats_panel.load_chats(chats)

            # Set active chat if there's a current one
            current_chat = self.event_hub.copilot.get_current_chat()
            if current_chat:
                self.chats_panel.set_active_chat(current_chat)

        except Exception as e:
            Settings.logger.critical(f"Error loading chats: {e}")

    async def on_chat_input_message_submitted(
        self, message: ChatInput.MessageSubmitted
    ) -> None:
        """Handle chat message submission."""
        if not self.chat_panel or not self.event_hub:
            return

        user_message = message.text.strip()
        if not user_message:
            return

        # Add user message to chat with timestamp
        from datetime import datetime

        timestamp = datetime.now().strftime("Today %I:%M %p")
        self.chat_panel.add_message("user", user_message, timestamp=timestamp)

        # Send to copilot through controller
        self.event_hub.copilot.ask_question(user_message)

    async def on_chat_messages_new_chat_requested(
        self, message: ChatMessages.NewChatRequested
    ) -> None:
        """Handle new chat request."""
        self.action_new_chat()

    async def on_chat_messages_chat_switched(
        self, message: ChatMessages.ChatSwitched
    ) -> None:
        """Handle chat switch."""
        if self.event_hub:
            # Switch chat through controller
            self.event_hub.chat.switch_chat(message.chat)

            # Load the conversation in the chat panel
            if self.chat_panel:
                self.chat_panel.load_conversation(message.chat)

            # Update status bar
            if self.status_bar:
                self.status_bar.update_chat_info(message.chat)

            # Focus the input
            if self.chat_input:
                self.chat_input.focus()

    def action_new_chat(self):
        """Create a new chat."""
        if self.event_hub:
            # Create new chat through controller
            self.event_hub.chat.create_new_chat()

        # Clear the chat panel
        if self.chat_panel:
            self.chat_panel.clear_messages()
            self.chat_panel.border_title = "Chat: New Conversation"
            self.chat_panel.add_message(
                "system", "New conversation started. Ask me anything!"
            )

        # Update status bar
        if self.status_bar:
            self.status_bar.update_chat_info(None)

        # Clear active chat in sidebar
        if self.chats_panel:
            self.chats_panel.set_active_chat(None)

        # Focus the input
        if self.chat_input:
            self.chat_input.focus()

    def action_refresh(self):
        """Refresh the chats list."""
        self._load_chats()

        # Trigger connection check
        if self.event_hub:
            self.event_hub.connection.reconnect()

        if self.status_bar:
            self.status_bar.show_temporary_message("✅ Refreshed")

    def action_focus_chats(self):
        """Focus the chats panel."""
        if self.chats_panel:
            self.chats_panel.focus()

    def action_toggle_sidebar(self):
        """Toggle the sidebar visibility."""
        if self.chats_panel:
            self.chats_panel.display = not self.chats_panel.display
            if self.status_bar:
                status = "visible" if self.chats_panel.display else "hidden"
                self.status_bar.show_temporary_message(f"📁 Sidebar {status}")

    def _setup_event_listeners(self):
        """Set up event listeners for controllers."""
        if not self.event_hub:
            return

        # Connection events
        self.event_hub.connection.on(
            EventType.CONNECTION_ESTABLISHED, self._on_connection_established
        )
        self.event_hub.connection.on(
            EventType.CONNECTION_LOST, self._on_connection_lost
        )

        # Chat events
        self.event_hub.chat.on(EventType.CHAT_UPDATED, self._on_chat_updated)
        self.event_hub.chat.on(EventType.CHAT_DELETED, self._on_chat_deleted)

        # Model events
        self.event_hub.model.on(EventType.MODEL_CHANGED, self._on_model_changed)

        # Context events
        self.event_hub.material.on(EventType.CONTEXT_ADDED, self._on_context_changed)
        self.event_hub.material.on(EventType.CONTEXT_REMOVED, self._on_context_changed)
        self.event_hub.material.on(EventType.CONTEXT_CLEARED, self._on_context_changed)

        # Copilot events
        self.event_hub.copilot.on(
            EventType.COPILOT_THINKING_STARTED, self._on_thinking_started
        )
        self.event_hub.copilot.on(
            EventType.COPILOT_THINKING_ENDED, self._on_thinking_ended
        )
        self.event_hub.copilot.on(
            EventType.COPILOT_STREAM_STARTED, self._on_stream_started
        )
        self.event_hub.copilot.on(EventType.COPILOT_STREAM_CHUNK, self._on_stream_chunk)
        self.event_hub.copilot.on(
            EventType.COPILOT_STREAM_COMPLETED, self._on_stream_completed
        )
        self.event_hub.copilot.on(EventType.COPILOT_STREAM_ERROR, self._on_stream_error)

    def _on_chat_created(self, chat):
        """Handle new chat created."""
        # Refresh the chats list
        self._load_chats()

    def _on_chat_updated(self, chat):
        """Handle chat updated."""
        # Update chats list
        self._load_chats()

        # Update current chat if it's the one being updated
        current_chat = getattr(Settings.pieces_client.copilot, "chat", None)
        if current_chat and current_chat.conversation == chat.id:
            if self.status_bar:
                self.status_bar.update_chat_info(current_chat)

    def _on_chat_deleted(self, chat):
        """Handle chat deleted."""
        # If deleted chat was active, switch to new chat
        current_chat = getattr(Settings.pieces_client.copilot, "chat", None)
        if current_chat and current_chat.conversation == chat.id:
            self.action_new_chat()

    def _on_model_changed(self, data):
        """Handle model change."""
        if self.status_bar:
            self.status_bar.update_model_info(data["new_model"])
            self.status_bar.show_temporary_message(
                f"🤖 Model changed to {data['new_model']}"
            )

    def _on_context_changed(self, data):
        """Handle context change."""
        if self.status_bar and self.event_hub:
            materials = len(self.event_hub.material.get_context_materials())
            self.status_bar.update_context_count(materials=materials)

    def _on_connection_established(self, data):
        """Handle connection established."""
        if self.status_bar:
            self.status_bar.update_connection_status(is_connected=True)

    def _on_connection_lost(self, data):
        """Handle connection lost."""
        if self.status_bar:
            self.status_bar.update_connection_status(is_connected=False)
            self.status_bar.show_temporary_message("❌ Connection lost", 5)

    def _on_thinking_started(self, data):
        """Handle copilot thinking started."""
        if self.chat_panel:
            self.chat_panel.add_thinking_indicator()

    def _on_thinking_ended(self, data):
        """Handle copilot thinking ended."""
        # Thinking indicator will be removed when stream starts
        pass

    def _on_stream_started(self, data):
        """Handle stream started."""
        if self.chat_panel:
            self.chat_panel.add_streaming_message("assistant", data["text"])

    def _on_stream_chunk(self, data):
        """Handle stream chunk."""
        if self.chat_panel:
            self.chat_panel.update_streaming_message(data["full_text"])

    def _on_stream_completed(self, data):
        """Handle stream completed."""
        if self.chat_panel:
            self.chat_panel.finalize_streaming_message()

    def _on_stream_error(self, data):
        """Handle stream error."""
        if self.chat_panel:
            error_msg = data.get("error", "Unknown error")
            self.chat_panel.add_message("system", f"❌ Error: {error_msg}")

    def on_unmount(self):
        """Clean up when app is unmounted."""
        if self.event_hub:
            self.event_hub.cleanup()


def run_tui():
    """Run the TUI application."""
    app = PiecesTUI()
    app.run()


if __name__ == "__main__":
    run_tui()
