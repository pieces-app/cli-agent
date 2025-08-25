"""Workstream activities panel widget for displaying and managing workstream summaries."""

from typing import List, Optional, Tuple, TYPE_CHECKING
from textual.message import Message
from textual.css.query import NoMatches

from pieces.settings import Settings
from .base_list_panel import BaseListPanel
from .workstream_item import WorkstreamItem
from .dialogs import ConfirmDialog, EditNameDialog
from ..messages import WorkstreamMessages

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.wrapper.basic_identifier.summary import (
        BasicSummary,
    )


class WorkstreamActivitiesPanel(BaseListPanel):
    """Panel for displaying and managing workstream summaries."""

    def __init__(self, **kwargs):
        super().__init__(
            panel_title="Workstream Activities",
            empty_message="No workstream activities yet...",
            show_new_button=False,
            **kwargs,
        )

    def get_new_button_text(self) -> str:
        """Not used since show_new_button=False."""
        return ""

    def get_item_id(self, item: "BasicSummary") -> str:
        """Get a unique ID for a workstream summary."""
        return item.id

    def create_item_widget(
        self, item: "BasicSummary", title: str, subtitle: str
    ) -> WorkstreamItem:
        """Create a widget for a workstream summary."""
        is_active = item == self.active_item
        return WorkstreamItem(
            summary=item,
            title=title,
            subtitle=subtitle,
            is_active=is_active,
            is_selected=False,
        )

    def create_new_item_message(self) -> Message:
        """Not used since show_new_button=False."""
        from ..messages import ViewMessages

        return ViewMessages.SwitchToWorkstream()

    def extract_item_display_info(self, item: "BasicSummary") -> Tuple[str, str]:
        """Extract title and subtitle from a workstream summary."""
        title = item.name or "Untitled Summary"

        subtitle = ""
        # Create a subtitle from basic summary info
        # summary_annotation = item.summary_annotation()
        # subtitle = summary_annotation.raw_content if summary_annotation else ""
        #
        # # Limit subtitle length
        # if len(subtitle) > 50:
        #     subtitle = subtitle[:47] + "..."

        return title, subtitle

    def load_summaries(self, summaries: List["BasicSummary"]):
        """Load workstream summaries into the panel."""
        Settings.logger.info(f"Loading {len(summaries)} workstream summaries")
        self.load_items(summaries)

    def add_summary(self, summary: "BasicSummary", title: str, subtitle: str = ""):
        """Add a single new workstream summary efficiently."""
        # Add to data
        self.items = list(self.items) + [(summary, title, subtitle)]

        # Add widget incrementally
        if summary.id not in self._item_widgets:
            try:
                items_container = self.query_one("#items-container")
                self._add_item_widget(summary, title, subtitle, items_container)

                # Hide empty state
                empty_state = items_container.query_one("#empty-state")
                empty_state.display = False
            except NoMatches:
                # If container doesn't exist, skip the widget addition
                pass

    def add_summary_at_top(
        self, summary: "BasicSummary", title: str, subtitle: str = ""
    ):
        """Add a workstream summary at the top of the list."""
        # Add to data at the beginning
        self.items = [(summary, title, subtitle)] + list(self.items)

        # Add widget
        if summary.id not in self._item_widgets:
            try:
                items_container = self.query_one("#items-container")
                self._add_item_widget(summary, title, subtitle, items_container)

                # Hide empty state
                empty_state = items_container.query_one("#empty-state")
                empty_state.display = False

                # Move the new summary widget to the top
                self._reorder_item_widgets(items_container)
            except NoMatches:
                # If container doesn't exist, skip the widget addition
                pass

    def remove_summary(self, summary_id: str):
        """Remove a workstream summary from the UI."""
        # Remove from data - use safe filtering
        valid_summaries = []
        for summary, title, subtitle in self.items:
            try:
                if summary.id != summary_id:
                    valid_summaries.append((summary, title, subtitle))
            except (AttributeError, Exception):
                # Summary object is invalid/deleted, skip it
                continue
        self.items = valid_summaries

        # Remove widget
        if summary_id in self._item_widgets:
            widget = self._item_widgets[summary_id]
            if widget.is_mounted:
                widget.remove()
            del self._item_widgets[summary_id]
            if summary_id in self._item_order:
                self._item_order.remove(summary_id)

        # Update selection if the deleted summary was selected
        if self._selected_item_id == summary_id:
            if self._item_order:
                # Select the first available summary
                self._selected_item_id = self._item_order[0]
                self._update_visual_selection()
            else:
                self._selected_item_id = None

        # Show empty state if no summaries left
        if not self.items:
            try:
                items_container = self.query_one("#items-container")
                empty_state = items_container.query_one("#empty-state")
                empty_state.display = True
            except NoMatches:
                # If container doesn't exist, skip showing empty state
                pass

    def update_summary(self, summary: "BasicSummary", title: str, subtitle: str = ""):
        """Update a single workstream summary efficiently."""
        # Update data
        updated_summaries = []
        for existing_summary, existing_title, existing_subtitle in self.items:
            if existing_summary == summary:
                updated_summaries.append((summary, title, subtitle))
            else:
                updated_summaries.append(
                    (existing_summary, existing_title, existing_subtitle)
                )
        self.items = updated_summaries

        # Update widget incrementally
        self._update_item_widget(summary.id, summary, title, subtitle)

    def set_active_summary(self, summary: Optional["BasicSummary"]):
        """Set the active workstream summary."""
        self.set_active_item(summary)

    async def on_workstream_messages_switch_confirmed(
        self, message: WorkstreamMessages.SwitchConfirmed
    ) -> None:
        """Handle confirmed workstream summary switch event."""
        self._selected_item_id = message.summary.id
        self._update_visual_selection()

        # Set active summary for backend sync
        self.set_active_summary(message.summary)

    def action_rename_item(self):
        """Rename the selected workstream summary."""
        if self._selected_item_id and self._selected_item_id in self._item_widgets:
            summary_widget = self._item_widgets[self._selected_item_id]
            if hasattr(summary_widget, "summary"):
                self.app.run_worker(
                    self._rename_summary_worker(
                        summary_widget.summary,  # type: ignore
                        summary_widget.title,
                    )
                )

    def action_delete_item(self):
        """Delete the selected workstream summary."""
        if self._selected_item_id and self._selected_item_id in self._item_widgets:
            # Get the summary widget and extract the summary object
            summary_widget = self._item_widgets[self._selected_item_id]
            if hasattr(summary_widget, "summary"):
                self.app.run_worker(
                    self._delete_summary_worker(
                        summary_widget.summary,  # type: ignore
                        summary_widget.title,
                    )
                )

    def get_selected_summary(self) -> Optional["BasicSummary"]:
        """Get the currently selected workstream summary."""
        if self._selected_item_id and self._selected_item_id in self._item_widgets:
            summary_widget = self._item_widgets[self._selected_item_id]
            if hasattr(summary_widget, "summary"):
                return summary_widget.summary  # type: ignore
        return None

    # Message handlers for workstream updates
    async def on_workstream_messages_updated(
        self, message: WorkstreamMessages.Updated
    ) -> None:
        """Handle workstream summary update event from backend."""
        if not message.summary:
            Settings.logger.info(
                "Received workstream update with None summary - ignoring"
            )
            return

        try:
            # Extract display info for the summary
            title, subtitle = self.extract_item_display_info(message.summary)
            self.update_summary(message.summary, title, subtitle)
        except Exception as e:
            Settings.logger.error(f"Error updating workstream summary in UI: {e}")

    async def on_workstream_messages_deleted(
        self, message: WorkstreamMessages.Deleted
    ) -> None:
        """Handle workstream summary deletion event from backend."""
        self.remove_summary(message.summary_id)

    async def _rename_summary_worker(self, summary: "BasicSummary", current_title: str):
        """Worker method to handle rename summary dialog."""
        # Update the dialog title for workstream summaries
        dialog = EditNameDialog(current_title, title="✏️ Edit Summary Name")
        new_name = await self.app.push_screen_wait(dialog)

        if new_name:
            try:
                summary.name = new_name
                Settings.logger.info(f"Renamed workstream summary to: {new_name}")
            except Exception as e:
                Settings.logger.error(f"Error renaming workstream summary: {e}")

    async def _delete_summary_worker(self, summary: "BasicSummary", title: str):
        """Delete workstream summary after user confirmation."""
        dialog = ConfirmDialog(
            title="⚠️ Delete Workstream Summary",
            message=f"Are you sure you want to delete '{title}'?\n\nThis action cannot be undone.",
        )
        confirmed = await self.app.push_screen_wait(dialog)

        if confirmed:
            try:
                summary_id = summary.id
                summary.delete()
                Settings.logger.info(
                    f"Requested deletion of workstream summary: {title} (ID: {summary_id})"
                )
            except Exception as e:
                Settings.logger.error(f"Error deleting workstream summary: {e}")
