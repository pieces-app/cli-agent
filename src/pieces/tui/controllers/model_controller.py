"""Controller for handling model-related events."""

from typing import Optional, List, TYPE_CHECKING
import threading
from pieces.settings import Settings
from .base_controller import BaseController, EventType

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.models.model import Model


class ModelController(BaseController):
    """Handles model-related events and changes."""

    def __init__(self):
        """Initialize the model controller."""
        super().__init__()
        self._current_model: Optional["Model"] = None
        self._available_models: List["Model"] = []
        self._polling_thread: Optional[threading.Thread] = None
        self._stop_polling = threading.Event()

    def initialize(self):
        """Start monitoring for model changes."""
        if self._initialized:
            return

        try:
            model_id = Settings.get_model_id()
            for model in Settings.pieces_client.models_object:
                if model.id == model_id:
                    self._current_model = model
            self._initialized = True
            Settings.logger.info("ModelController initialized")

        except Exception as e:
            Settings.logger.error(f"Failed to initialize ModelController: {e}")

    def cleanup(self):
        """Stop monitoring for model changes."""
        # Stop polling thread
        if self._polling_thread:
            self._stop_polling.set()
            self._polling_thread.join(timeout=2)
            self._polling_thread = None

        self._initialized = False

    def _get_current_model_name(self) -> Optional[str]:
        """Get the current model name."""
        return Settings.get_model()

    def change_model(self, model_name: str) -> bool:
        """
        Change the current model.

        Args:
            model_name: Name of the model to switch to

        Returns:
            True if successful, False otherwise
        """
        try:
            # Find the model in available models
            model = None
            for m in self._available_models:
                if m.name == model_name:
                    model = m
                    break

            if not model:
                Settings.logger.error(f"Model '{model_name}' not found")
                return False

            # Change the model
            # TODO: Update the local cache here and the file
            Settings.pieces_client.model_id = str(model.id)

            self._current_model = model

            # Emit event
            self.emit(EventType.MODEL_CHANGED, model)

            return True

        except Exception as e:
            Settings.logger.error(f"Error changing model: {e}")
            return False

    def get_current_model(self) -> Optional["Model"]:
        """Get the current model name."""
        return self._current_model

    def get_available_models(self) -> List["Model"]:
        """Get list of available models."""
        return self._available_models.copy()
