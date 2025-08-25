"""Base item widget for displaying items in lists with common functionality."""

from abc import abstractmethod
from typing import Any
from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Container
from textual.message import Message


class BaseItem(Container):
    """Base class for list items with common functionality and styling."""

    DEFAULT_CSS = """
    BaseItem {
        width: 100%;
        height: auto;
        min-height: 3;
        margin: 0 0 1 0;
        padding: 0;
        border: none;
        background: $surface;
        
        &:hover {
            background: $surface-lighten-1;
        }
        
        &.item-active {
            border-left: thick $primary;
            background: $primary 10%;
            
            &:hover {
                background: $primary 20%;
            }
        }
        
        &.item-selected {
            background: $accent !important;
            color: $text !important;
        }
    }
    
    BaseItem .item-content {
        padding: 1;
        width: 100%;
        height: auto;
    }
    
    BaseItem .item-title {
        text-style: bold;
        color: $text;
        height: 1;
        width: 100%;
    }
    
    BaseItem.item-active .item-title {
        color: $primary;
    }
    
    BaseItem.item-selected .item-title {
        color: $text !important;
    }
    
    BaseItem .item-subtitle {
        color: $text-muted;
        text-style: italic;
        margin: 1 0 0 0;
        height: auto;
        width: 100%;
    }
    
    BaseItem.item-active .item-subtitle {
        color: $primary 80%;
    }
    
    BaseItem.item-selected .item-subtitle {
        color: $text-muted !important;
    }
    """

    def __init__(
        self,
        item: Any,
        title: str,
        subtitle: str = "",
        is_active: bool = False,
        is_selected: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.item = item
        self.title = title
        self.subtitle = subtitle
        self.is_active = is_active
        self.is_selected = is_selected

        if is_active:
            self.add_class("item-active")
        if is_selected:
            self.add_class("item-selected")

    def compose(self) -> ComposeResult:
        """Compose the item with title and optional subtitle."""
        with Container(classes="item-content"):
            # Always show title
            title_widget = Static(self.title, classes="item-title")
            yield title_widget

            # Show subtitle if it exists
            if self.subtitle:
                subtitle_widget = Static(self.subtitle, classes="item-subtitle")
                yield subtitle_widget

    def on_mount(self):
        """Called when the widget is mounted."""
        # Ensure proper styling is applied
        if self.is_active:
            self.add_class("item-active")
        if self.is_selected:
            self.add_class("item-selected")

    def on_click(self) -> None:
        """Handle item click."""
        if not self.item:
            return
        self.post_message(self.create_selected_message(self.item))

    @abstractmethod
    def create_selected_message(self, item: Any) -> Message:
        """Create the appropriate message for when this item is selected."""
        pass

    def select(self):
        """Select this item."""
        self.is_selected = True
        self.add_class("item-selected")

    def deselect(self):
        """Deselect this item."""
        self.is_selected = False
        self.remove_class("item-selected")

    def set_active(self, active: bool):
        """Set the active state of this item."""
        self.is_active = active
        if active:
            self.add_class("item-active")
        else:
            self.remove_class("item-active")

    def cleanup(self):
        """Clean up widget resources to prevent memory leaks."""
        try:
            # Clear item reference
            self.item = None

            # Clear state
            self.is_active = False
            self.is_selected = False
            self.title = ""
            self.subtitle = ""

        except (RuntimeError, ValueError, AttributeError):
            pass

    def __del__(self):
        """Ensure cleanup is called when widget is destroyed."""
        try:
            self.cleanup()
        except (RuntimeError, ValueError, AttributeError):
            pass
