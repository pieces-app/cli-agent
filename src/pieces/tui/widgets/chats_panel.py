"""Enhanced chats panel widget with keyboard navigation."""

from typing import List, Optional
from textual.app import ComposeResult
from textual.widgets import Static, Button
from textual.containers import ScrollableContainer, Container
from textual.reactive import reactive
from textual.message import Message
from textual.binding import Binding

from pieces._vendor.pieces_os_client.wrapper.basic_identifier.chat import BasicChat


class ChatMessages:
    """Container for all chat-related messages."""

    class ChatSelected(Message):
        """Message sent when a chat is selected."""

        def __init__(self, chat: BasicChat):
            super().__init__()
            self.chat = chat

    class NewChatRequested(Message):
        """Message sent when new chat is requested."""

        pass

    class ChatSwitched(Message):
        """Message sent when chat is switched."""

        def __init__(self, chat: BasicChat):
            super().__init__()
            self.chat = chat


class ChatItem(Container):
    """A single chat item in the list."""

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
        self.add_class("conversation-item")

        if is_active:
            self.add_class("conversation-active")
        if is_selected:
            self.add_class("conversation-selected")

    def compose(self) -> ComposeResult:
        """Compose the chat item."""
        with Container(classes="conversation-content"):
            yield Static(self.title, classes="conversation-title")
            if self.summary:
                yield Static(self.summary, classes="conversation-summary")

    def on_click(self) -> None:
        """Handle chat item click."""
        self.post_message(ChatMessages.ChatSelected(self.chat))

    def select(self):
        """Select this chat item."""
        self.is_selected = True
        self.add_class("conversation-selected")

    def deselect(self):
        """Deselect this chat item."""
        self.is_selected = False
        self.remove_class("conversation-selected")


class ChatsPanel(ScrollableContainer):
    """Enhanced chats panel with keyboard navigation."""

    chats: reactive[List[tuple]] = reactive([])  # (chat, title, summary)
    active_chat: reactive[Optional[BasicChat]] = reactive(None)
    selected_index: int = -1

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
        self.add_class("conversations-panel")
        self.chat_items: List[ChatItem] = []

    def compose(self) -> ComposeResult:
        """Compose the chats panel."""
        # New chat button
        with Container(classes="new-conversation-container"):
            yield Button("+ New Chat", id="new-chat", classes="new-conversation-btn")

        # Chats list container
        with Container(classes="conversations-list", id="chats-container"):
            yield Static("No chats yet...", classes="empty-conversations")

    def add_chat(self, chat: BasicChat, title: str, summary: str = ""):
        """Add a new chat to the list."""
        self.chats.append((chat, title, summary))
        self.refresh_chats()

    def load_chats(self, chats_list: List[BasicChat]):
        """Load a list of chat objects."""
        self.chats.clear()

        for idx, chat in enumerate(chats_list, 1):
            title = getattr(chat, "name", f"Chat {idx}")
            summary = getattr(chat, "summary", "")
            if summary and len(summary) > 50:
                summary = summary[:47] + "..."

            self.chats.append((chat, title, summary))

        self.refresh_chats()

        # Select first chat if available
        if self.chats and self.selected_index == -1:
            self.selected_index = 0
            self._update_selection()

    def set_active_chat(self, chat: Optional[BasicChat]):
        """Set the active chat."""
        self.active_chat = chat
        self.refresh_chats()

    def refresh_chats(self):
        """Refresh the chats display."""
        chats_container = self.query_one("#chats-container")
        chats_container.remove_children()
        self.chat_items.clear()

        if not self.chats:
            chats_container.mount(
                Static("No chats yet...", classes="empty-conversations")
            )
            return

        for idx, (chat, title, summary) in enumerate(self.chats):
            is_active = chat == self.active_chat
            is_selected = idx == self.selected_index

            chat_item = ChatItem(
                chat=chat,
                title=title,
                summary=summary,
                is_active=is_active,
                is_selected=is_selected,
            )
            self.chat_items.append(chat_item)
            chats_container.mount(chat_item)

    def clear_chats(self):
        """Clear all chats."""
        self.chats.clear()
        self.active_chat = None
        self.selected_index = -1
        self.chat_items.clear()
        self.refresh_chats()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "new-chat":
            self.post_message(ChatMessages.NewChatRequested())

    async def on_chat_item_chat_selected(
        self, message: ChatMessages.ChatSelected
    ) -> None:
        """Handle chat selection."""
        # Find and update selected index
        for idx, (chat, _, _) in enumerate(self.chats):
            if chat == message.chat:
                self.selected_index = idx
                break

        self.set_active_chat(message.chat)
        self.post_message(ChatMessages.ChatSwitched(message.chat))

    # Keyboard navigation
    def action_select_next(self):
        """Select the next chat."""
        if self.chats:
            self.selected_index = min(self.selected_index + 1, len(self.chats) - 1)
            self._update_selection()

    def action_select_previous(self):
        """Select the previous chat."""
        if self.chats:
            self.selected_index = max(self.selected_index - 1, 0)
            self._update_selection()

    def action_open_selected(self):
        """Open the selected chat."""
        if 0 <= self.selected_index < len(self.chats):
            chat, _, _ = self.chats[self.selected_index]
            self.post_message(ChatMessages.ChatSelected(chat))

    def action_new_chat(self):
        """Request a new chat."""
        self.post_message(ChatMessages.NewChatRequested())

    def action_rename_chat(self):
        """Rename the selected chat."""
        # TODO: Implement rename functionality
        pass

    def action_delete_chat(self):
        """Delete the selected chat."""
        # TODO: Implement delete functionality
        pass

    def _update_selection(self):
        """Update the visual selection."""
        # Update all chat items
        for idx, item in enumerate(self.chat_items):
            if idx == self.selected_index:
                item.select()
                self.scroll_to_widget(item)
            else:
                item.deselect()
