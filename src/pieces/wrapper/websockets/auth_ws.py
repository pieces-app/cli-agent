from .base_websocket import BaseWebsocket
from pieces_os_client.models.user_profile import UserProfile
import json
from typing import Callable, Optional,TYPE_CHECKING
from websocket import WebSocketApp

if TYPE_CHECKING:
	from ..client import PiecesClient

class AuthWS(BaseWebsocket):
	"""
	AuthWS is a WebSocket client for handling authentication-related messages.

	Attributes:
		pieces_client (PiecesClient): The client used to interact with the Pieces service.
		on_message_callback (Callable[[Optional[UserProfile]], None]): Callback function to handle incoming messages.
		on_open_callback (Optional[Callable[[WebSocketApp], None]]): Optional callback function to handle WebSocket opening.
		on_error (Optional[Callable[[WebSocketApp, Exception], None]]): Optional callback function to handle errors.
		on_close (Optional[Callable[[WebSocketApp, str, str], None]]): Optional callback function to handle WebSocket closing.
	"""

	def __init__(self, 
				 pieces_client: "PiecesClient", 
				 on_message_callback: Callable[[Optional[UserProfile]], None],
				 on_open_callback: Optional[Callable[[WebSocketApp], None]] = None, 
				 on_error: Optional[Callable[[WebSocketApp, Exception], None]] = None, 
				 on_close: Optional[Callable[[WebSocketApp, str, str], None]] = None):
		"""
		Initializes the AuthWS instance.

		Args:
			pieces_client (PiecesClient): The client used to interact with the Pieces service.
			on_message_callback (Callable[[Optional[UserProfile]], None]): Callback function to handle incoming messages.
			on_open_callback (Optional[Callable[[WebSocketApp], None]]): Optional callback function to handle WebSocket opening.
			on_error (Optional[Callable[[WebSocketApp, Exception], None]]): Optional callback function to handle errors.
			on_close (Optional[Callable[[WebSocketApp, str, str], None]]): Optional callback function to handle WebSocket closing.
		"""
		super().__init__(pieces_client, on_message_callback, on_open_callback, on_error, on_close)

	@property
	def url(self):
		"""
		Returns the WebSocket URL for authentication.

		Returns:
			str: The WebSocket URL for authentication.
		"""
		return self.pieces_client.AUTH_WS_URL

	def on_message(self, ws, message):
		"""
		Handles incoming WebSocket messages.

		Args:
			ws (WebSocketApp): The WebSocket application instance.
			message (str): The incoming message as a JSON string.

		Raises:
			json.decoder.JSONDecodeError: If the message cannot be decoded as JSON.
		"""
		try:
			self.on_message_callback(UserProfile.from_json(message))
		except json.decoder.JSONDecodeError:
			self.on_message_callback(None)  # User logged out!
