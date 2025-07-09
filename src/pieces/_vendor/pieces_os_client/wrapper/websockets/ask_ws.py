from websocket import WebSocketConnectionClosedException, WebSocketApp
from typing import Callable, Optional,TYPE_CHECKING

from .base_websocket import BaseWebsocket

if TYPE_CHECKING:
	from ..client import PiecesClient
	from pieces._vendor.pieces_os_client.models.qgpt_stream_input import QGPTStreamInput
	from pieces._vendor.pieces_os_client.models.qgpt_stream_output import QGPTStreamOutput

class AskStreamWS(BaseWebsocket):
	"""
	A WebSocket client for handling streaming requests and responses using the PiecesClient.

	Attributes:
		pieces_client (PiecesClient): The client used to interact with the Pieces API.
		on_message_callback (Callable[[QGPTStreamOutput], None]): Callback function to handle incoming messages.
		on_open_callback (Optional[Callable[[WebSocketApp], None]]): Optional callback function to handle WebSocket opening.
		on_error (Optional[Callable[[WebSocketApp, Exception], None]]): Optional callback function to handle errors.
		on_close (Optional[Callable[[WebSocketApp, str, str], None]]): Optional callback function to handle WebSocket closing.
	"""
	def __init__(self, pieces_client: "PiecesClient",
				 on_message_callback: Callable[["QGPTStreamOutput"], None], 
				 on_open_callback: Optional[Callable[[WebSocketApp], None]] = None, 
				 on_error: Optional[Callable[[WebSocketApp, Exception], None]] = None, 
				 on_close: Optional[Callable[[WebSocketApp, str, str], None]] = None):
		"""
		Initializes the AskStreamWS instance.

		Args:
			pieces_client (PiecesClient): The client used to interact with the Pieces API.
			on_message_callback (Callable[[QGPTStreamOutput], None]): Callback function to handle incoming messages.
			on_open_callback (Optional[Callable[[WebSocketApp], None]]): Optional callback function to handle WebSocket opening.
			on_error (Optional[Callable[[WebSocketApp, Exception], None]]): Optional callback function to handle errors.
			on_close (Optional[Callable[[WebSocketApp, str, str], None]]): Optional callback function to handle WebSocket closing.
		"""
		super().__init__(pieces_client, on_message_callback, on_open_callback, on_error, on_close)

	@property
	def url(self):
		"""
		Returns the WebSocket URL for the ASK stream.

		Returns:
			str: The WebSocket URL.
		"""
		return self.pieces_client.ASK_STREAM_WS_URL

	def on_message(self, ws, message):
		"""
		Handles incoming messages from the WebSocket.

		Args:
			ws (WebSocketApp): The WebSocket application instance.
			message (str): The incoming message in JSON format.
		"""
		from pieces._vendor.pieces_os_client.models.qgpt_stream_output import QGPTStreamOutput
		self.on_message_callback(QGPTStreamOutput.from_json(message))

	def send_message(self, message: "QGPTStreamInput"):
		"""
		Sends a message through the WebSocket.

		Args:
			message (QGPTStreamInput): The message to be sent.

		Raises:
			WebSocketConnectionClosedException: If the WebSocket connection is closed.
		"""
		try:
			if not self.ws:
				raise WebSocketConnectionClosedException()
			self.ws.send(message.to_json())
		except WebSocketConnectionClosedException:
			self.on_open_callback = lambda ws: ws.send(message.to_json())  # Send the message on opening
			self.start()  # Start a new WebSocket since we are not connected to any
