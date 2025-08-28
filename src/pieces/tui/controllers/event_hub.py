"""Central event hub for managing all controllers and bridging to Textual messages."""

from typing import Dict, TYPE_CHECKING
from pieces.settings import Settings
from .base_controller import BaseController, EventType
from .chat_controller import ChatController
from .model_controller import ModelController
from .connection_controller import ConnectionController
from .copilot_controller import CopilotController
from .workstream_controller import WorkstreamController

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
        self._controllers["connection"] = ConnectionController()
        self._controllers["copilot"] = CopilotController()
        self._controllers["workstream"] = WorkstreamController()

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

    def _post_to_all_targets(self, message):
        """Post message to both app and current screen for maximum compatibility."""
        try:
            self.app.post_message(message)
            current_screen = self.app.screen
            if current_screen:
                current_screen.post_message(message)

                # Also post directly to specific widgets that need the message
                self._post_to_widgets(current_screen, message)

            Settings.logger.info(f"Posted message to all targets: {current_screen}")

        except Exception as e:
            Settings.logger.error(f"Error posting message to all targets: {e}")
            # Fallback to just app
            self.app.post_message(message)

    def _post_to_widgets(self, screen, message):
        """Post messages directly to widgets that need them."""
        try:
            # Import here to avoid circular imports
            from ..messages import ChatMessages, WorkstreamMessages

            # Post ChatMessages to chat widgets
            if isinstance(
                message,
                (
                    ChatMessages.Updated,
                    ChatMessages.Deleted,
                    ChatMessages.Switched,
                    ChatMessages.NewRequested,
                ),
            ):
                if hasattr(screen, "chat_list_panel") and screen.chat_list_panel:
                    # Use call_later to ensure we're on the main thread
                    chat_panel = screen.chat_list_panel
                    self.app.call_later(
                        lambda msg=message, panel=chat_panel: panel.post_message(msg)
                    )

            # Post WorkstreamMessages to workstream widgets
            elif isinstance(
                message,
                (
                    WorkstreamMessages.Updated,
                    WorkstreamMessages.Deleted,
                    WorkstreamMessages.Switched,
                ),
            ):
                if (
                    hasattr(screen, "workstream_activities_panel")
                    and screen.workstream_activities_panel
                ):
                    # Use call_later to ensure we're on the main thread
                    workstream_panel = screen.workstream_activities_panel
                    self.app.call_later(
                        lambda msg=message, panel=workstream_panel: panel.post_message(
                            msg
                        )
                    )

        except Exception as e:
            Settings.logger.error(f"Error posting to widgets: {e}")

    def _setup_event_bridging(self):
        """Set up event listeners to bridge controller events to Textual messages."""
        # Import here to avoid circular imports
        from ..messages import (
            ChatMessages,
            ModelMessages,
            CopilotMessages,
            ConnectionMessages,
            WorkstreamMessages,
        )

        # Connection events
        self.connection.on(
            EventType.CONNECTION_ESTABLISHED,
            lambda _: self._post_to_all_targets(ConnectionMessages.Established()),
        )
        self.connection.on(
            EventType.CONNECTION_LOST,
            lambda _: self._post_to_all_targets(ConnectionMessages.Lost()),
        )
        self.connection.on(
            EventType.CONNECTION_RECONNECTING,
            lambda _: self._post_to_all_targets(ConnectionMessages.Reconnecting()),
        )

        # Chat events - post to both app and current screen for maximum compatibility
        self.chat.on(
            EventType.CHAT_UPDATED,
            lambda chat: self._post_to_all_targets(ChatMessages.Updated(chat)),
        )
        self.chat.on(
            EventType.CHAT_DELETED,
            lambda chat_id: self._post_to_all_targets(ChatMessages.Deleted(chat_id)),
        )
        self.chat.on(
            EventType.CHAT_SWITCHED,
            lambda chat: self._post_to_all_targets(ChatMessages.Switched(chat)),
        )

        self.copilot.on(
            EventType.CHAT_SWITCHED,
            lambda chat: self._post_to_all_targets(ChatMessages.Switched(chat)),
        )

        # Model events - post to current screen to ensure proper message routing
        self.model.on(
            EventType.MODEL_CHANGED,
            lambda model: self._post_to_all_targets(ModelMessages.Changed(model)),
        )

        # Material/Context events
        # self.material.on(
        #     EventType.CONTEXT_ADDED,
        #     lambda data: self.app.post_message(
        #         ContextMessages.Added(data["context_type"], data["context_data"])
        #     ),
        # )
        # self.material.on(
        #     EventType.CONTEXT_REMOVED,
        #     lambda data: self.app.post_message(
        #         ContextMessages.Removed(data["context_type"], data["context_data"])
        #     ),
        # )
        # self.material.on(
        #     EventType.CONTEXT_CLEARED,
        #     lambda data: self.app.post_message(ContextMessages.Cleared(data["count"])),
        # )

        # Copilot events - post to current screen to ensure proper message routing
        self.copilot.on(
            EventType.COPILOT_THINKING_STARTED,
            lambda _: self._post_to_all_targets(CopilotMessages.ThinkingStarted()),
        )
        self.copilot.on(
            EventType.COPILOT_THINKING_ENDED,
            lambda _: self._post_to_all_targets(CopilotMessages.ThinkingEnded()),
        )
        self.copilot.on(
            EventType.COPILOT_STREAM_STARTED,
            lambda data: self._post_to_all_targets(CopilotMessages.StreamStarted(data)),
        )
        self.copilot.on(
            EventType.COPILOT_STREAM_CHUNK,
            lambda data: self._post_to_all_targets(
                CopilotMessages.StreamChunk(data["text"], data["full_text"])
            ),
        )
        self.copilot.on(
            EventType.COPILOT_STREAM_COMPLETED,
            lambda data: self._post_to_all_targets(
                CopilotMessages.StreamCompleted(data)
            ),
        )
        self.copilot.on(
            EventType.COPILOT_STREAM_ERROR,
            lambda data: self._post_to_all_targets(
                CopilotMessages.StreamError(data["error"])
            ),
        )

        # Workstream events - post to current screen to ensure proper message routing
        self.workstream.on(
            EventType.WORKSTREAM_SUMMARY_UPDATED,
            lambda summary: self._post_to_all_targets(
                WorkstreamMessages.Updated(summary)
            ),
        )
        self.workstream.on(
            EventType.WORKSTREAM_SUMMARY_DELETED,
            lambda summary_id: self._post_to_all_targets(
                WorkstreamMessages.Deleted(summary_id)
            ),
        )
        self.workstream.on(
            EventType.WORKSTREAM_SUMMARY_SWITCHED,
            lambda summary: self._post_to_all_targets(
                WorkstreamMessages.Switched(summary)
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
    def connection(self) -> ConnectionController:
        """Get the connection controller."""
        return self._controllers["connection"]  # pyright: ignore[reportReturnType]

    @property
    def copilot(self) -> CopilotController:
        """Get the copilot controller."""
        return self._controllers["copilot"]  # pyright: ignore[reportReturnType]

    @property
    def workstream(self) -> WorkstreamController:
        """Get the workstream controller."""
        return self._controllers["workstream"]  # pyright: ignore[reportReturnType]

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
        return Settings.pieces_client.copilot.chat

    def create_new_chat(self):
        """Create new chat via chat controller."""
        self.chat.create_new_chat()

    def ask_question(self, question: str):
        """Ask question via copilot controller."""
        Settings.logger.info(f"EventHub: Asking question: {question[:50]}...")
        self.copilot.ask_question(question)

    def stop_streaming(self):
        """Stop current streaming operation via copilot controller."""
        Settings.logger.info("EventHub: Stopping streaming...")
        self.copilot.stop_streaming()
