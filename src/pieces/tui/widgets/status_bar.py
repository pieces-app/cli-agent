"""Status bar widget for displaying application state and context."""

from typing import Optional, TYPE_CHECKING
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import Footer, Static
from textual.app import ComposeResult

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.wrapper.basic_identifier.chat import BasicChat
    from pieces._vendor.pieces_os_client.models.model import Model


class StatusBar(Footer):
    """Status bar showing connection status, model info, and context, plus keybindings."""

    connection_status: reactive[str] = reactive("Disconnected")
    current_model: reactive[str] = reactive("Unknown")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._status_widget: Optional[Static] = None
        self._update_status()

    def compose(self) -> ComposeResult:
        # Add our custom status widget first
        # self._status_widget = Static(self._build_status_text())
        # yield self._status_widget

        # Then yield Footer's keybindings
        yield from super().compose()

    def _build_status_text(self) -> str:
        """Build the status text string."""
        connection_icon = "🟢" if self.connection_status == "Connected" else "🔴"

        model_name = (
            self.current_model if self.current_model != "Unknown" else "No model"
        )
        if model_name and len(model_name) > 20:
            model_name = model_name[:17] + "..."

        return f"{connection_icon} {self.connection_status} | 🤖 {model_name}"

    def _update_status(self):
        """Update the status widget with current information."""
        if self._status_widget:
            self._status_widget.update(self._build_status_text())

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

    def show_temporary_message(self, message: str, duration: float = 3.0):
        """Show a temporary message in the status bar."""
        if not self._status_widget:
            return

        # Store current status
        current_status = self._build_status_text()

        # Show temporary message
        self._status_widget.update(f"ℹ️ {message}")

        # Schedule restoration after duration
        self.set_timer(duration, lambda: self._status_widget.update(current_status))
