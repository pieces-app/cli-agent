"""Status bar widget for displaying application state and context."""

from typing import Optional, TYPE_CHECKING
from textual.reactive import reactive
from textual.widgets import Footer

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.models.model import Model


class StatusBar(Footer):
    """Status bar showing model info and keybindings."""

    current_model: reactive[str] = reactive("Unknown")
    temp_message: reactive[str] = reactive("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_mount(self) -> None:
        """Called when the widget is mounted."""
        super().on_mount()
        self.refresh()

    def watch_current_model(self, old_model: str, new_model: str) -> None:
        """React to model changes."""
        self.refresh()

    def render(self):
        """Render the footer with keybindings and model info."""
        # Get the original Footer rendering (keybindings)
        footer = super().render()
        
        # Add our status text after the keybindings
        status_text = self._build_status_text()
        
        if footer:
            return f"{footer} • {status_text}"
        else:
            return status_text

    def _build_status_text(self) -> str:
        """Build the status text string."""
        model_name = (
            self.current_model if self.current_model != "Unknown" else "No model"
        )
        model_name = model_name.replace("Chat Model", "")
        if model_name and len(model_name) > 20:
            model_name = model_name[:17] + "..."

        status_parts = [f"🤖 {model_name}"]
        
        if self.temp_message:
            status_parts.append(f"ℹ️ {self.temp_message}")
        
        return " • ".join(status_parts)

    def update_model_info(self, model: Optional["Model"] = None):
        """Update the current model information."""
        if model and hasattr(model, 'name'):
            self.current_model = model.name
        else:
            self.current_model = "Unknown"

    def show_temporary_message(self, message: str, duration: float = 3.0):
        """Show a temporary message in the status bar alongside the model."""
        self.temp_message = message
        
        self.set_timer(
            duration,
            lambda: setattr(self, "temp_message", ""),
        )
