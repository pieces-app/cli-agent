"""Chat item widget for displaying chat details in the chat list."""

from typing import TYPE_CHECKING
from textual.message import Message
from .base_item import BaseItem
from ..messages import ChatMessages

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.wrapper.basic_identifier.chat import BasicChat


class ChatItem(BaseItem):
    """A single chat item in the list showing chat details."""

    def __init__(
        self,
        chat: "BasicChat",
        title: str,
        summary: str = "",
        is_active: bool = False,
        is_selected: bool = False,
        **kwargs,
    ):
        # Store the chat for easy access
        self.chat = chat
        super().__init__(
            item=chat,
            title=title,
            subtitle=summary,  # Use subtitle instead of summary for consistency
            is_active=is_active,
            is_selected=is_selected,
            **kwargs,
        )

    def create_selected_message(self, item) -> Message:
        """Create the appropriate message for when this chat item is selected."""
        return ChatMessages.Switched(item)

    @property
    def summary(self) -> str:
        """Backward compatibility property for summary."""
        return self.subtitle

    @summary.setter
    def summary(self, value: str):
        """Backward compatibility property for summary."""
        self.subtitle = value

    def cleanup(self):
        """Clean up chat-specific resources."""
        try:
            self.chat = None
        except (RuntimeError, ValueError, AttributeError):
            pass
        super().cleanup()
