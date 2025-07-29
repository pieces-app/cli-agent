"""Status bar widget for displaying application state and context."""

from typing import Optional, TYPE_CHECKING
from textual.reactive import reactive
from textual.widgets import Footer, Static
from textual.app import ComposeResult

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.models.model import Model
    from textual.screen import Screen


class StatusBar(Footer):
    """Status bar showing connection status, model info, and context, plus keybindings."""

    connection_status: reactive[str] = reactive("Disconnected")
    current_model: reactive[str] = reactive("Unknown")
    context_count: reactive[int] = reactive(0)
    current_chat: reactive[Optional[str]] = reactive(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._status_widget: Optional[Static] = None
        self._update_status()

    def compose(self) -> ComposeResult:
        # Add our custom status widget first
        self._status_widget = Static(self._build_status_text(), classes="status-text")
        yield self._status_widget
        
        # Then yield Footer's keybindings (only if bindings are ready)
        yield from super().compose()

    async def bindings_changed(self, screen: "Screen") -> None:
        """Called when bindings change - recompose to show both status and keybindings."""
        # Call parent to handle binding logic
        await super().bindings_changed(screen)
        
        # Force recompose to show both status widget and keybindings
        if self.is_attached and self._bindings_ready:
            await self.recompose()

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
