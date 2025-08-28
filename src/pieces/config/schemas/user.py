"""
User data configuration schema.
"""

from pydantic import BaseModel, Field, field_validator
from pieces.config.utils import validate_semver


class UserDataSchema(BaseModel):
    """Schema for user data configuration."""

    schema_version: str = Field(
        default="1.0.0", description="Configuration schema version"
    )

    # Onboarding status - that's it!
    is_onboarded: bool = Field(
        default=False, description="Whether user has completed onboarding"
    )
    onboarding_step: int = Field(
        default=1, description="Current onboarding step (1, 2, 3, etc.)"
    )
    skip_onboarding: bool = Field(default=False, description="Skip onboarding process")

    @field_validator("schema_version", mode="before")
    @classmethod
    def validate_semver_field(cls, v):
        return validate_semver(v)

    @field_validator("onboarding_step")
    @classmethod
    def validate_onboarding_step(cls, v):
        """Validate onboarding step."""
        if v < 1 or v > 8:
            return 1
        return v
