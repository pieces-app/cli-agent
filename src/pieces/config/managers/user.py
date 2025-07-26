"""
User data configuration manager.
"""

from pathlib import Path
from ..schemas.user import UserDataSchema
from .base import BaseConfigManager


class UserManager(BaseConfigManager[UserDataSchema]):
    """Manager for user data configuration."""

    def __init__(self, config_path: Path):
        """
        Initialize user manager.

        Args:
            config_path: Full path to the user configuration file
        """
        super().__init__(config_path, UserDataSchema)

    @property
    def onboarded(self) -> bool:
        """Check if user has completed onboarding."""
        return self.config.is_onboarded

    @property
    def onboarding_step(self) -> int:
        """Get current onboarding step."""
        return self.config.onboarding_step

    @onboarding_step.setter
    def onboarding_step(self, step: int) -> None:
        self.config.onboarding_step = step
        self.save()

    @onboarded.setter
    def onboarded(self, value: bool) -> None:
        self.config.is_onboarded = value
        self.save()

    def complete_onboarding(self) -> None:
        """Mark onboarding as complete."""
        self.config.is_onboarded = True
        self.config.onboarding_step = 0
        self.save()

    @property
    def skip_onboarding(self) -> bool:
        """Check if onboarding should be skipped."""
        return self.config.skip_onboarding

    @skip_onboarding.setter
    def skip_onboarding(self, value: bool) -> None:
        self.config.skip_onboarding = value
        self.save()
