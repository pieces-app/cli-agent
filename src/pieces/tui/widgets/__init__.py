"""TUI widgets for the Pieces CLI."""

# Base abstractions
from .base_item import BaseItem
from .base_list_panel import BaseListPanel
from .base_content_panel import BaseContentPanel

# Chat widgets
from .chat_panel import ChatViewPanel
from .chats_panel import ChatListPanel
from .chat_input import ChatInput
from .chat_message import ChatMessage
from .chat_item import ChatItem

# Workstream widgets
from .workstream_item import WorkstreamItem
from .workstream_activities_panel import WorkstreamActivitiesPanel
from .workstream_content_panel import WorkstreamContentPanel

# Shared widgets
from .status_bar import StatusBar

# Dialogs
from .dialogs import ConfirmDialog, EditNameDialog
from .ltm_progress_dialog import LTMProgressDialog

__all__ = [
    # Base abstractions
    "BaseItem",
    "BaseListPanel",
    "BaseContentPanel",
    # Chat widgets
    "ChatViewPanel",
    "ChatListPanel",
    "ChatInput",
    "ChatMessage",
    "ChatItem",
    # Workstream widgets
    "WorkstreamItem",
    "WorkstreamActivitiesPanel",
    "WorkstreamContentPanel",
    # Shared widgets
    "StatusBar",
    # Dialogs
    "ConfirmDialog",
    "EditNameDialog",
    "LTMProgressDialog",
]
