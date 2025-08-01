"""Enhanced chat list panel widget with keyboard navigation and efficient updates."""

from typing import List, Optional, Dict
from textual.app import ComposeResult
from textual.widgets import Static, Button
from textual.containers import ScrollableContainer, Container
from textual.reactive import reactive
from textual.widget import Widget
from textual.binding import Binding

from pieces.settings import Settings
from pieces._vendor.pieces_os_client.wrapper.basic_identifier.chat import BasicChat
from .chat_item import ChatItem
from .dialogs import ConfirmDeleteDialog, EditNameDialog
from ..messages import ChatMessages


class ChatListPanel(ScrollableContainer):
    """Enhanced chat list panel with keyboard navigation and efficient incremental updates."""

    DEFAULT_CSS = """
    ChatListPanel {
        border: solid $secondary;
        border-title-color: $secondary;
        border-title-style: bold;
        scrollbar-background: $surface;
        scrollbar-color: $secondary;
        scrollbar-color-hover: $accent;
        
        &:focus {
            border: solid $accent;
            border-title-color: $accent;
            border-title-style: bold;
        }
    }
    
    ChatListPanel .new-chat-button {
        width: 100%;
        height: 3;
        margin: 0 0 1 0;
        background: $primary;
        color: $text;
        border: none;
        text-style: bold;
        
        &:hover {
            background: $primary-lighten-1;
        }
        
        &:focus {
            background: $primary-lighten-2;
        }
    }
    
    ChatListPanel .chats-list {
        width: 100%;
        height: 1fr;
        overflow-y: auto;
    }
    
    ChatListPanel .empty-chats {
        width: 100%;
        text-align: center;
        padding: 2;
        color: $text-muted;
        text-style: italic;
        height: auto;
    }
    """

    chats: reactive[List[tuple]] = reactive([])  # (chat, title, summary)
    active_chat: reactive[Optional[BasicChat]] = reactive(None)

    BINDINGS = [
        Binding("j", "select_next", "Next chat", show=False),
        Binding("k", "select_previous", "Previous chat", show=False),
        Binding("enter", "open_selected", "Open chat", show=False),
        Binding("n", "new_chat", "New chat", show=False),
        Binding("r", "rename_chat", "Rename chat", show=False),
        Binding("d", "delete_chat", "Delete chat", show=False),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.border_title = "Chats"

        # Efficient tracking: chat_id -> ChatItem widget
        self._chat_widgets: Dict[str, ChatItem] = {}
        # Track current chat order for positioning
        self._chat_order: List[str] = []
        self._selected_chat_id: Optional[str] = None

    def compose(self) -> ComposeResult:
        """Compose the chats panel."""
        # New Chat button at the top
        new_chat_btn = Button(
            "➕ New Chat", classes="new-chat-button", id="new-chat-btn"
        )
        new_chat_btn.can_focus = False
        yield new_chat_btn

        # Chats list container (use regular Container since parent is already ScrollableContainer)
        with Container(classes="chats-list", id="chats-container"):
            yield Static("No chats yet...", classes="empty-chats", id="empty-state")

    def load_chats(self, chats):
        """Load chats with efficient incremental updates."""
        if chats and not isinstance(chats[0], tuple):
            converted_chats = []
            for chat in chats:
                title = chat.name or "Untitled"
                summary = chat.summary or ""
                if len(summary) > 50:
                    summary = summary[:47] + "..."
                converted_chats.append((chat, title, summary))
            self.chats = converted_chats
        else:
            # Already in tuple format
            self.chats = chats

        self._update_chats_incrementally()

        # Select first chat if available and none selected
        if self.chats and self._selected_chat_id is None and self._chat_order:
            self._selected_chat_id = self._chat_order[0]
            self._update_visual_selection()

    def _update_chats_incrementally(self):
        """Efficiently update chats - only add/remove/update what changed."""
        chats_container = self.query_one("#chats-container")

        # Get current chat IDs from the new data
        new_chat_ids = {chat.id for chat, _, _ in self.chats}
        current_chat_ids = set(self._chat_widgets.keys())

        # Calculate what changed
        chats_to_add = new_chat_ids - current_chat_ids
        chats_to_remove = current_chat_ids - new_chat_ids
        chats_to_update = new_chat_ids & current_chat_ids

        # Remove deleted chats
        for chat_id in chats_to_remove:
            if chat_id in self._chat_widgets:
                widget = self._chat_widgets[chat_id]
                if widget.is_mounted:
                    widget.remove()
                del self._chat_widgets[chat_id]
                if chat_id in self._chat_order:
                    self._chat_order.remove(chat_id)

        # Hide/show empty state based on whether we have chats
        empty_state = chats_container.query_one("#empty-state")
        if self.chats:
            empty_state.display = False
        else:
            empty_state.display = True
            # Clear everything when no chats
            self._chat_widgets.clear()
            self._chat_order.clear()
            return

        # Create mapping for efficient lookup
        chat_data_by_id = {
            chat.id: (chat, title, summary) for chat, title, summary in self.chats
        }

        # Add new chats
        for chat_id in chats_to_add:
            if chat_id in chat_data_by_id:
                chat, title, summary = chat_data_by_id[chat_id]
                self._add_chat_widget(chat, title, summary, chats_container)

        # Update existing chats (title, summary, active state)
        for chat_id in chats_to_update:
            if chat_id in chat_data_by_id and chat_id in self._chat_widgets:
                chat, title, summary = chat_data_by_id[chat_id]
                self._update_chat_widget(chat_id, chat, title, summary)

        # Reorder widgets to match the new chat order
        self._reorder_chat_widgets(chats_container)

    def _add_chat_widget(
        self, chat: BasicChat, title: str, summary: str, container: Widget
    ):
        """Add a new chat widget efficiently."""
        is_active = chat == self.active_chat

        chat_item = ChatItem(
            chat=chat,
            title=title,
            summary=summary,
            is_active=is_active,
            is_selected=False,
        )

        # Use chat ID for unique identification
        chat_item.id = f"chat-item-{chat.id}"
        self._chat_widgets[chat.id] = chat_item
        self._chat_order.append(chat.id)

        container.mount(chat_item)

    def _update_chat_widget(
        self, chat_id: str, chat: BasicChat, title: str, summary: str
    ):
        """Update an existing chat widget efficiently."""
        if chat_id not in self._chat_widgets:
            return

        widget = self._chat_widgets[chat_id]

        # Update widget data if changed
        if widget.title != title:
            widget.title = title
            # Update the title widget in the UI
            title_widget = widget.query_one(".chat-title", Static)
            title_widget.update(title)

        if widget.summary != summary:
            widget.summary = summary
            # Update summary widget if it exists
            summary_widgets = widget.query(".chat-summary")
            if summary_widgets and summary:
                # Cast to Static to satisfy type checker
                summary_widget = summary_widgets[0]
                if hasattr(summary_widget, "update"):
                    summary_widget.update(  # pyright: ignore[reportAttributeAccessIssue]
                        summary
                    )

        # Update active state
        is_active = chat == self.active_chat
        if widget.is_active != is_active:
            widget.is_active = is_active
            if is_active:
                widget.add_class("chat-active")
            else:
                widget.remove_class("chat-active")

    def _reorder_chat_widgets(self, container: Widget):
        """Reorder widgets to match the new chat order efficiently."""
        # Build new order based on current chats list
        new_order = []
        for chat, _, _ in self.chats:
            if chat.id in self._chat_widgets:
                new_order.append(chat.id)

        # Only reorder if the order actually changed
        if new_order != self._chat_order:
            self._chat_order = new_order

            # Move widgets to correct positions
            # Textual doesn't have an easy reorder, so we'll use the move_child method
            for i, chat_id in enumerate(self._chat_order):
                if chat_id in self._chat_widgets:
                    widget = self._chat_widgets[chat_id]
                    try:
                        # Move widget to the correct position
                        if i == 0:
                            # Move to beginning - use before the first child
                            children = list(container.children)
                            if children:
                                container.move_child(widget, before=children[0])
                        else:
                            # Move after the previous widget
                            prev_chat_id = self._chat_order[i - 1]
                            if prev_chat_id in self._chat_widgets:
                                prev_widget = self._chat_widgets[prev_chat_id]
                                container.move_child(widget, after=prev_widget)
                    except (ValueError, RuntimeError):
                        pass

    def add_chat(self, chat: BasicChat, title: str, summary: str = ""):
        """Add a single new chat efficiently."""
        # Add to data
        self.chats = list(self.chats) + [(chat, title, summary)]

        # Add widget incrementally
        if chat.id not in self._chat_widgets:
            chats_container = self.query_one("#chats-container")
            self._add_chat_widget(chat, title, summary, chats_container)

            # Hide empty state
            empty_state = chats_container.query_one("#empty-state")
            empty_state.display = False

    def add_chat_at_top(self, chat: BasicChat, title: str, summary: str = ""):
        """Add a chat at the top of the list."""
        # Add to data at the beginning
        self.chats = [(chat, title, summary)] + list(self.chats)

        # Add widget
        if chat.id not in self._chat_widgets:
            chats_container = self.query_one("#chats-container")
            self._add_chat_widget(chat, title, summary, chats_container)

            # Hide empty state
            empty_state = chats_container.query_one("#empty-state")
            empty_state.display = False

            # Move the new chat widget to the top
            self._reorder_chat_widgets(chats_container)

    def remove_chat(self, chat_id: str):
        """Remove a chat from the UI."""
        # Remove from data - use safe filtering to avoid accessing deleted chat objects
        valid_chats = []
        for chat, title, summary in self.chats:
            try:
                # Try to access chat.id to check if chat is still valid
                if chat.id != chat_id:
                    valid_chats.append((chat, title, summary))
            except (AttributeError, Exception):
                # Chat object is invalid/deleted, skip it
                continue
        self.chats = valid_chats

        # Remove widget
        if chat_id in self._chat_widgets:
            widget = self._chat_widgets[chat_id]
            if widget.is_mounted:
                widget.remove()
            del self._chat_widgets[chat_id]
            if chat_id in self._chat_order:
                self._chat_order.remove(chat_id)
                
        # Update selection if the deleted chat was selected
        if self._selected_chat_id == chat_id:
            if self._chat_order:
                # Select the first available chat
                self._selected_chat_id = self._chat_order[0]
                self._update_visual_selection()
            else:
                self._selected_chat_id = None

        # Show empty state if no chats left
        if not self.chats:
            chats_container = self.query_one("#chats-container")
            empty_state = chats_container.query_one("#empty-state")
            empty_state.display = True

    def update_chat(self, chat: BasicChat, title: str, summary: str = ""):
        """Update a single chat efficiently."""

        # Update data
        updated_chats = []
        for existing_chat, existing_title, existing_summary in self.chats:
            if existing_chat == chat:
                updated_chats.append((chat, title, summary))
            else:
                updated_chats.append((existing_chat, existing_title, existing_summary))
        self.chats = updated_chats

        # Update widget incrementally
        self._update_chat_widget(chat.id, chat, title, summary)

    def set_active_chat(self, chat: Optional[BasicChat]):
        """Set the active chat efficiently - only update affected widgets."""
        if self.active_chat != chat:  # Only update if actually changing
            old_active_id = self.active_chat.id if self.active_chat else None
            new_active_id = chat.id if chat else None

            self.active_chat = chat

            # Update only the affected widgets
            if old_active_id and old_active_id in self._chat_widgets:
                old_widget = self._chat_widgets[old_active_id]
                old_widget.is_active = False
                old_widget.remove_class("chat-active")

            if new_active_id and new_active_id in self._chat_widgets:
                new_widget = self._chat_widgets[new_active_id]
                new_widget.is_active = True
                new_widget.add_class("chat-active")

    def refresh_chats(self):
        self._update_chats_incrementally()

    def clear_chats(self):
        """Clear all chats efficiently."""
        # Remove all widgets
        for widget in self._chat_widgets.values():
            if widget.is_mounted:
                widget.remove()

        # Clear tracking
        self._chat_widgets.clear()
        self._chat_order.clear()

        # Clear data
        self.chats.clear()
        self.active_chat = None
        self._selected_chat_id = None

        # Show empty state
        chats_container = self.query_one("#chats-container")
        empty_state = chats_container.query_one("#empty-state")
        empty_state.display = True

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "new-chat-btn":
            # Post Textual message that will bubble up to parent handlers
            self.post_message(ChatMessages.NewRequested())
            event.stop()  # Prevent further propagation

    async def on_chat_messages_switched(self, message: ChatMessages.Switched) -> None:
        """Handle chat selection with O(1) widget-based approach."""
        self._selected_chat_id = message.chat.id
        self._update_visual_selection()

        # Set active chat for backend sync
        self.set_active_chat(message.chat)

    def _update_visual_selection(self):
        """Update visual selection efficiently using widget dictionary."""
        # Clear all selections first (efficient iteration over widgets)
        for widget in self._chat_widgets.values():
            widget.is_selected = False
            widget.remove_class("chat-selected")

        if self._selected_chat_id and self._selected_chat_id in self._chat_widgets:
            selected_widget = self._chat_widgets[self._selected_chat_id]
            selected_widget.is_selected = True
            selected_widget.add_class("chat-selected")

            # Scroll to selected widget
            try:
                self.scroll_to_widget(selected_widget, animate=True)
            except (ValueError, RuntimeError):
                # Widget may not be scrollable or visible
                pass

    # Keyboard navigation
    def action_select_next(self):
        """Select the next chat using efficient chat order navigation."""
        if not self._chat_order:
            return

        if self._selected_chat_id is None:
            # No selection, select first chat
            self._selected_chat_id = self._chat_order[0]
        else:
            # Find current position and move to next
            try:
                current_index = self._chat_order.index(self._selected_chat_id)
                next_index = min(current_index + 1, len(self._chat_order) - 1)
                self._selected_chat_id = self._chat_order[next_index]
            except ValueError:
                # Current selection not in order, select first
                self._selected_chat_id = self._chat_order[0]

        self._update_visual_selection()

    def action_select_previous(self):
        """Select the previous chat using efficient chat order navigation."""
        if not self._chat_order:
            return

        if self._selected_chat_id is None:
            # No selection, select last chat
            self._selected_chat_id = self._chat_order[-1]
        else:
            # Find current position and move to previous
            try:
                current_index = self._chat_order.index(self._selected_chat_id)
                prev_index = max(current_index - 1, 0)
                self._selected_chat_id = self._chat_order[prev_index]
            except ValueError:
                # Current selection not in order, select last
                self._selected_chat_id = self._chat_order[-1]

        self._update_visual_selection()

    def action_open_selected(self):
        """Open the selected chat using efficient ID-based lookup."""
        if self._selected_chat_id and self._selected_chat_id in self._chat_widgets:
            # Get the chat widget and extract the chat object
            chat_widget = self._chat_widgets[self._selected_chat_id]
            self.post_message(ChatMessages.Switched(chat_widget.chat))

    def action_new_chat(self):
        """Request a new chat."""
        # Post Textual message that will bubble up to parent handlers
        self.post_message(ChatMessages.NewRequested())

    def action_rename_chat(self):
        """Rename the selected chat using efficient ID-based lookup."""
        if self._selected_chat_id and self._selected_chat_id in self._chat_widgets:
            # Get the chat widget and extract the chat object
            chat_widget = self._chat_widgets[self._selected_chat_id]
            self.app.run_worker(
                self._rename_chat_worker(chat_widget.chat, chat_widget.title)
            )

    async def _rename_chat_worker(self, chat: BasicChat, current_title: str):
        """Worker method to handle rename chat dialog."""
        dialog = EditNameDialog(current_title)
        new_name = await self.app.push_screen_wait(dialog)

        if new_name:  # User confirmed and entered a name
            try:
                chat.name = new_name
                Settings.logger.info(f"Renamed chat to: {new_name}")

            except Exception as e:
                Settings.logger.error(f"Error renaming chat: {e}")

    def action_delete_chat(self):
        """Delete the selected chat using efficient ID-based lookup."""
        if self._selected_chat_id and self._selected_chat_id in self._chat_widgets:
            # Get the chat widget and extract the chat object
            chat_widget = self._chat_widgets[self._selected_chat_id]
            self.app.run_worker(
                self._delete_chat_worker(chat_widget.chat, chat_widget.title)
            )

    async def _delete_chat_worker(self, chat: BasicChat, title: str):
        """Delete chat after user confirmation."""
        dialog = ConfirmDeleteDialog(title)
        confirmed = await self.app.push_screen_wait(dialog)

        if confirmed:  # User confirmed deletion
            try:
                # Store chat ID before deletion since chat object becomes invalid after delete()
                chat_id = chat.id
                
                # Delete chat via API - backend will notify us when done
                chat.delete()
                Settings.logger.info(f"Requested deletion of chat: {title} (ID: {chat_id})")
            except Exception as e:
                Settings.logger.error(f"Error deleting chat: {e}")
