"""Enhanced chat list panel widget with keyboard navigation and efficient updates."""

from typing import Optional, Tuple, TYPE_CHECKING
from textual.message import Message
from textual.css.query import NoMatches

from pieces.settings import Settings
from pieces._vendor.pieces_os_client.wrapper.basic_identifier.chat import BasicChat
from .base_list_panel import BaseListPanel
from .chat_item import ChatItem
from .dialogs import ConfirmDialog, EditNameDialog
from ..messages import ChatMessages
from pieces._vendor.pieces_os_client.wrapper.streamed_identifiers import (
    ConversationsSnapshot,
)

def _chat_sort_key(failures):
    """Sort key for BasicChat objects, descending by conversation.updated.value.

    Returns (rank, value) tuples — rank=1 for chats with a usable
    timestamp, rank=0 for chats whose snapshot fails to load. The rank
    pushes failures to the bottom under reverse=True while keeping the
    comparable type homogeneous, so a mixed corpus of datetime and str
    .value representations still sorts (avoids
    TypeError: '<' not supported between datetime and str). Ties within
    rank=0 preserve input order via Python's stable sort. Failure ids
    are appended to ``failures`` for one summary log line.
    """

    def _key(chat):
        try:
            value = chat.conversation.updated.value
            if value is None:
                raise ValueError("updated.value is None")
            return (1, value)
        except (AttributeError, TypeError, ValueError) as exc:
            failures.append(
                str(getattr(chat, "id", "?")) + ":" + type(exc).__name__
            )
            return (0, "")

    return _key


def _chat_sort_key_tuple(failures):
    """Same as _chat_sort_key but for (chat, title, subtitle) tuples."""
    inner = _chat_sort_key(failures)

    def _key(entry):
        return inner(entry[0])

    return _key


if TYPE_CHECKING:
    pass


