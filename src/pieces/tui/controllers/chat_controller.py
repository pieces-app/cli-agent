"""Controller for handling chat-related events."""

from typing import Optional, TYPE_CHECKING
from pieces.settings import Settings
from pieces.copilot.ltm import update_ltm_cache
from .base_controller import BaseController, EventType

from pieces._vendor.pieces_os_client.wrapper.websockets.conversations_ws import (
    ConversationWS,
)
from pieces._vendor.pieces_os_client.wrapper.basic_identifier.chat import BasicChat

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.models.conversation import Conversation


class ChatController(BaseController):
    """Handles chat-related events from the backend."""

    def __init__(self):
        """Initialize the chat controller."""
        super().__init__()
        self._conversation_ws = None

    def initialize(self):
        """Set up WebSocket listeners for chat events."""
        if self._initialized:
            return

        self._conversation_ws = ConversationWS.get_instance() or ConversationWS(
            pieces_client=Settings.pieces_client,
            on_conversation_update=self._on_conversation_update,
            on_conversation_remove=self._on_conversation_remove,
        )
        self._conversation_ws.start()

        self._initialized = True
        Settings.logger.info("ChatController initialized.")

    def cleanup(self):
        """Stop listening to chat events."""
        try:
            if self._conversation_ws:
                Settings.logger.debug("Closing conversation WebSocket...")
                self._conversation_ws.close()
                Settings.logger.debug("Conversation WebSocket closed successfully")
        except Exception as e:
            Settings.logger.error(
                f"Failed to properly close conversation WebSocket: {e}"
            )
            Settings.logger.info(
                "WebSocket cleanup incomplete - connection may remain active"
            )
        finally:
            self._conversation_ws = None

    def _on_conversation_update(self, conversation: "Conversation"):
        """Handle conversation update from WebSocket."""
        try:
            self.emit(EventType.CHAT_UPDATED, BasicChat(conversation.id))
        except Exception as e:
            Settings.logger.error(f"Error handling chat update: {e}")

    def _on_conversation_remove(self, conversation: "Conversation"):
        """Handle chat removal from WebSocket."""
        self.emit(EventType.CHAT_DELETED, conversation.id)

    def switch_chat(self, chat: Optional["BasicChat"]):
        """
        Switch to a different chat.

        Args:
            chat: The BasicChat object to switch to (None for new chat)
        """
        if not chat:
            chat = Settings.pieces_client.copilot.create_chat()
        Settings.pieces_client.copilot.chat = chat
        self.emit(EventType.CHAT_SWITCHED, chat)

    def create_new_chat(self):
        """Create a new chat and notify listeners."""
        self.switch_chat(None)

    def is_ltm_running(self) -> bool:
        update_ltm_cache()
        return Settings.pieces_client.copilot.context.ltm.is_enabled

    def activate_ltm(self):
        Settings.pieces_client.copilot.context.ltm.chat_enable_ltm()

    def deactivate_ltm(self):
        Settings.pieces_client.copilot.context.ltm.chat_disable_ltm()

    def is_chat_ltm_enabled(self) -> bool:
        return Settings.pieces_client.copilot.context.ltm.is_chat_ltm_enabled
