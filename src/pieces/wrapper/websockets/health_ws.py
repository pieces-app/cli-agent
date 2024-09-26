from .base_websocket import BaseWebsocket

class HealthWS(BaseWebsocket):
	@property
	def url(self):
		return self.pieces_client.HEALTH_WS_URL

	def on_message(self, ws, message):
		self.on_message_callback(message)