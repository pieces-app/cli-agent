from .base_websocket import BaseWebsocket

class HealthWS(BaseWebsocket):
	@property
	def url(self):
		return self.pieces_client.HEALTH_WS_URL

	def on_message(self, ws, message:str):
		self.on_message_callback(message)
		if message.lower().startswith("ok"):
			self.pieces_client.is_pos_stream_running = True

	def on_close(self, ws, close_status_code, close_msg):
		self.pieces_client.is_pos_stream_running = False
		self.pieces_client.port = None # Reset the port
		super().on_close(ws, close_status_code, close_msg)