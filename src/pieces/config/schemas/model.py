"""
Model configuration schema.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator
from pieces.config.utils import validate_semver


class ModelInfo(BaseModel):
    """Simple model info with name and UUID."""

    name: str = Field(..., description="Human-readable model name")
    uuid: str = Field(..., description="Unique model identifier (UUID)")


def get_default_model_info() -> ModelInfo:
    from pieces.settings import Settings

    models = Settings.pieces_client.models_object
    if not models:
        raise ValueError("No models available for default ModelInfo")
    for model in models:
        if (
            model.unique == "gemini-2.0-flash-lite-001"
        ):  # TODO: Change this model if it is deprecated
            return ModelInfo(name=model.name, uuid=model.id)
    raise ValueError("Default model not found in available models")


class ModelConfigSchema(BaseModel):
    """Schema for model configuration."""

    schema_version: str = Field(
        default="1.0.0", description="Configuration schema version"
    )

    auto_commit_model: ModelInfo = Field(
        default_factory=get_default_model_info, description="Model used for auto-commit"
    )
    model: Optional[ModelInfo] = Field(default=None, description="Default/main model")

    @field_validator("schema_version", mode="before")
    @classmethod
    def validate_semver_field(cls, v):
        return validate_semver(v)

    @field_validator("auto_commit_model", "model", mode="before")
    @classmethod
    def validate_model_info(cls, v):
        from pieces.settings import Settings

        for model_name, model_id in Settings.pieces_client.get_models().items():
            if model_id == v.uuid:
                return ModelInfo(name=model_name, uuid=model_id)
        raise ValueError("Model UUID not found in available models")
