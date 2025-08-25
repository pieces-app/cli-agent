"""Main TUI application router for Pieces CLI."""

from typing import Optional, Iterable
from enum import Enum

from textual.app import App, SystemCommand
from textual.theme import Theme

from textual.screen import Screen


from pieces.settings import Settings

from .views import WorkstreamActivityView, PiecesCopilot
from .controllers import EventHub
from .messages import ViewMessages


class ViewType(Enum):
    """Available view types in the application."""

    COPILOT = "copilot"
    WORKSTREAM = "workstream"


class PiecesTUI(App):
    """Main TUI application router that manages different views."""

    DEFAULT_CSS = """
    Screen {
        background: $background;
        color: $text;
    }
    
    /* Shared Layout Styles */
    .main-layout {
        width: 100%;
        height: 100%;
    }
    
    .main-layout-with-sidebar .content-panel {
        width: 75%;
    }
    
    .main-layout-with-sidebar .list-panel {
        width: 25%;
    }
    
    .main-layout-no-sidebar .content-panel {
        width: 100%;
    }
    
    .main-layout-no-sidebar .list-panel {
        display: none;
    }
    
    /* Shared Utility Styles */
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

    BINDINGS = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Router state
        self.current_view_type = ViewType.COPILOT
        self.event_hub: Optional[EventHub] = None

        # View instances
        self.copilot_view: Optional[PiecesCopilot] = None
        self.workstream_view: Optional[WorkstreamActivityView] = None
        self.current_view: Optional[Screen] = None

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        yield from super().get_system_commands(screen)

        # Show context-aware view switching command
        if isinstance(screen, PiecesCopilot):
            yield SystemCommand(
                "Switch to Workstream Activity",
                "Context-aware AI that helps with code, docs, and workflow tasks.",
                self.switch_to_workstream,
            )
        elif isinstance(screen, WorkstreamActivityView):
            yield SystemCommand(
                "Switch to Copilot",
                "Context-aware AI that helps with code, docs, and workflow tasks.",
                self.switch_to_copilot,
            )

    def on_mount(self) -> None:
        """Initialize the application router when mounted."""
        self.title = "Pieces CLI - TUI Mode"

        # Setup themes and event hub
        self._setup_themes()
        self.theme_changed_signal.subscribe(self, self.on_theme_change)
        self.event_hub = EventHub(self)
        self.event_hub.initialize()

        # Install screens
        self.copilot_view = PiecesCopilot(event_hub=self.event_hub)
        self.workstream_view = WorkstreamActivityView(event_hub=self.event_hub)

        self.install_screen(self.copilot_view, name="copilot")
        self.install_screen(self.workstream_view, name="workstream")

        # Start with copilot view
        self.push_screen("copilot")
        self.current_view_type = ViewType.COPILOT
        self.current_view = self.copilot_view

    def _setup_themes(self):
        """Set up application themes."""
        pieces_dark_theme = Theme(
            name="pieces-dark",
            primary="#64B5F6",  # Vibrant blue for primary actions
            secondary="#212121",  # Dark grey for secondary elements
            accent="#81C784",  # Green accent for highlights
            warning="#FFB74D",  # Orange for warnings
            error="#E57373",  # Soft red for errors
            success="#81C784",  # Green for success
            foreground="#FFFFFF",  # White text
            background="#212121",  # Dark background
            surface="#2C2C2C",  # Slightly lighter surface
            panel="#424242",  # Medium grey panels
            dark=True,
            variables={
                "border": "#64B5F6",  # Blue borders for focus
                "border-blurred": "#424242",  # Grey for unfocused
                "footer-description-foreground": "#FFFFFF",
                "footer-key-foreground": "#81C784",  # Green key bindings
                "input-selection-background": "#64B5F6 40%",
                "scrollbar": "#424242",
                "scrollbar-hover": "#64B5F6",
                "scrollbar-active": "#81C784",
                "scrollbar-background": "#1a1a1a",
                "block-cursor-background": "#64B5F6",
                "block-cursor-foreground": "#212121",
            },
        )

        pieces_light_theme = Theme(
            name="pieces-light",
            primary="#1976D2",  # Strong blue for primary actions
            secondary="#FFFFFF",  # White for secondary elements
            accent="#388E3C",  # Green accent for highlights
            warning="#F57C00",  # Orange for warnings
            error="#D32F2F",  # Red for errors
            success="#388E3C",  # Green for success
            foreground="#212121",  # Dark text
            background="#FAFAFA",  # Very light grey background
            surface="#FFFFFF",  # White surface
            panel="#F5F5F5",  # Light grey panels
            dark=False,
            variables={
                "border": "#1976D2",  # Blue borders for focus
                "border-blurred": "#E0E0E0",  # Light grey for unfocused
                "footer-description-foreground": "#212121",
                "footer-key-foreground": "#388E3C",  # Green key bindings
                "input-selection-background": "#1976D2 30%",
                "scrollbar": "#E0E0E0",
                "scrollbar-hover": "#1976D2",
                "scrollbar-active": "#388E3C",
                "scrollbar-background": "#F5F5F5",
                "block-cursor-background": "#1976D2",
                "block-cursor-foreground": "#FFFFFF",
            },
        )

        self.register_theme(pieces_dark_theme)
        self.register_theme(pieces_light_theme)

        # Load theme from configuration
        try:
            self.theme = Settings.cli_config.theme
        except Exception as e:
            Settings.logger.error(f"Failed to load saved theme: {e}")
            self.theme = "pieces-dark"

    def _switch_to_view(self, view_type: ViewType):
        """Switch to a specific view type."""
        if view_type == self.current_view_type:
            return

        Settings.logger.info(f"Switching to {view_type.value} view")

        # Switch to the appropriate screen
        if view_type == ViewType.COPILOT:
            self.switch_screen("copilot")
            self.current_view = self.copilot_view
        elif view_type == ViewType.WORKSTREAM:
            self.switch_screen("workstream")
            self.current_view = self.workstream_view
        else:
            Settings.logger.error(f"Unknown view type: {view_type}")
            return

        self.current_view_type = view_type

    def switch_to_copilot(self):
        """Switch to copilot view."""
        self._switch_to_view(ViewType.COPILOT)

    def switch_to_workstream(self):
        """Switch to workstream view."""
        self._switch_to_view(ViewType.WORKSTREAM)

    # View switching message handlers
    async def on_view_messages_switch_to_chat(
        self, _: ViewMessages.SwitchToChat
    ) -> None:
        """Handle switch to copilot view message."""
        self._switch_to_view(ViewType.COPILOT)

    async def on_view_messages_switch_to_workstream(
        self, _: ViewMessages.SwitchToWorkstream
    ) -> None:
        """Handle switch to workstream view message."""
        self._switch_to_view(ViewType.WORKSTREAM)

    def on_theme_change(self, new_theme):
        try:
            Settings.cli_config.theme = new_theme.name
            Settings.logger.info(
                f"Theme changed to {new_theme} and saved to configuration"
            )
        except Exception as e:
            Settings.logger.error(f"Failed to save theme preference: {e}")

    def on_unmount(self):
        """Clean up when app is unmounted."""
        try:
            # Clean up event hub and controllers
            if self.event_hub:
                self.event_hub.cleanup()
                self.event_hub = None

            # Clean up views
            if self.copilot_view:
                self.copilot_view.cleanup()

            if self.workstream_view:
                self.workstream_view.cleanup()

            # Clear references
            self.copilot_view = None
            self.workstream_view = None
            self.current_view = None

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
