"""Status bar widget for displaying application state and context."""

from typing import Optional, TYPE_CHECKING
from textual.reactive import reactive
from textual.app import ComposeResult
from textual.widgets import Footer
from textual.widget import Widget

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.models.model import Model

# Constants
MAX_MODEL_NAME_LENGTH = 20


class StatusText(Widget):
    """Widget to display status text in the footer."""

    def __init__(self, text: str = "", **kwargs):
        super().__init__(**kwargs)
        self._text = text

    def render(self) -> str:
        return self._text

    def update_text(self, text: str) -> None:
        """Update the status text."""
        self._text = text
        self.refresh()


class StatusBar(Footer):
    """Status bar showing model info and keybindings."""

    DEFAULT_CSS = """
    StatusBar {
        StatusText {
            width: auto;
            height: 1;
            padding: 0 2;
            color: $footer-description-foreground;
            background: $footer-description-background;
            border-right: vkey $foreground 20%;
        }
    }
    """

    current_model: reactive[str] = reactive("Unknown")
    temp_message: reactive[str] = reactive("")
    ltm_enabled: reactive[bool] = reactive(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._status_widget: Optional[StatusText] = None

    def compose(self) -> ComposeResult:
        """Compose the footer with status text and key bindings."""
        if not self._bindings_ready:
            return

        yield from super().compose()

        self._status_widget = StatusText(
            self._build_status_text(), classes="status-text"
        )
        yield self._status_widget

        self.styles.grid_size_columns += 1

    def _build_status_text(self) -> str:
        """Build the status text string."""
        model_name = (
            self.current_model if self.current_model != "Unknown" else "No model"
        )
        model_name = model_name.replace("Chat Model", "")
        status_parts = []
        if model_name:
            if len(model_name) > MAX_MODEL_NAME_LENGTH:
                model_name = model_name[: MAX_MODEL_NAME_LENGTH - 3] + "..."
            status_parts.append(f"🤖 {model_name}")

        # Add LTM status - only show when enabled
        if self.ltm_enabled:
            status_parts.append("🧠 LTM enabled")

        if self.temp_message:
            status_parts.append(self.temp_message)

        return " • ".join(status_parts)

    def watch_current_model(self, current_model: str) -> None:
        """Update display when model changes."""
        if self._status_widget:
            self._status_widget.update_text(self._build_status_text())

    def watch_temp_message(self, temp_message: str) -> None:
        """Update display when temp message changes."""
        if self._status_widget:
            self._status_widget.update_text(self._build_status_text())

    def watch_ltm_enabled(self, ltm_enabled: bool) -> None:
        """Update display when LTM status changes."""
        if self._status_widget:
            self._status_widget.update_text(self._build_status_text())

    def update_model_info(self, model: Optional["Model"] = None):
        """Update the current model information."""
        if model and hasattr(model, "name"):
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

    def update_ltm_status(self, enabled: bool):
        """Update the LTM status indicator."""
        self.ltm_enabled = enabled
