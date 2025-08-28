"""Workstream Activity View - using base dual-pane architecture for consistency."""

from typing import Optional
from textual.binding import Binding
from textual.widgets import Footer

from pieces.settings import Settings
from ..widgets import WorkstreamActivitiesPanel, WorkstreamContentPanel, ConfirmDialog
from ..controllers import EventHub
from ..messages import (
    WorkstreamMessages,
    ViewMessages,
)
from .base_dual_pane_view import BaseDualPaneView


class WorkstreamActivityView(BaseDualPaneView):
    """Workstream activities view with consistent dual-pane layout."""

    BINDINGS = [
        Binding("ctrl+e", "toggle_edit_mode", "Toggle Edit Mode"),
        Binding("ctrl+shift+c", "switch_to_chat", "Switch to Copilot"),
    ]

    def __init__(self, event_hub: "EventHub", **kwargs):
        super().__init__(
            event_hub=event_hub, view_name="Workstream Activities", **kwargs
        )
        self.workstream_activities_panel: Optional[WorkstreamActivitiesPanel] = None
        self.workstream_content_panel: Optional[WorkstreamContentPanel] = None

    # Base view implementation
    def create_list_panel(self) -> WorkstreamActivitiesPanel:
        """Create the workstream activities panel (LEFT side)."""
        self.workstream_activities_panel = WorkstreamActivitiesPanel()
        return self.workstream_activities_panel

    def create_content_panel(self) -> WorkstreamContentPanel:
        """Create the workstream content panel (RIGHT side)."""
        self.workstream_content_panel = WorkstreamContentPanel()
        return self.workstream_content_panel

    def create_additional_components(self):
        """Create chat input and status bar."""
        self.footer = Footer()
        yield self.footer

    def _initialize_view(self):
        """Initialize workstream-specific components."""
        # Load items
        self._load_items()

    def _load_items(self):
        """Load workstream summaries into the list panel."""
        if not self.workstream_activities_panel or not self.event_hub:
            Settings.logger.info("Cannot load workstream summaries: missing components")
            return

        try:
            summaries = self.event_hub.workstream.get_all_summaries()
            Settings.logger.info(f"Found {len(summaries)} workstream summaries to load")
            self.workstream_activities_panel.load_summaries(summaries)

        except Exception as e:
            Settings.logger.error(f"Error loading workstream summaries: {e}")

    def _show_status_message(self, message: str, duration: int = 3):
        """Show temporary status message."""
        # For now, just log since workstream view doesn't have status bar
        Settings.logger.info(f"Workstream Status: {message}")

    def _show_unsaved_changes_dialog(self, target_summary):
        """Show confirmation dialog for unsaved changes."""
        self.app.run_worker(self._handle_unsaved_changes_dialog(target_summary))

    async def _handle_unsaved_changes_dialog(self, target_summary):
        """Handle the unsaved changes dialog in a worker context."""
        dialog = ConfirmDialog(
            title="⚠️ Unsaved Changes",
            message="You have unsaved changes in the current workstream summary.\n\nDo you want to discard these changes and switch to the selected summary?",
            width=70,
            height=14,
        )

        result = await self.app.push_screen_wait(dialog)

        if result:
            Settings.logger.info("User confirmed discarding unsaved changes")
            if (
                self.workstream_content_panel
                and self.workstream_content_panel.edit_mode
            ):
                self.workstream_content_panel.edit_mode = False
            self.post_message(WorkstreamMessages.SwitchConfirmed(target_summary))
        else:
            # User cancelled - stay on current summary
            Settings.logger.info(
                "User cancelled summary switch - keeping unsaved changes"
            )

    # Message handlers that need view-level handling
    async def on_workstream_messages_switch_requested(
        self, message: WorkstreamMessages.SwitchRequested
    ) -> None:
        """Handle workstream summary switch request - check for unsaved changes first."""
        # Check if there are unsaved changes in the current content
        if (
            self.workstream_content_panel
            and self.workstream_content_panel.has_unsaved_changes()
        ):
            # Show confirmation dialog
            self._show_unsaved_changes_dialog(message.summary)
        else:
            if (
                self.workstream_content_panel
                and self.workstream_content_panel.edit_mode
            ):
                self.workstream_content_panel.edit_mode = False
            self.post_message(WorkstreamMessages.SwitchConfirmed(message.summary))

    async def on_workstream_messages_switch_confirmed(
        self, message: WorkstreamMessages.SwitchConfirmed
    ) -> None:
        """Handle confirmed workstream summary switch event - update content panel."""
        if self.workstream_content_panel:
            self.workstream_content_panel.clear_content(False)
            self.workstream_content_panel.load_workstream_summary(message.summary)

    async def on_workstream_messages_edit_mode_toggled(
        self, message: WorkstreamMessages.EditModeToggled
    ) -> None:
        """Handle edit mode toggle."""
        mode = "edit" if message.edit_mode else "read"
        Settings.logger.info(f"Workstream content switched to {mode} mode")

    async def on_workstream_messages_content_saved(
        self, message: WorkstreamMessages.ContentSaved
    ) -> None:
        """Handle workstream content save."""
        if (
            self.workstream_content_panel
            and self.workstream_content_panel.current_summary
        ):
            # Save content via controller
            self.event_hub.workstream.update_summary_content(
                self.workstream_content_panel.current_summary, message.content
            )
            Settings.logger.info("Workstream content saved")

    # Workstream-specific actions
    def action_toggle_edit_mode(self):
        """Toggle edit mode in the content panel."""
        if self.workstream_content_panel:
            self.workstream_content_panel.action_toggle_edit_mode()

    def action_switch_to_chat(self):
        """Switch to chat view."""
        self.post_message(ViewMessages.SwitchToChat())

    def cleanup(self):
        """Clean up workstream view resources."""
        try:
            # Clear widget references
            self.workstream_activities_panel = None
            self.workstream_content_panel = None

        except Exception as e:
            Settings.logger.error(f"Error during WorkstreamActivityView cleanup: {e}")

        super().cleanup()
