"""Enhanced chat message widget with metadata display and markdown support for the TUI."""

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from textual.app import ComposeResult
from textual.widgets import Static, Markdown
from textual.containers import Container, Horizontal, Vertical

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.models.grouped_timestamp import (
        GroupedTimestamp,
    )
    from pieces._vendor.pieces_os_client.wrapper.basic_identifier.message import (
        BasicMessage,
    )


class ChatMessage(Container):
    """An enhanced chat message widget with role-based styling, metadata, and markdown support.

    Attributes:
        role: The role of the message sender (e.g., 'user', 'assistant', 'system')
        content: The text content of the message
        timestamp: Optional timestamp when the message was created
        message_id: Optional unique identifier for the message
    """

    DEFAULT_CSS = """
    ChatMessage {
        margin: 1;
        padding: 0;
        width: 100%;
        height: auto;
        
        &:hover {
            background: $surface-darken-1;
        }
    }
    
    ChatMessage .message-wrapper {
        padding: 0 1;
        width: 100%;
        height: auto;
    }
    
    ChatMessage .message-header {
        height: auto;
        margin: 0 0 0 0;
        width: 100%;
    }
    
    ChatMessage .message-role {
        text-style: bold;
        margin: 0 1 0 0;
        width: auto;
        
        &.message-role-user { color: $primary; }
        &.message-role-assistant { color: $success; }
        &.message-role-system { color: $warning; }
    }
    
    ChatMessage .message-timestamp {
        color: $text-muted;
        text-style: italic;
        margin: 0;
        width: auto;
    }
    
    ChatMessage .message-content {
        margin: 0;
        padding: 1;
        width: 100%;
        height: auto;
        border-left: thick $accent;
        
        &.message-content-user {
            border-left: thick $primary;
            background: $primary 20%;
        }
        
        &.message-content-assistant {
            border-left: thick $success;
            background: $success 20%;
        }
        
        &.message-content-system {
            border-left: thick $warning;
            background: $warning 20%;
            text-style: italic;
        }
    }
    
    ChatMessage Markdown {
        background: transparent;
        padding: 0;
        width: 100%;
        height: auto;
    }
    """

    def __init__(
        self,
        role: str,
        content: str,
        timestamp: Optional[str] = None,
        message_id: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.role = role
        self.content = content
        self.timestamp = timestamp
        self.message_id = message_id
        self.add_class(f"message-{role.lower()}")

    def compose(self) -> ComposeResult:
        """Compose the chat message with enhanced layout and markdown support."""
        with Vertical(classes="message-wrapper"):
            # Header with role and metadata
            with Horizontal(classes="message-header"):
                # Role indicator
                role_display = self._get_role_display()
                yield Static(
                    role_display,
                    classes=f"message-role message-role-{self.role.lower()}",
                )

                # Timestamp
                if self.timestamp:
                    yield Static(self.timestamp, classes="message-timestamp")

            yield Markdown(
                self.content,
                classes=f"message-content message-content-{self.role.lower()}",
            )

    def _get_role_display(self) -> str:
        """Get the display string for the role."""
        role_icons = {
            "user": "👤 You",
            "assistant": "🤖 Assistant",
            "system": "⚙️ System",
        }
        return role_icons.get(self.role.lower(), f"{self.role.capitalize()}:")

    @classmethod
    def from_basic_message(cls, basic_message: "BasicMessage") -> "ChatMessage":
        """Create a ChatMessage from a BasicMessage object."""
        # Get timestamp
        timestamp = None
        if hasattr(basic_message.message, "created") and basic_message.message.created:
            timestamp = cls._format_timestamp(basic_message.message.created)

        return cls(
            role=basic_message.role,
            content=basic_message.raw_content or "",
            timestamp=timestamp,
            message_id=basic_message.id,
        )

    @staticmethod
    def _format_timestamp(grouped_timestamp: "GroupedTimestamp") -> str:
        """Format a GroupedTimestamp into a readable string."""
        if hasattr(grouped_timestamp, "readable") and grouped_timestamp.readable:
            return grouped_timestamp.readable

        # Fallback to parsing if readable is not available
        try:
            if hasattr(grouped_timestamp, "value") and grouped_timestamp.value:
                # Assuming value is milliseconds since epoch
                timestamp_value = grouped_timestamp.value
                if isinstance(timestamp_value, (int, float)):
                    dt = datetime.fromtimestamp(timestamp_value / 1000)
                    now = datetime.now()

                    # Format based on how recent
                    if dt.date() == now.date():
                        return dt.strftime("Today %I:%M %p")
                    elif (now - dt).days == 1:
                        return dt.strftime("Yesterday %I:%M %p")
                    elif (now - dt).days < 7:
                        return dt.strftime("%A %I:%M %p")
                    else:
                        return dt.strftime("%b %d, %Y %I:%M %p")
        except (OSError, OverflowError, ValueError):
            pass

        return ""
