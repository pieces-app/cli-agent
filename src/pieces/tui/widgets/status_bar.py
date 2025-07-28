"""Status bar widget for displaying application state and context."""

from typing import Optional, TYPE_CHECKING
from textual.reactive import reactive
from textual.widgets import Static
from textual.containers import Horizontal
from textual.app import ComposeResult

from pieces.settings import Settings

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.wrapper.basic_identifier.chat import BasicChat
    from pieces._vendor.pieces_os_client.models.model import Model


class StatusBar(Horizontal):
    """Status bar showing connection status, model info, and context."""

    connection_status: reactive[str] = reactive("Disconnected")
    current_model: reactive[str] = reactive("Unknown")
    context_count: reactive[int] = reactive(0)
    current_chat: reactive[Optional[str]] = reactive(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_class("status-bar")

    def compose(self) -> ComposeResult:
        """Compose the status bar layout."""
        # Connection status
        self.connection_widget = Static(
            "🔴 Disconnected", classes="status-item status-connection"
        )
        yield self.connection_widget

        # Current chat
        self.chat_widget = Static("💬 No chat", classes="status-item status-chat")
        yield self.chat_widget

        # Model info
        self.model_widget = Static(
            "🤖 Model: Unknown", classes="status-item status-model"
        )
        yield self.model_widget

        # Context count
        self.context_widget = Static(
            "📎 Context: 0 items", classes="status-item status-context"
        )
        yield self.context_widget

        # Spacer
        yield Static("", classes="status-spacer")

        # Help hint
        yield Static("Press ? for help", classes="status-item status-help")

    def on_mount(self):
        """Initialize status when mounted."""
        # Status will be updated by events from controllers
        pass

    def update_connection_status(self, is_connected: bool = False):
        """Update the connection status."""
        if is_connected:
            self.connection_status = "Connected"
            self.connection_widget.update("🟢 Connected")
            self.connection_widget.add_class("status-connected")
            self.connection_widget.remove_class("status-disconnected")
        else:
            self._set_disconnected()

    def _set_disconnected(self):
        """Set status to disconnected."""
        self.connection_status = "Disconnected"
        self.connection_widget.update("🔴 Disconnected")
        self.connection_widget.add_class("status-disconnected")
        self.connection_widget.remove_class("status-connected")

    def update_model_info(self, model: Optional["Model"] = None):
        """Update the current model information."""
        if model:
            self.current_model = model.name
            self.model_widget.update(f"🤖 Model: {model.name}")
        else:
            self.current_model = "Unknown"
            self.model_widget.update("🤖 Model: Unknown")

    def update_chat_info(self, chat: Optional["BasicChat"] = None):
        """Update current chat information."""
        if chat:
            chat_name = chat.name if chat.name else "Untitled"
            if len(chat_name) > 20:
                chat_name = chat_name[:17] + "..."
            self.current_chat = chat_name
            self.chat_widget.update(f"💬 {chat_name}")
        else:
            self.current_chat = None
            self.chat_widget.update("💬 New chat")

    def update_context_count(self, materials: int = 0, files: int = 0):
        """Update the context items count."""
        total = materials + files
        self.context_count = total

        if total == 0:
            self.context_widget.update("📎 No context")
        else:
            parts = []
            if materials > 0:
                parts.append(f"{materials} material{'s' if materials != 1 else ''}")
            if files > 0:
                parts.append(f"{files} file{'s' if files != 1 else ''}")

            context_text = " & ".join(parts)
            self.context_widget.update(f"📎 {context_text}")

    def show_temporary_message(self, message: str, duration: int = 3):
        """Show a temporary message in the status bar."""
        # Store current help text
        current_help = self.query_one(".status-help").renderable

        # Show temporary message
        help_widget = self.query_one(".status-help")
        help_widget.update(message)

        # Schedule restoration
        self.set_timer(duration, lambda: help_widget.update(current_help))
