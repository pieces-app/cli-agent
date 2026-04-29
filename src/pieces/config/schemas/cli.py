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
    auto_enable_chat_ltm: bool = Field(
        default=False,
        description=(
            "Auto-attach Long-Term Memory to every new chat created in the "
            "TUI. Only takes effect when system LTM (workstream pattern "
            "engine) is already enabled. Defaults False so privacy-sensitive "
            "users opt in explicitly."
        ),
    )
    auto_enable_chat_ltm_lookback_days: int = Field(
        default=7,
        ge=0,
        description=(
            "When auto-attaching LTM to a chat, the range covers the last N "
            "days. The SDK default of 15 minutes is far too narrow for "
            "long-term memory; 7 days covers a typical work week. Set to 0 "
            "to keep the SDK 15-minute default (e.g. when a user only wants "
            "very recent context attached). Has no effect unless "
            "auto_enable_chat_ltm is also True."
        ),
    )

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