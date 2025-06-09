from typing import Callable, Optional, TYPE_CHECKING
from ..streamed_identifiers.anchor_snapshot import AnchorSnapshot
from .base_websocket import BaseWebsocket
from websocket import WebSocketApp

from pieces._vendor.pieces_os_client.models.streamed_identifiers import StreamedIdentifiers
from pieces._vendor.pieces_os_client.models.anchor import Anchor


if TYPE_CHECKING:
	from ..client import PiecesClient

class AnchorsIdentifiersWS(BaseWebsocket):
	"""
	WebSocket client for handling anchor identifiers updates and removals.

	Attributes:
		pieces_client (PiecesClient): The client used to interact with the Pieces API.
		on_anchor_update (Optional[Callable[[Anchor], None]]): Callback function to handle anchor updates.
		on_anchor_remove (Optional[Callable[[Anchor], None]]): Callback function to handle anchor removals.
		on_open_callback (Optional[Callable[[WebSocketApp], None]]): Callback function to handle WebSocket opening.
		on_error (Optional[Callable[[WebSocketApp, Exception], None]]): Callback function to handle WebSocket errors.
		on_close (Optional[Callable[[WebSocketApp, str, str], None]]): Callback function to handle WebSocket closing.
	"""

	def __init__(self, pieces_client: "PiecesClient", 
				 on_anchor_update: Optional[Callable[[Anchor], None]] = None,
				 on_anchor_remove: Optional[Callable[[Anchor], None]] = None,
				 on_open_callback: Optional[Callable[[WebSocketApp], None]] = None, 
				 on_error: Optional[Callable[[WebSocketApp, Exception], None]] = None, 
				 on_close: Optional[Callable[[WebSocketApp, str, str], None]] = None):
		"""
		Initializes the AnchorsIdentifiersWS instance.

		Args:
			pieces_client (PiecesClient): The client used to interact with the Pieces API.
			on_anchor_update (Optional[Callable[[Anchor], None]]): Callback function to handle anchor updates.
			on_anchor_remove (Optional[Callable[[Anchor], None]]): Callback function to handle anchor removals.
			on_open_callback (Optional[Callable[[WebSocketApp], None]]): Callback function to handle WebSocket opening.
			on_error (Optional[Callable[[WebSocketApp, Exception], None]]): Callback function to handle WebSocket errors.
			on_close (Optional[Callable[[WebSocketApp, str, str], None]]): Callback function to handle WebSocket closing.
		"""
		AnchorSnapshot.pieces_client = pieces_client
		if on_anchor_update:
			AnchorSnapshot.on_update_list.append(on_anchor_update)
		if on_anchor_remove:
			AnchorSnapshot.on_remove_list.append(on_anchor_remove)

		super().__init__(pieces_client, AnchorSnapshot.streamed_identifiers_callback, on_open_callback, on_error, on_close)
		AnchorSnapshot._initialized = self._initialized

	@property
	def url(self):
		"""
		Returns the WebSocket URL for anchor identifiers.

		Returns:
			str: The WebSocket URL.
		"""
		return self.pieces_client.ANCHORS_IDENTIFIERS_WS_URL

	def on_message(self, ws, message):
		"""
		Handles incoming WebSocket messages.

		Args:
			ws (WebSocketApp): The WebSocket application instance.
			message (str): The incoming message in JSON format.
		"""
		self.on_message_callback(StreamedIdentifiers.from_json(message))

	@property
	def _is_initialized_on_open(self):
		return False

