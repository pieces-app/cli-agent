from typing import Callable,Optional,TYPE_CHECKING
from ..streamed_identifiers.assets_snapshot import AssetSnapshot
from .base_websocket import BaseWebsocket
from websocket import WebSocketApp

from pieces_os_client.models.streamed_identifiers import StreamedIdentifiers
from pieces_os_client.models.asset import Asset


if TYPE_CHECKING:
	from ..client import PiecesClient
class AssetsIdentifiersWS(BaseWebsocket):
	"""
	WebSocket client for handling asset identifiers updates and removals.

	Attributes:
		pieces_client (PiecesClient): The client used to interact with the Pieces API.
		on_asset_update (Optional[Callable[[Asset], None]]): Callback function to handle asset updates.
		on_asset_remove (Optional[Callable[[Asset], None]]): Callback function to handle asset removals.
		on_open_callback (Optional[Callable[[WebSocketApp], None]]): Callback function to handle WebSocket opening.
		on_error (Optional[Callable[[WebSocketApp, Exception], None]]): Callback function to handle WebSocket errors.
		on_close (Optional[Callable[[WebSocketApp, str, str], None]]): Callback function to handle WebSocket closing.
	"""

	def __init__(self, pieces_client: "PiecesClient", 
				 on_asset_update: Optional[Callable[[Asset], None]] = None,
				 on_asset_remove: Optional[Callable[[Asset], None]] = None,
				 on_open_callback: Optional[Callable[[WebSocketApp], None]] = None, 
				 on_error: Optional[Callable[[WebSocketApp, Exception], None]] = None, 
				 on_close: Optional[Callable[[WebSocketApp, str, str], None]] = None):
		"""
		Initializes the AssetsIdentifiersWS instance.

		Args:
			pieces_client (PiecesClient): The client used to interact with the Pieces API.
			on_asset_update (Optional[Callable[[Asset], None]]): Callback function to handle asset updates.
			on_asset_remove (Optional[Callable[[Asset], None]]): Callback function to handle asset removals.
			on_open_callback (Optional[Callable[[WebSocketApp], None]]): Callback function to handle WebSocket opening.
			on_error (Optional[Callable[[WebSocketApp, Exception], None]]): Callback function to handle WebSocket errors.
			on_close (Optional[Callable[[WebSocketApp, str, str], None]]): Callback function to handle WebSocket closing.
		"""
		AssetSnapshot.pieces_client = pieces_client
		if on_asset_update:
			AssetSnapshot.on_update_list.append(on_asset_update)
		if on_asset_remove:
			AssetSnapshot.on_remove_list.append(on_asset_remove)

		super().__init__(pieces_client, AssetSnapshot.streamed_identifiers_callback, on_open_callback, on_error, on_close)
		AssetSnapshot._initialized = self._initialized

	@property
	def url(self):
		"""
		Returns the WebSocket URL for asset identifiers.

		Returns:
			str: The WebSocket URL.
		"""
		return self.pieces_client.ASSETS_IDENTIFIERS_WS_URL

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

