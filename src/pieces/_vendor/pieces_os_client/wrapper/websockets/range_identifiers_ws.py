from typing import Callable, Optional, TYPE_CHECKING
from ..streamed_identifiers.range_snapshot import RangeSnapshot
from .base_websocket import BaseWebsocket
from websocket import WebSocketApp

if TYPE_CHECKING:
    from ..client import PiecesClient


class RangesIdentifiersWS(BaseWebsocket):
    """
    WebSocket client for handling range identifiers updates and removals.

    Attributes:
        pieces_client (PiecesClient): The client used to interact with the Pieces API.
        on_range_update (Optional[Callable[[Range], None]]): Callback function to handle range updates.
        on_range_remove (Optional[Callable[[Range], None]]): Callback function to handle range removals.
        on_open_callback (Optional[Callable[[WebSocketApp], None]]): Callback function to handle WebSocket opening.
        on_error (Optional[Callable[[WebSocketApp, Exception], None]]): Callback function to handle WebSocket errors.
        on_close (Optional[Callable[[WebSocketApp, str, str], None]]): Callback function to handle WebSocket closing.
    """

    def __init__(
        self,
        pieces_client: "PiecesClient",
        on_range_update: Optional[Callable[["Range"], None]] = None,
        on_range_remove: Optional[Callable[["Range"], None]] = None,
        on_open_callback: Optional[Callable[[WebSocketApp], None]] = None,
        on_error: Optional[Callable[[WebSocketApp, Exception], None]] = None,
        on_close: Optional[Callable[[WebSocketApp, str, str], None]] = None,
    ):
        """
        Initializes the RangesIdentifiersWS instance.

        Args:
            pieces_client (PiecesClient): The client used to interact with the Pieces API.
            on_range_update (Optional[Callable[[Range], None]]): Callback function to handle range updates.
            on_range_remove (Optional[Callable[[Range], None]]): Callback function to handle range removals.
            on_open_callback (Optional[Callable[[WebSocketApp], None]]): Callback function to handle WebSocket opening.
            on_error (Optional[Callable[[WebSocketApp, Exception], None]]): Callback function to handle WebSocket errors.
            on_close (Optional[Callable[[WebSocketApp, str, str], None]]): Callback function to handle WebSocket closing.
        """
        RangeSnapshot.pieces_client = pieces_client
        if on_range_update:
            RangeSnapshot.on_update_list.append(on_range_update)
        if on_range_remove:
            RangeSnapshot.on_remove_list.append(on_range_remove)

        super().__init__(
            pieces_client,
            RangeSnapshot.streamed_identifiers_callback,
            on_open_callback,
            on_error,
            on_close,
        )
        RangeSnapshot._initialized = self._initialized

    @property
    def url(self):
        """
        Returns the WebSocket URL for range identifiers.

        Returns:
            str: The WebSocket URL.
        """
        return self.pieces_client.RANGES_IDENTIFIERS_WS_URL

    def on_message(self, ws, message):
        """
        Handles incoming WebSocket messages.

        Args:
            ws (WebSocketApp): The WebSocket application instance.
            message (str): The incoming message in JSON format.
        """
        from pieces._vendor.pieces_os_client.models.streamed_identifiers import StreamedIdentifiers

        self.on_message_callback(StreamedIdentifiers.from_json(message))

    @property
    def _is_initialized_on_open(self):
        return False
