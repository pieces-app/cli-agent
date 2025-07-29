"""Central event hub for managing all controllers and bridging to Textual messages."""

from typing import Dict, TYPE_CHECKING
from pieces.settings import Settings
from .base_controller import BaseController, EventType
from .chat_controller import ChatController
from .model_controller import ModelController
from .material_controller import MaterialController
from .connection_controller import ConnectionController
from .copilot_controller import CopilotController

if TYPE_CHECKING:
    from textual.app import App


class EventHub:
    """Central hub for managing all controllers and bridging to Textual messages."""

    def __init__(self, app: "App"):
        """
        Initialize the event hub.

        Args:
            app: The Textual application instance
        """
        self.app = app
        self._controllers: Dict[str, BaseController] = {}
        self._initialized = False

        # Create controllers
        self._controllers["chat"] = ChatController()
        self._controllers["model"] = ModelController()
        self._controllers["material"] = MaterialController()
        self._controllers["connection"] = ConnectionController()
        self._controllers["copilot"] = CopilotController()

    def initialize(self):
        """Initialize all controllers and set up event bridging."""
        if self._initialized:
            return

        Settings.logger.info("Initializing EventHub")

        for name, controller in self._controllers.items():
            try:
                controller.initialize()
                Settings.logger.info(f"Initialized {name} controller")
            except Exception as e:
                Settings.logger.error(f"Failed to initialize {name} controller: {e}")

        # Set up event listeners to bridge controller events to Textual messages
        self._setup_event_bridging()
        self._initialized = True

    def _setup_event_bridging(self):
        """Set up event listeners to bridge controller events to Textual messages."""
        # Import here to avoid circular imports
        from ..messages import (
            ChatMessages,
            UserMessages,
            ModelMessages,
            CopilotMessages,
            ConnectionMessages,
            MaterialMessages,
            ContextMessages,
        )

        # Connection events
        self.connection.on(
            EventType.CONNECTION_ESTABLISHED,
            lambda data: self.app.post_message(
                ConnectionMessages.Established(
                    data.get("endpoint", "Pieces OS") if data else "Pieces OS"
                )
            ),
        )
        self.connection.on(
            EventType.CONNECTION_LOST,
            lambda data: self.app.post_message(
                ConnectionMessages.Lost(data.get("reason") if data else None)
            ),
        )
        self.connection.on(
            EventType.CONNECTION_RECONNECTING,
            lambda _: self.app.post_message(ConnectionMessages.Reconnecting()),
        )

        # Chat events
        self.chat.on(
            EventType.CHAT_UPDATED,
            lambda chat: self.app.post_message(ChatMessages.Updated(chat)),
        )
        self.chat.on(
            EventType.CHAT_DELETED,
            lambda chat: self.app.post_message(ChatMessages.Deleted(chat)),
        )
        self.chat.on(
            EventType.CHAT_SWITCHED,
            lambda chat: self.app.post_message(ChatMessages.Switched(chat)),
        )
        self.chat.on(
            EventType.CHAT_SELECTED,
            lambda chat: self.app.post_message(ChatMessages.Selected(chat)),
        )
        self.chat.on(
            EventType.CHAT_NEW_REQUESTED,
            lambda _: self.app.post_message(ChatMessages.NewRequested()),
        )

        # User input events
        self.chat.on(
            EventType.USER_INPUT_SUBMITTED,
            lambda data: self.app.post_message(
                UserMessages.InputSubmitted(data["text"], data.get("timestamp"))
            ),
        )

        # Model events
        self.model.on(
            EventType.MODEL_CHANGED,
            lambda model: self.app.post_message(ModelMessages.Changed(model)),
        )

        # Material/Context events
        self.material.on(
            EventType.CONTEXT_ADDED,
            lambda data: self.app.post_message(
                ContextMessages.Added(data["context_type"], data["context_data"])
            ),
        )
        self.material.on(
            EventType.CONTEXT_REMOVED,
            lambda data: self.app.post_message(
                ContextMessages.Removed(data["context_type"], data["context_data"])
            ),
        )
        self.material.on(
            EventType.CONTEXT_CLEARED,
            lambda data: self.app.post_message(ContextMessages.Cleared(data["count"])),
        )

        # Copilot events
        self.copilot.on(
            EventType.COPILOT_THINKING_STARTED,
            lambda data: self.app.post_message(
                CopilotMessages.ThinkingStarted(data["query"])
            ),
        )
        self.copilot.on(
            EventType.COPILOT_THINKING_ENDED,
            lambda _: self.app.post_message(CopilotMessages.ThinkingEnded()),
        )
        self.copilot.on(
            EventType.COPILOT_STREAM_STARTED,
            lambda data: self.app.post_message(
                CopilotMessages.StreamStarted(data["text"])
            ),
        )
        self.copilot.on(
            EventType.COPILOT_STREAM_CHUNK,
            lambda data: self.app.post_message(
                CopilotMessages.StreamChunk(data["chunk"], data["full_text"])
            ),
        )
        self.copilot.on(
            EventType.COPILOT_STREAM_COMPLETED,
            lambda data: self.app.post_message(
                CopilotMessages.StreamCompleted(data["final_text"])
            ),
        )
        self.copilot.on(
            EventType.COPILOT_STREAM_ERROR,
            lambda data: self.app.post_message(
                CopilotMessages.StreamError(data["error"])
            ),
        )

    def cleanup(self):
        """Clean up all controllers."""
        Settings.logger.info("Cleaning up EventHub")

        for name, controller in self._controllers.items():
            try:
                controller.cleanup()
                Settings.logger.info(f"Cleaned up {name} controller")
            except Exception as e:
                Settings.logger.error(f"Error cleaning up {name} controller: {e}")

        self._initialized = False

    # Expose controllers for app to use directly
    @property
    def chat(self) -> ChatController:
        """Get the chat controller."""
        return self._controllers["chat"]  # pyright: ignore[reportReturnType]

    @property
    def model(self) -> ModelController:
        """Get the model controller."""
        return self._controllers["model"]  # pyright: ignore[reportReturnType]

    @property
    def material(self) -> MaterialController:
        """Get the material controller."""
        return self._controllers["material"]  # pyright: ignore[reportReturnType]

    @property
    def connection(self) -> ConnectionController:
        """Get the connection controller."""
        return self._controllers["connection"]  # pyright: ignore[reportReturnType]

    @property
    def copilot(self) -> CopilotController:
        """Get the copilot controller."""
        return self._controllers["copilot"]  # pyright: ignore[reportReturnType]

    def get_controller(self, name: str) -> BaseController:
        """
        Get a controller by name.

        Args:
            name: Name of the controller

        Returns:
            The controller instance

        Raises:
            KeyError: If controller not found
        """
        return self._controllers[name]

    # Convenience methods that delegate to controllers
    def is_connected(self) -> bool:
        """Check if connected to Pieces OS."""
        return self.connection.is_connected()

    def get_current_model(self):
        """Get current model from model controller."""
        return self.model.get_current_model()

    def get_current_chat(self):
        """Get current chat from copilot controller."""
        return self.copilot.get_current_chat()

    def get_chats(self):
        """Get all chats from chat controller."""
        return self.chat.get_chats()

    def create_new_chat(self):
        """Create new chat via chat controller."""
        self.chat.create_new_chat()

    def ask_question(self, question: str):
        """Ask question via copilot controller."""
        Settings.logger.info(f"EventHub: Asking question: {question[:50]}...")
        self.copilot.ask_question(question)
