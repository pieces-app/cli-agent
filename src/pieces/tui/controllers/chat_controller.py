"""Controller for handling chat-related events."""

from datetime import datetime, timedelta
from typing import Optional, TYPE_CHECKING
from pieces.settings import Settings
from pieces.copilot.ltm import update_ltm_cache
from .base_controller import BaseController, EventType

from pieces._vendor.pieces_os_client.wrapper.websockets.conversations_ws import (
    ConversationWS,
)
from pieces._vendor.pieces_os_client.wrapper.basic_identifier.chat import BasicChat
from pieces._vendor.pieces_os_client.wrapper.basic_identifier.range import BasicRange
from pieces._vendor.pieces_os_client.wrapper.streamed_identifiers import (
    ConversationsSnapshot,
)

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.models.conversation import Conversation


def _activate_chat_ltm_with_lookback() -> None:
    """Activate Chat-LTM with a configurable lookback window.

    Mirrors ``ltm.chat_enable_ltm()`` but lets the caller widen the
    backing range. The SDK default is 15 minutes, far too narrow for
    long-term-memory; we honor
    ``cli_config.auto_enable_chat_ltm_lookback_days`` (default 7) to
    cover a typical work week. Setting the value to 0 falls back to
    the SDK default for users who want only the most recent context.

    The trailing local-cache refresh mirrors what ``chat_enable_ltm``
    does so callers reading ``conversation.ranges`` immediately after
    see the new range without an extra round-trip.
    """
    days = Settings.cli_config.auto_enable_chat_ltm_lookback_days
    chat = Settings.pieces_client.copilot.chat
    if not chat:
        chat = Settings.pieces_client.copilot.create_chat("New Conversation")

    if days > 0:
        chat.associate_range(
            BasicRange.create(from_=datetime.now() - timedelta(days=days))
        )
    else:
        chat.associate_range(BasicRange.create())  # SDK 15-min default

    conv = Settings.pieces_client.conversation_api.conversation_get_specific_conversation(
        chat.id
    )
    ConversationsSnapshot.identifiers_snapshot[conv.id] = conv


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
        fresh_chat_created = chat is None
        if not chat:
            chat = Settings.pieces_client.copilot.create_chat()
        Settings.pieces_client.copilot.chat = chat

        if fresh_chat_created:
            self._maybe_auto_enable_chat_ltm()

        self.emit(EventType.CHAT_SWITCHED, chat)

    def _maybe_auto_enable_chat_ltm(self) -> None:
        """Auto-attach LTM to a freshly-created chat when the user opts in.

        Two preconditions must hold: the user has set
        ``cli_config.auto_enable_chat_ltm`` (opt-in, default False) AND
        the system-level workstream pattern engine is already enabled.
        Without the second check, this would silently do nothing on a
        machine where LTM permissions were never granted.

        Failures are logged and swallowed: a transient API hiccup must
        not break chat creation. The user can always toggle manually
        with Ctrl+L if auto-enable did not land.
        """
        try:
            if not Settings.cli_config.auto_enable_chat_ltm:
                return
            if self.is_chat_ltm_enabled():
                return
            if not self.is_ltm_running():
                return
            _activate_chat_ltm_with_lookback()
        except Exception as e:
            Settings.logger.error(
                f"Auto-enable Chat-LTM failed: {e}"
            )

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
