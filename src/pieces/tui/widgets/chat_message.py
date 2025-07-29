"""Enhanced chat message widget with metadata display and markdown support for the TUI."""

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from textual.app import ComposeResult
from textual.widgets import Static, Markdown
from textual.containers import Container, Horizontal, Vertical

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.models.conversation_message import (
        ConversationMessage,
    )
    from pieces._vendor.pieces_os_client.models.grouped_timestamp import (
        GroupedTimestamp,
    )
    from pieces._vendor.pieces_os_client.wrapper.basic_identifier.message import (
        BasicMessage,
    )


class ChatMessage(Container):
    """An enhanced chat message widget with role-based styling, metadata, and markdown support."""

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
        self.add_class("message-container")
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
                dt = datetime.fromtimestamp(grouped_timestamp.value / 1000)
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
        except:
            pass

        return ""

    def highlight(self):
        """Highlight this message."""
        self.add_class("message-highlighted")

    def unhighlight(self):
        """Remove highlight from this message."""
        self.remove_class("message-highlighted")