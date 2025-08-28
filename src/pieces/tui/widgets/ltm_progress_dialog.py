"""LTM setup progress dialog using Rich widgets directly in Textual."""

from textual.app import ComposeResult
from textual.widgets import Static
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.containers import Vertical
from rich.progress import Progress, TextColumn
from pieces.copilot.ltm import ConditionalSpinnerColumn

import threading


class AutoRefreshProgress(Static):
    """Static widget that auto-refreshes when content changes."""

    def __init__(self, progress_obj, **kwargs):
        super().__init__(**kwargs)
        self.progress_obj = progress_obj
        self.update_content()
        self.set_interval(0.1, self.update_content)

    def update_content(self):
        """Update the content and refresh display."""
        self.update(self.progress_obj)

    def refresh_progress(self):
        """Force refresh the progress display."""
        self.update_content()


class LTMProgressDialog(ModalScreen):
    """LTM setup progress dialog using Rich widgets for exact CLI consistency."""

    DEFAULT_CSS = """
    LTMProgressDialog {
        align: center middle;
    }

    LTMProgressDialog > Vertical {
        width: 80;
        height: 12;
        border: thick $primary;
        background: $surface;
        padding: 2;
    }

    .rich-progress {
        height: 1fr;
        width: 1fr;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close", show=False),
        Binding("ctrl+c", "close", "Close", show=False),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rich_progress = None
        self._vision_task = None
        self._accessibility_task = None
        self._main_task = None

    def compose(self) -> ComposeResult:
        """Compose the progress dialog with Rich Progress widget."""
        # Create the Rich Progress widget exactly like CLI
        self.rich_progress = Progress(
            ConditionalSpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=False,
        )

        # Add the same tasks as CLI
        self._vision_task = self.rich_progress.add_task(
            "[cyan]Vision permission: checking..."
        )
        self._accessibility_task = self.rich_progress.add_task(
            "[cyan]Accessibility permission: checking..."
        )
        self._main_task = self.rich_progress.add_task(
            "[cyan]Checking PiecesOS permissions...", total=None
        )

        with Vertical():
            self.progress_widget = AutoRefreshProgress(
                self.rich_progress, id="rich-progress", classes="rich-progress"
            )
            yield self.progress_widget

    def call_from_thread(self, callback):
        """Thread-safe method to call UI updates."""
        self.app.call_later(callback)

    def update_main_status(self, message: str):
        """Update the main status message."""

        def update():
            try:
                if self.rich_progress is not None and self._main_task is not None:
                    self.rich_progress.update(
                        self._main_task,
                        description=message,
                    )
                    self._refresh_display()
            except Exception:
                pass

        self.call_from_thread(update)

    def update_vision_status(self, enabled: bool):
        """Update vision permission status."""

        def update():
            try:
                if self.rich_progress is not None and self._vision_task is not None:
                    if enabled:
                        self.rich_progress.update(
                            self._vision_task,
                            description="[green]Vision permission: enabled",
                            completed=True,
                        )
                    else:
                        self.rich_progress.update(
                            self._vision_task,
                            description="[yellow]Vision permission: enabling...",
                        )
                    self._refresh_display()
            except Exception:
                pass

        self.call_from_thread(update)

    def update_accessibility_status(self, enabled: bool):
        """Update accessibility permission status."""

        def update():
            try:
                if (
                    self.rich_progress is not None
                    and self._accessibility_task is not None
                ):
                    if enabled:
                        self.rich_progress.update(
                            self._accessibility_task,
                            description="[green]Accessibility permission: enabled",
                            completed=True,
                        )
                    else:
                        self.rich_progress.update(
                            self._accessibility_task,
                            description="[yellow]Accessibility permission: enabling...",
                        )
                    self._refresh_display()
            except Exception:
                pass

        self.call_from_thread(update)

    def hide_vision_task(self):
        """Hide the vision task."""

        def update():
            try:
                if self.rich_progress is not None and self._vision_task is not None:
                    self.rich_progress.update(self._vision_task, visible=False)
                    self._refresh_display()
            except Exception:
                pass

        self.call_from_thread(update)

    def hide_accessibility_task(self):
        """Hide the accessibility task."""

        def update():
            try:
                if (
                    self.rich_progress is not None
                    and self._accessibility_task is not None
                ):
                    self.rich_progress.update(self._accessibility_task, visible=False)
                    self._refresh_display()
            except Exception:
                pass

        self.call_from_thread(update)

    def show_vision_task(self):
        """Show the vision task."""

        def update():
            try:
                if self.rich_progress is not None and self._vision_task is not None:
                    self.rich_progress.update(self._vision_task, visible=True)
                    self._refresh_display()
            except Exception:
                pass

        self.call_from_thread(update)

    def show_accessibility_task(self):
        """Show the accessibility task."""

        def update():
            try:
                if (
                    self.rich_progress is not None
                    and self._accessibility_task is not None
                ):
                    self.rich_progress.update(self._accessibility_task, visible=True)
                    self._refresh_display()
            except Exception:
                pass

        self.call_from_thread(update)

    def _refresh_display(self):
        """Refresh the Rich Progress display."""
        try:
            if hasattr(self, "progress_widget"):
                self.progress_widget.refresh_progress()
        except Exception:
            pass

    def set_complete(self, success: bool, message: str):
        """Mark as complete and dismiss after delay."""

        def update():
            try:
                if self.rich_progress is not None and self._main_task is not None:
                    self.rich_progress.update(
                        self._main_task,
                        description=message,
                        completed=True,
                    )
                    self._refresh_display()
            except Exception:
                pass

        self.call_from_thread(update)

        def delayed_dismiss():
            self.call_from_thread(lambda: self.dismiss(success))

        threading.Thread(target=delayed_dismiss, daemon=True).start()

    def action_close(self) -> None:
        """Close the dialog."""
        self.dismiss(False)
