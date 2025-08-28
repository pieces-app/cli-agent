"""Workstream item widget for displaying workstream summary details in the list."""

from typing import TYPE_CHECKING
from textual.message import Message
from .base_item import BaseItem
from ..messages import WorkstreamMessages

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.wrapper.basic_identifier.summary import (
        BasicSummary,
    )


class WorkstreamItem(BaseItem):
    """A single workstream summary item in the list showing summary details."""

    def __init__(
        self,
        summary: "BasicSummary",
        title: str,
        subtitle: str = "",
        is_active: bool = False,
        is_selected: bool = False,
        **kwargs,
    ):
        # Store the summary for easy access
        self.summary = summary
        super().__init__(
            item=summary,
            title=title,
            subtitle=subtitle,
            is_active=is_active,
            is_selected=is_selected,
            **kwargs,
        )

    def create_selected_message(self, item) -> Message:
        """Create the appropriate message for when this workstream item is selected."""
        return WorkstreamMessages.SwitchRequested(item)

    def cleanup(self):
        """Clean up workstream-specific resources."""
        try:
            self.summary = None
        except (RuntimeError, ValueError, AttributeError):
            pass
        super().cleanup()
