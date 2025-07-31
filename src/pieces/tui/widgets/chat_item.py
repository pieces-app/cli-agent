"""Chat item widget for displaying chat details in the chat list."""

from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Container

from pieces._vendor.pieces_os_client.wrapper.basic_identifier.chat import BasicChat
from ..messages import ChatMessages


class ChatItem(Container):
    """A single chat item in the list showing chat details."""

    DEFAULT_CSS = """
    ChatItem {
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
        
        &.chat-active {
            border-left: thick $primary;
            background: $primary 10%;
            
            &:hover {
                background: $primary 20%;
            }
        }
        
        &.chat-selected {
            background: $accent !important;
            color: $text !important;
        }
    }
    
    ChatItem .chat-content {
        padding: 1;
        width: 100%;
        height: auto;
    }
    
    ChatItem .chat-title {
        text-style: bold;
        color: $text;
        height: 1;
        width: 100%;
    }
    
    ChatItem.chat-active .chat-title {
        color: $primary;
    }
    
    ChatItem.chat-selected .chat-title {
        color: $text !important;
    }
    
    ChatItem .chat-summary {
        color: $text-muted;
        text-style: italic;
        margin: 1 0 0 0;
        height: auto;
        width: 100%;
    }
    
    ChatItem.chat-active .chat-summary {
        color: $primary 80%;
    }
    
    ChatItem.chat-selected .chat-summary {
        color: $text-muted !important;
    }
    """

    def __init__(
        self,
        chat: BasicChat,
        title: str,
        summary: str = "",
        is_active: bool = False,
        is_selected: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.chat = chat
        self.title = title
        self.summary = summary
        self.is_active = is_active
        self.is_selected = is_selected

        if is_active:
            self.add_class("chat-active")
        if is_selected:
            self.add_class("chat-selected")

    def compose(self) -> ComposeResult:
        """Compose the chat item."""
        with Container(classes="chat-content"):
            # Always show title
            title_widget = Static(self.title, classes="chat-title")
            yield title_widget

            # Show summary if it exists
            if self.summary:
                summary_widget = Static(self.summary, classes="chat-summary")
                yield summary_widget

    def on_mount(self):
        """Called when the widget is mounted."""
        # Ensure proper styling is applied
        if self.is_active:
            self.add_class("chat-active")
        if self.is_selected:
            self.add_class("chat-selected")

    def on_click(self) -> None:
        """Handle chat item click."""
        # Post Textual message that will bubble up to parent handlers
        if not self.chat:
            return
        self.post_message(ChatMessages.Switched(self.chat))

    def select(self):
        """Select this chat item."""
        self.is_selected = True
        self.add_class("chat-selected")

    def deselect(self):
        """Deselect this chat item."""
        self.is_selected = False
        self.remove_class("chat-selected")

    def cleanup(self):
        """Clean up widget resources to prevent memory leaks."""
        try:
            # Clear chat reference
            self.chat = None

            # Clear state
            self.is_active = False
            self.is_selected = False
            self.title = ""
            self.summary = ""

        except Exception:
            # Ignore errors during cleanup
            pass

    def __del__(self):
        """Ensure cleanup is called when widget is destroyed."""
        try:
            self.cleanup()
        except Exception:
            # Ignore errors during cleanup in destructor
            pass
