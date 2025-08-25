"""Base dual-pane view with clean, minimal abstraction."""

from abc import abstractmethod
from typing import Optional, TYPE_CHECKING, Iterator
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Header
from textual.widget import Widget
from textual.screen import Screen
from textual.binding import Binding

from pieces.settings import Settings
from ..controllers import EventHub

if TYPE_CHECKING:
    from ..widgets.base_list_panel import BaseListPanel


class BaseDualPaneView(Screen):
    """Base view with consistent left-list, right-content layout."""

    DEFAULT_CSS = """
    BaseDualPaneView {
        background: $background;
        color: $text;
    }
    
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
    """

    BINDINGS = [
        Binding("ctrl+s", "toggle_sidebar", "Toggle Sidebar"),
        Binding("ctrl+r", "refresh", "Refresh", show=False),
    ]

    def __init__(self, event_hub: EventHub, view_name: str, **kwargs):
        super().__init__(**kwargs)
        self.event_hub = event_hub
        self.view_name = view_name
        self.sidebar_visible = True
        self.main_layout: Optional[Horizontal] = None
        self.list_panel: Optional["BaseListPanel"] = None
        self.content_panel: Optional[Widget] = None

    def compose(self) -> ComposeResult:
        """Compose the dual-pane layout."""
        yield Header(name=f"Pieces {self.view_name}")

        # Main layout: list panel on LEFT, content panel on RIGHT
        self.main_layout = Horizontal(classes="main-layout main-layout-with-sidebar")
        with self.main_layout:
            # List panel (25% width) - LEFT SIDE
            self.list_panel = self.create_list_panel()
            self.list_panel.add_class("list-panel")
            yield self.list_panel

            # Content panel (75% width) - RIGHT SIDE
            self.content_panel = self.create_content_panel()
            self.content_panel.add_class("content-panel")
            yield self.content_panel

        yield self.main_layout

        # Additional components (input, status bar, etc.)
        yield from self.create_additional_components()

    @abstractmethod
    def create_list_panel(self) -> "BaseListPanel":
        """Create the left-side list panel."""
        pass

    @abstractmethod
    def create_content_panel(self) -> Widget:
        """Create the right-side content panel."""
        pass

    def create_additional_components(self) -> Iterator[Widget]:
        """Create additional components (input, status bar, etc.)."""
        # Override in subclasses if needed - this is an empty generator by default
        return iter(())

    def on_mount(self) -> None:
        """Initialize the view when mounted."""
        Settings.logger.info(f"{self.view_name} view mounted")
        self._initialize_view()

    @abstractmethod
    def _initialize_view(self):
        """Initialize view-specific components."""
        pass

    @abstractmethod
    def _load_items(self):
        """Load items into the list panel."""
        pass

    def action_toggle_sidebar(self):
        """Toggle the sidebar visibility and adjust layout accordingly."""
        if self.list_panel and self.main_layout:
            self.sidebar_visible = not self.sidebar_visible

            if self.sidebar_visible:
                # Show sidebar and adjust layout
                self.main_layout.remove_class("main-layout-no-sidebar")
                self.main_layout.add_class("main-layout-with-sidebar")
                status = "visible"
            else:
                # Hide sidebar and expand content view
                self.main_layout.remove_class("main-layout-with-sidebar")
                self.main_layout.add_class("main-layout-no-sidebar")
                status = "hidden"

            self._show_status_message(f"📁 Sidebar {status}")

    def action_refresh(self):
        """Refresh the current view."""
        self._load_items()

        # Trigger connection check through EventHub
        if self.event_hub:
            self.event_hub.connection.reconnect()

        self._show_status_message("✅ Refreshed")

    @abstractmethod
    def _show_status_message(self, message: str, duration: int = 3):
        """Show temporary status message."""
        pass

    # Common connection handlers
    async def on_connection_messages_established(self, _) -> None:
        """Handle connection established."""
        self._show_status_message("✅ Connected")

    async def on_connection_messages_lost(self, _) -> None:
        """Handle connection lost."""
        self._show_status_message("❌ Connection lost", 5)

    def cleanup(self):
        """Clean up view resources."""
        try:
            # Clean up panels
            if self.content_panel and hasattr(self.content_panel, "cleanup"):
                self.content_panel.cleanup()  # type: ignore

            if self.list_panel and hasattr(self.list_panel, "clear_items"):
                self.list_panel.clear_items()

            # Clear references
            self.list_panel = None
            self.content_panel = None
            self.main_layout = None

        except Exception as e:
            Settings.logger.error(f"Error during {self.view_name} view cleanup: {e}")

    def __del__(self):
        """Ensure cleanup is called when view is destroyed."""
        try:
            self.cleanup()
        except (RuntimeError, ValueError, AttributeError):
            pass
