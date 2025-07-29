"""Status bar widget for displaying application state and context."""

from typing import Optional, TYPE_CHECKING
from textual.reactive import reactive
from textual.widgets import Footer

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.wrapper.basic_identifier.chat import BasicChat
    from pieces._vendor.pieces_os_client.models.model import Model


class StatusBar(Footer):
    """Status bar showing connection status, model info, and context."""

    connection_status: reactive[str] = reactive("Disconnected")
    current_model: reactive[str] = reactive("Unknown")
    context_count: reactive[int] = reactive(0)
    current_chat: reactive[Optional[str]] = reactive(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._update_status()

    def update(self, message: str):
        """Update the status bar with a message."""
        pass

    def _update_status(self):
        """Update the footer with current status information."""
        # Build status parts
        connection_icon = "🟢" if self.connection_status == "Connected" else "🔴"
        
        chat_name = self.current_chat if self.current_chat else "No chat"
        if chat_name and len(chat_name) > 15:
            chat_name = chat_name[:12] + "..."
            
        model_name = self.current_model if self.current_model != "Unknown" else "No model"
        if model_name and len(model_name) > 20:
            model_name = model_name[:17] + "..."
            
        context_text = f"{self.context_count} items" if self.context_count > 0 else "No context"
        
        # Combine all status information
        status_text = f"{connection_icon} {self.connection_status} | 💬 {chat_name} | 🤖 {model_name} | 📎 {context_text} | Press ? for help"
        
        # Update footer text
        self.update(status_text)

    def update_connection_status(self, is_connected: bool = False):
        """Update the connection status."""
        self.connection_status = "Connected" if is_connected else "Disconnected"
        self._update_status()

    def update_model_info(self, model: Optional["Model"] = None):
        """Update the current model information."""
        if model:
            self.current_model = model.name
        else:
            self.current_model = "Unknown"
        self._update_status()

    def update_chat_info(self, chat: Optional["BasicChat"] = None):
        """Update current chat information."""
        if chat:
            self.current_chat = chat.name if chat.name else "Untitled"
        else:
            self.current_chat = None
        self._update_status()

    def update_context_count(self, materials: int = 0, files: int = 0):
        """Update the context items count."""
        self.context_count = materials + files
        self._update_status()

    def show_temporary_message(self, message: str, duration: float = 3.0):
        """Show a temporary message in the status bar."""
        # Store current status
        current_status = f"🟢 {self.connection_status}" if self.connection_status == "Connected" else f"🔴 {self.connection_status}"
        
        # Show temporary message
        self.update(f"ℹ️ {message}")
        
        # Schedule restoration after duration
        self.set_timer(duration, lambda: self._update_status())
