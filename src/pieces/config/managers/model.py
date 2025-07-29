"""
Model configuration manager.
"""

from pathlib import Path
from typing import Optional
from ..schemas.model import ModelConfigSchema, ModelInfo
from .base import BaseConfigManager


class ModelManager(BaseConfigManager[ModelConfigSchema]):
    """Manager for model configuration."""

    def __init__(self, config_path: Path):
        """
        Initialize model manager.

        Args:
            config_path: Full path to the model configuration file
        """
        super().__init__(config_path, ModelConfigSchema)

    # Auto-commit model management
    @property
    def auto_commit_model(self) -> ModelInfo:
        """Get auto-commit model."""
        return self.config.auto_commit_model

    @auto_commit_model.setter
    def auto_commit_model(self, model_info: ModelInfo) -> None:
        """
        Set auto-commit model.

        Args:
            name: Human-readable model name
            uuid: Model UUID
        """
        self.config.auto_commit_model = model_info
        self.save()

    @property
    def model(self) -> Optional[ModelInfo]:
        """Get default/main model."""
        return self.config.model

    @model.setter
    def model(self, model_info: ModelInfo) -> None:
        """
        Set default/main model.

        Args:
            name: Human-readable model name
            uuid: Model UUID
        """
        from pieces.settings import Settings

        self.config.model = model_info
        Settings.pieces_client.model_name = model_info.name
        self.save()

    def clear_model(self) -> None:
        """Clear default/main model."""
        self.config.model = None
        self.save()
