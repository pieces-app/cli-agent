"""Controller for handling model-related events."""

from typing import Optional, List, TYPE_CHECKING
import threading
from pieces.settings import Settings
from .base_controller import BaseController, EventType
from pieces.config.schemas.model import ModelInfo

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.models.model import Model


class ModelController(BaseController):
    """Handles model-related events and changes."""

    def __init__(self):
        """Initialize the model controller."""
        super().__init__()
        self._current_model: Optional["ModelInfo"] = None
        self._available_models: List["Model"] = []
        self._polling_thread: Optional[threading.Thread] = None
        self._stop_polling = threading.Event()

    def initialize(self):
        """Start monitoring for model changes."""
        if self._initialized:
            return

        try:
            model = Settings.model_config.model
            if not model:
                return
            self._current_model = model
            self._initialized = True
            Settings.logger.info("ModelController initialized")

        except Exception as e:
            Settings.logger.error(f"Failed to initialize ModelController: {e}")

    def cleanup(self):
        """Clean up model controller resources."""
        try:
            # Clear current model info if needed
            pass
        except Exception as e:
            Settings.logger.error(f"Error during model controller cleanup: {e}")

        # Clear all event listeners
        self._safe_cleanup()

    def _get_current_model_name(self) -> Optional[str]:
        """Get the current model name."""
        return self._current_model.name if self._current_model else None

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

            # Emit event
            Settings.pieces_client.model_name = model_name
            model_info = ModelInfo(
                name=model_name, uuid=Settings.pieces_client._model_id
            )
            Settings.model_config.model = model_info
            self.emit(EventType.MODEL_CHANGED, model_info)

            return True

        except Exception as e:
            Settings.logger.error(f"Error changing model: {e}")
            return False

    def get_current_model(self) -> Optional["ModelInfo"]:
        """Get the current model name."""
        return self._current_model

    def get_available_models(self) -> List["Model"]:
        """Get list of available models."""
        return [
            model
            for model in Settings.pieces_client.models_object
            if model.cloud or model.downloaded
        ]
