from typing import Callable, Optional, TYPE_CHECKING

from pieces._vendor.pieces_os_client.wrapper.streamed_identifiers.workstream_summary_snapshot import (
    WorkstreamSummarySnapshot,
)
from .base_websocket import BaseWebsocket
from websocket import WebSocketApp

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.models.workstream_summary import (
        WorkstreamSummary,
    )
    from ..client import PiecesClient


class WorkstreamSummariesIdentifiersWS(BaseWebsocket):
    """
    WebSocket client for handling summary identifiers updates and removals.

    Attributes:
        pieces_client (PiecesClient): The client used to interact with the Pieces API.
        on_summary_update (Optional[Callable[[WorkstreamSummary], None]]): Callback function to handle summary updates.
        on_summary_remove (Optional[Callable[[WorkstreamSummary], None]]): Callback function to handle summary removals.
        on_open_callback (Optional[Callable[[WebSocketApp], None]]): Callback function to handle WebSocket opening.
        on_error (Optional[Callable[[WebSocketApp, Exception], None]]): Callback function to handle WebSocket errors.
        on_close (Optional[Callable[[WebSocketApp, str, str], None]]): Callback function to handle WebSocket closing.
    """

    def __init__(
        self,
        pieces_client: "PiecesClient",
        on_summary_update: Optional[Callable[["WorkstreamSummary"], None]] = None,
        on_summary_remove: Optional[Callable[["WorkstreamSummary"], None]] = None,
        on_open_callback: Optional[Callable[[WebSocketApp], None]] = None,
        on_error: Optional[Callable[[WebSocketApp, Exception], None]] = None,
        on_close: Optional[Callable[[WebSocketApp, str, str], None]] = None,
    ):
        """
        Initializes the summarysIdentifiersWS instance.

        Args:
            pieces_client (PiecesClient): The client used to interact with the Pieces API.
            on_summary_update (Optional[Callable[[WorkstreamSummary], None]]): Callback function to handle summary updates.
            on_summary_remove (Optional[Callable[[WorkstreamSummary], None]]): Callback function to handle summary removals.
            on_open_callback (Optional[Callable[[WebSocketApp], None]]): Callback function to handle WebSocket opening.
            on_error (Optional[Callable[[WebSocketApp, Exception], None]]): Callback function to handle WebSocket errors.
            on_close (Optional[Callable[[WebSocketApp, str, str], None]]): Callback function to handle WebSocket closing.
        """
        WorkstreamSummarySnapshot.pieces_client = pieces_client
        if on_summary_update:
            WorkstreamSummarySnapshot.on_update_list.append(on_summary_update)
        if on_summary_remove:
            WorkstreamSummarySnapshot.on_remove_list.append(on_summary_remove)

        super().__init__(
            pieces_client,
            WorkstreamSummarySnapshot.streamed_identifiers_callback,
            on_open_callback,
            on_error,
            on_close,
        )
        WorkstreamSummarySnapshot._initialized = self._initialized

    @property
    def url(self):
        """
        Returns the WebSocket URL for summary identifiers.

        Returns:
            str: The WebSocket URL.
        """
        return self.pieces_client.WORKSTREAM_SUMMARY_WS_URL

    def on_message(self, ws, message):
        """
        Handles incoming WebSocket messages.

        Args:
            ws (WebSocketApp): The WebSocket application instance.
            message (str): The incoming message in JSON format.
        """
        from pieces._vendor.pieces_os_client.models.streamed_identifiers import (
            StreamedIdentifiers,
        )

        self.on_message_callback(StreamedIdentifiers.from_json(message))

    @property
    def _is_initialized_on_open(self):
        return False