class ChatListPanel(BaseListPanel):
    """Enhanced chat list panel with keyboard navigation and efficient incremental updates."""

    def __init__(self, **kwargs):
        super().__init__(panel_title="Chats", empty_message="No chats yet...", **kwargs)
        self.active_chat: Optional[BasicChat] = None

    def get_new_button_text(self) -> str:
        """Get the text for the new chat button."""
        return "➕ New Chat"

    def get_item_id(self, item: BasicChat) -> str:
        """Get a unique ID for a chat."""
        return item.id

    def create_item_widget(
        self, item: BasicChat, title: str, subtitle: str
    ) -> ChatItem:
        """Create a widget for a chat."""
        is_active = item == self.active_item
        return ChatItem(
            chat=item,
            title=title,
            summary=subtitle,  # ChatItem uses 'summary' instead of 'subtitle'
            is_active=is_active,
            is_selected=False,
        )

    def create_new_item_message(self) -> Message:
        """Create message for new chat request."""
        return ChatMessages.NewRequested()

    def extract_item_display_info(self, item: BasicChat) -> Tuple[str, str]:
        """Extract title and subtitle from a chat."""
        title = item.name or "Untitled"
        summary = item.summary or ""
        if len(summary) > 50:
            summary = summary[:47] + "..."
        return title, summary

    # Legacy compatibility methods - delegate to base implementation
    def load_chats(self, chats):
        """Load chats. Sort by updated.value desc so newest are at top.

        ``copilot_view._load_items`` calls ``copilot.chats()`` which
        returns ``BasicChat`` instances in the order PiecesOS streamed
        their identifiers — roughly chronological-ascending. Without
        sorting here the panel opens with the oldest chats at the top.
        """
        sort_failures = []
        chats = sorted(
            chats, key=_chat_sort_key(sort_failures), reverse=True
        )
        if sort_failures:
            Settings.logger.warning(
                "chats_panel.load_chats: "
                + str(len(sort_failures))
                + " chat(s) with unloadable updated.value sunk to bottom; "
                + "first few=" + str(sort_failures[:3])
            )

        # Convert chats to the format expected by base implementation
        converted_chats = []
        for chat in chats:
            title, subtitle = self.extract_item_display_info(chat)
            converted_chats.append((chat, title, subtitle))
        self.load_items(converted_chats)

    def _sort_items_by_updated(self, items, log_label: str):
        """Sort (chat, title, subtitle) tuples by conversation.updated.value desc.

        Uses ``_chat_sort_key_tuple`` so chats whose snapshot fails to
        load sink to the bottom under reverse=True instead of raising.
        ``log_label`` distinguishes warning lines per call site.
        """
        sort_failures = []
        items.sort(key=_chat_sort_key_tuple(sort_failures), reverse=True)
        if sort_failures:
            Settings.logger.warning(
                "chats_panel." + log_label + ": "
                + str(len(sort_failures))
                + " chat(s) sunk to bottom; first="
                + str(sort_failures[:1])
            )
        return items

    def _schedule_reorder(self, items_container):
        """Reorder DOM widgets to match self.items.

        During first-shot the WS streams chats in arrival order — many
        per refresh cycle — so we debounce via ``call_after_refresh`` to
        avoid O(n^2) reorder passes. Post-first-shot, WS events arrive
        sparsely, so we reorder eagerly.
        """
        if ConversationsSnapshot.first_shot:
            if not getattr(self, "_reorder_pending", False):
                self._reorder_pending = True

                def _do_reorder() -> None:
                    self._reorder_pending = False
                    try:
                        container = self.query_one("#items-container")
                    except NoMatches:
                        return
                    self._reorder_item_widgets(container)

                self.call_after_refresh(_do_reorder)
        else:
            self._reorder_item_widgets(items_container)

    def add_chat(self, chat: BasicChat, title: str, summary: str = ""):
        """Add a chat, keeping the list sorted by updated.value desc.

        Sorting on every add (rather than only during first_shot) keeps
        the panel correct even when a chat that *looks* new to the
        widget map is actually an older chat the panel hadn't seen yet.
        Without this, ``add_chat_at_top`` previously placed such chats
        at the top regardless of timestamp, leaving stale chats stuck
        at position 0.
        """
        items = list(self.items) + [(chat, title, summary)]
        items = self._sort_items_by_updated(items, "add_chat")
        self.items = items

        if chat.id not in self._item_widgets:
            try:
                items_container = self.query_one("#items-container")
                self._add_item_widget(chat, title, summary, items_container)

                empty_state = items_container.query_one("#empty-state")
                empty_state.display = False

                self._schedule_reorder(items_container)
            except NoMatches:
                pass

    def add_chat_at_top(self, chat: BasicChat, title: str, summary: str = ""):
        """Compatibility shim — delegates to add_chat.

        Earlier versions blindly prepended, but a fresh chat with the
        latest ``updated.value`` already lands at the top under the
        sorted ordering, and a chat that merely *appears* new to the
        widget map (e.g. opened from another client) should fall into
        its correct slot, not jump to the top.
        """
        self.add_chat(chat, title, summary)

    def remove_chat(self, chat_id: str):
        """Remove a chat from the UI."""
        # Remove from data - use safe filtering to avoid accessing deleted chat objects
        valid_chats = []
        for chat, title, summary in self.items:
            try:
                if chat.id != chat_id:
                    valid_chats.append((chat, title, summary))
            except (AttributeError, Exception):
                continue
        self.items = valid_chats

        # Remove widget
        if chat_id in self._item_widgets:
            widget = self._item_widgets[chat_id]
            if widget.is_mounted:
                widget.remove()
            del self._item_widgets[chat_id]
            if chat_id in self._item_order:
                self._item_order.remove(chat_id)

        # Update selection if the deleted chat was selected
        if self._selected_item_id == chat_id:
            if self._item_order:
                self._selected_item_id = self._item_order[0]
                self._update_visual_selection()
            else:
                self._selected_item_id = None

        # Show empty state if no chats left
        if not self.items:
            try:
                items_container = self.query_one("#items-container")
                empty_state = items_container.query_one("#empty-state")
                empty_state.display = True
            except NoMatches:
                # If container doesn't exist, skip showing empty state
                pass

    def update_chat(self, chat: BasicChat, title: str, summary: str = ""):
        """Update a chat and re-position it by current updated.value.

        When PiecesOS bumps ``updated.value`` (e.g. a new message lands
        on an existing chat), the chat should bubble toward the top to
        match the panel's invariant that items are sorted by
        ``updated.value`` desc. The previous version mutated only the
        title/summary in place, so the visible DOM order drifted out of
        sync with the underlying data on every chat update.
        """
        updated_chats = []
        for existing_chat, existing_title, existing_summary in self.items:
            if existing_chat == chat:
                updated_chats.append((chat, title, summary))
            else:
                updated_chats.append((existing_chat, existing_title, existing_summary))
        updated_chats = self._sort_items_by_updated(updated_chats, "update_chat")
        self.items = updated_chats

        self._update_item_widget(chat.id, chat, title, summary)

        try:
            items_container = self.query_one("#items-container")
            self._schedule_reorder(items_container)
        except NoMatches:
            pass

    def set_active_chat(self, chat: Optional[BasicChat]):
        if not chat or not chat.exists():
            return
        if self.active_chat and not self.active_chat.exists():
            self.active_chat = None

        if self.active_chat != chat:
            self.active_chat = chat
            self.set_active_item(chat)

    async def on_chat_messages_switched(self, message: ChatMessages.Switched) -> None:
        """Handle chat switch event."""
        self._selected_item_id = message.chat.id
        self._update_visual_selection()
        self.set_active_chat(message.chat)

    def action_rename_item(self):
        """Rename the selected chat."""
        if self._selected_item_id and self._selected_item_id in self._item_widgets:
            chat_widget = self._item_widgets[self._selected_item_id]
            # Type cast to ChatItem since we know it's a ChatItem
            if hasattr(chat_widget, "chat"):
                self.app.run_worker(
                    self._rename_chat_worker(chat_widget.chat, chat_widget.title)  # type: ignore
                )

    def action_delete_item(self):
        """Delete the selected chat."""
        if self._selected_item_id and self._selected_item_id in self._item_widgets:
            chat_widget = self._item_widgets[self._selected_item_id]
            # Type cast to ChatItem since we know it's a ChatItem
            if hasattr(chat_widget, "chat"):
                self.app.run_worker(
                    self._delete_chat_worker(chat_widget.chat, chat_widget.title)  # type: ignore
                )

    async def _rename_chat_worker(self, chat: BasicChat, current_title: str):
        """Worker method to handle rename chat dialog."""
        dialog = EditNameDialog(current_title)
        new_name = await self.app.push_screen_wait(dialog)

        if new_name:
            try:
                chat.name = new_name
                Settings.logger.info(f"Renamed chat to: {new_name}")
            except Exception as e:
                Settings.logger.error(f"Error renaming chat: {e}")

    async def _delete_chat_worker(self, chat: BasicChat, title: str):
        """Delete chat after user confirmation."""
        dialog = ConfirmDialog(
            title="⚠️ Delete Chat", message=f"Are you sure you want to delete '{title}'?"
        )
        confirmed = await self.app.push_screen_wait(dialog)

        if confirmed:
            try:
                chat_id = chat.id
                chat.delete()
                Settings.logger.info(
                    f"Requested deletion of chat: {title} (ID: {chat_id})"
                )
            except Exception as e:
                Settings.logger.error(f"Error deleting chat: {e}")

    # Message handlers for chat updates
    async def on_chat_messages_updated(self, message: ChatMessages.Updated) -> None:
        """Handle chat update event from backend."""
        if not message.chat:
            Settings.logger.info("Received chat update with None chat - ignoring")
            return

        try:
            # Check if chat is valid by accessing its ID
            chat_id = message.chat.id
            Settings.logger.info(f"Chat updated: {chat_id}")
        except (AttributeError, TypeError):
            # Chat is deleted or not valid - ignore the update
            Settings.logger.info("Received update for deleted/invalid chat - ignoring")
            return

        try:
            chat_exists = chat_id in self._item_widgets
            title = message.chat.name
            summary = message.chat.summary or ""

            if chat_exists:
                self.update_chat(message.chat, title, summary)
            else:
                if ConversationsSnapshot.first_shot:
                    self.add_chat(message.chat, title, summary)
                else:
                    # New chat created - add at top
                    self.add_chat_at_top(message.chat, title, summary)
        except (AttributeError, TypeError):
            # Chat properties are not accessible (deleted chat) - ignore
            Settings.logger.info("Cannot access chat properties - chat may be deleted")
            return

    async def on_chat_messages_deleted(self, message: ChatMessages.Deleted) -> None:
        """Handle chat deletion event from backend."""
        self.remove_chat(message.chat_id)
