"""TUI widgets for the Pieces CLI."""

from .chat_panel import ChatViewPanel
from .chats_panel import ChatListPanel
from .chat_input import ChatInput
from .chat_message import ChatMessage
from .chat_item import ChatItem
from .status_bar import StatusBar
from .dialogs import ConfirmDeleteDialog, EditNameDialog

__all__ = [
    "ChatViewPanel",
    "ChatListPanel", 
    "ChatInput",
    "ChatMessage",
    "ChatItem",
    "StatusBar",
    "ConfirmDeleteDialog",
    "EditNameDialog",
]

