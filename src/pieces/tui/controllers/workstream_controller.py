"""Controller for handling workstream-related events and operations."""

from typing import Optional, List, TYPE_CHECKING
from pieces.settings import Settings
from .base_controller import BaseController, EventType
from pieces._vendor.pieces_os_client.wrapper.basic_identifier.summary import (
    BasicSummary,
)
from pieces._vendor.pieces_os_client.wrapper.streamed_identifiers.workstream_summary_snapshot import (
    WorkstreamSummarySnapshot,
)

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.models.workstream_summary import (
        WorkstreamSummary,
    )


class WorkstreamController(BaseController):
    """Handles workstream-related events from the backend."""

    def __init__(self):
        """Initialize the workstream controller."""
        super().__init__()
        self._workstream_ws = None
        self._current_summary: Optional[BasicSummary] = None

    def initialize(self):
        """Set up WebSocket listeners for workstream events."""
        if self._initialized:
            return

        try:
            from pieces._vendor.pieces_os_client.wrapper.websockets.workstream_summary_ws import (
                WorkstreamSummariesIdentifiersWS,
            )

            self._workstream_ws = (
                WorkstreamSummariesIdentifiersWS.get_instance()
                or WorkstreamSummariesIdentifiersWS(
                    pieces_client=Settings.pieces_client,
                    on_summary_update=self._on_workstream_summary_update,
                    on_summary_remove=self._on_workstream_summary_remove,
                )
            )
            self._workstream_ws.start()

            Settings.logger.info(
                "WorkstreamController initialized (WebSocket setup pending)"
            )
            self._initialized = True

        except Exception as e:
            Settings.logger.error(f"Failed to initialize WorkstreamController: {e}")

    def cleanup(self):
        """Stop listening to workstream events."""
        try:
            if self._workstream_ws:
                Settings.logger.debug("Closing workstream WebSocket...")
                self._workstream_ws.close()
                Settings.logger.debug("Workstream WebSocket closed successfully")

            self._workstream_ws = None
            self._current_summary = None

        except Exception as e:
            Settings.logger.error(f"Failed to properly close workstream WebSocket: {e}")

        # Clear all event listeners
        self._safe_cleanup()

    def _on_workstream_summary_update(self, summary: "WorkstreamSummary"):
        Settings.logger.debug(f"Workstream summary update received: {summary.id}")

        try:
            basic_summary = BasicSummary(summary.id)
            self.emit(EventType.WORKSTREAM_SUMMARY_UPDATED, basic_summary)
            Settings.logger.info(
                f"Successfully processed workstream update: {summary.id}"
            )
        except Exception as e:
            Settings.logger.error(
                f"Failed to process workstream summary update {summary.id}: {e}",
            )

    def _on_workstream_summary_remove(self, summary: "WorkstreamSummary"):
        """Handle workstream summary removal from WebSocket."""
        self.emit(EventType.WORKSTREAM_SUMMARY_DELETED, summary.id)
        Settings.logger.info(f"Workstream summary removal received: {summary.id}")

    def switch_summary(self, summary: Optional[BasicSummary]):
        """
        Switch to a different workstream summary.

        Args:
            summary: The WorkstreamSummary object to switch to (None for new summary)
        """
        self._current_summary = summary
        if summary:
            Settings.logger.info(f"Switched to workstream summary: {summary.name}")
            self.emit(EventType.WORKSTREAM_SUMMARY_SWITCHED, summary)
        else:
            Settings.logger.info("Cleared workstream summary selection")

    def update_summary_content(self, summary: "BasicSummary", content: str):
        """
        Update the content of a workstream summary.

        Args:
            summary: The summary to update
            content: New content for the summary
        """
        try:
            summary.raw_content = content

            Settings.logger.info(f"Updated workstream summary content: {summary.name}")
            self.emit(EventType.WORKSTREAM_SUMMARY_UPDATED, summary)

        except Exception as e:
            Settings.logger.error(f"Error updating workstream summary content: {e}")

        Settings.logger.info(
            f"Update workstream summary content requested: {summary.name}"
        )

    def delete_summary(self, summary: BasicSummary):
        """
        Delete a workstream summary.

        Args:
            summary: The summary to delete
        """
        try:
            summary_id = summary.id
            summary_name = summary.name
            summary.delete()

            # Clear current summary if it was the deleted one
            if self._current_summary and self._current_summary.id == summary_id:
                self._current_summary = None

            Settings.logger.info(f"Deleted workstream summary: {summary_name}")
            self.emit(EventType.WORKSTREAM_SUMMARY_DELETED, summary_id)

        except Exception as e:
            Settings.logger.error(f"Error deleting workstream summary: {e}")

        Settings.logger.info(f"Delete workstream summary requested: {summary.name}")

    def get_all_summaries(self) -> List[BasicSummary]:
        """
        Get all workstream summaries.

        Returns:
            List of WorkstreamSummary objects
        """
        try:
            return [
                BasicSummary(s)
                for s in WorkstreamSummarySnapshot.identifiers_snapshot.keys()
            ]
        except Exception as e:
            Settings.logger.error(f"Error fetching workstream summaries: {e}")
            return []

    def get_current_summary(self) -> Optional[BasicSummary]:
        """Get the currently selected workstream summary."""
        return self._current_summary
