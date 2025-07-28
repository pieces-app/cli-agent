"""Central event hub for managing all controllers."""

from typing import Dict, TYPE_CHECKING
from pieces.settings import Settings
from .base_controller import BaseController
from .chat_controller import ChatController
from .model_controller import ModelController
from .material_controller import MaterialController
from .connection_controller import ConnectionController
from .copilot_controller import CopilotController

if TYPE_CHECKING:
    from textual.app import App


class EventHub:
    """Central hub for managing all event controllers."""

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
        """Initialize all controllers."""
        if self._initialized:
            return

        Settings.logger.info("Initializing EventHub")

        for name, controller in self._controllers.items():
            try:
                controller.initialize()
                Settings.logger.info(f"Initialized {name} controller")
            except Exception as e:
                Settings.logger.error(f"Failed to initialize {name} controller: {e}")

        self._initialized = True

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
