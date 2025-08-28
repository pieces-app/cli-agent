"""
CLI configuration schema.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator
from pieces.config.utils import validate_semver


class CLIConfigSchema(BaseModel):
    """Schema for CLI configuration."""

    schema_version: str = Field(
        default="1.0.0", description="Configuration schema version"
    )
    editor: Optional[str] = Field(default=None, description="Default editor command")
    theme: str = Field(default="pieces-dark", description="TUI theme preference")

    @field_validator("editor")
    @classmethod
    def validate_editor(cls, v):
        """Validate editor command."""
        if v is not None and len(v.strip()) == 0:
            return None
        return v

    @field_validator('schema_version', mode='before')
    @classmethod
    def validate_semver_field(cls, v):
        return validate_semver(v)