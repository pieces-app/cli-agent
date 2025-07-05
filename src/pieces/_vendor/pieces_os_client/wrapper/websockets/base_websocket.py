from typing import Callable, Optional,TYPE_CHECKING, List
import websocket
import threading
from abc import ABC, abstractmethod

if TYPE_CHECKING:
	from ..client import PiecesClient

class BaseWebsocket(ABC):
	instances = []
	_initialized_events:List[threading.Event] = []

	def __new__(cls, *args, **kwargs):
		"""
		Ensure that only one instance of the url class is created (Singleton pattern).
		"""
		if not hasattr(cls, 'instance'):
			cls.instance = super(BaseWebsocket, cls).__new__(cls)
		return cls.instance

	def __init__(self,
				 pieces_client: "PiecesClient",
				 on_message_callback: Callable[[str], None],
				 on_open_callback: Optional[Callable[[websocket.WebSocketApp], None]] = None,
				 on_error: Optional[Callable[[websocket.WebSocketApp, Exception], None]] = None,
				 on_close: Optional[Callable[[websocket.WebSocketApp, str, str], None]] = None):
		"""
		Initialize the BaseWebsocket instance.

		:param pieces_client: An instance of PiecesClient.
		:param on_message_callback: Callback function to handle incoming messages.
		:param on_open_callback: Optional callback function to handle the websocket opening.
		:param on_error: Optional callback function to handle errors.
		:param on_close: Optional callback function to handle the websocket closing.
		"""
		self.ws = None
		self.thread = None
		self.running = False
		self.on_message_callback = on_message_callback
		self.on_open_callback = on_open_callback if on_open_callback else lambda x: None
		self.on_error = on_error if on_error else lambda ws, error: print(error)
		self.on_close = on_close if on_close else lambda ws, close_status_code, close_msg: None
		self.pieces_client = pieces_client
		self._initialized = threading.Event()
		self._initialized.set() # Set it as true at the beginning


		if self not in BaseWebsocket.instances:
			BaseWebsocket.instances.append(self)
			BaseWebsocket._initialized_events.append(self._initialized)
	
	@property
	def _is_initialized_on_open(self):
		return True

	@abstractmethod
	def url(self) -> str:
		"""
		The URL to connect to. Should be overridden by subclasses.
		"""
		pass

	@abstractmethod
	def on_message(self, ws, message):
		"""
		Handle incoming messages. Should be overridden by subclasses.
		"""
		pass

	def on_open(self, ws):
		"""
		Handle the websocket opening event.
		"""
		self.running = True
		self.on_open_callback(ws)
		if self._is_initialized_on_open:
			self._initialized.set()

	def run(self):
		"""
		Run the websocket connection.
		"""
		self.ws = websocket.WebSocketApp(
			self.url,
			on_message=self.on_message,
			on_error=self.on_error,
			on_close=self.on_close,
			on_open=self.on_open
		)
		self.ws.run_forever()

	def start(self):
		"""
		Start the websocket connection in a new thread.
		"""
		if not self.running:
			self._initialized.clear()
			self.thread = threading.Thread(target=self.run)
			self.thread.start()

	def close(self):
		"""
		Close the websocket connection and stop the thread.
		"""
		if self.running and self.ws:
			self.ws.close()
			self.thread.join()
			self.running = False

	@classmethod
	def close_all(cls):
		"""
		Close all websocket instances.
		"""
		for instance in cls.instances:
			instance.close()

	@classmethod
	def reconnect_all(cls):
		"""
		Reconnect all websocket instances.
		"""
		for instance in cls.instances:
			instance.reconnect()

	def reconnect(self):
		"""
		Reconnect the websocket connection.
		"""
		self.close()
		self.start()

	def __str__(self):
		"""
		Return a string representation of the instance.
		"""
		return getattr(self, "url", "BaseWebsocket(ABC)")

	@classmethod
	def is_running(cls) -> bool:
		"""
		Check if the websocket instance is running.

		:return: True if running, False otherwise.
		"""
		instance = cls.get_instance()
		if instance:
			return cls.instance.running
		return False

	@classmethod
	def get_instance(cls) -> Optional[type]:
		"""
		Get the singleton instance of the class.

		:return: The singleton instance or None if not created.
		"""
		return getattr(cls, 'instance', None)

	@classmethod
	def start_all(cls):
		"""
		Start all the websockets that are already initialized.
		"""
		for ws in cls.instances:
			ws.start()

	@classmethod
	def wait_all(cls):
		"""
			Wait for all websockets to set the internal flag on
		"""
		for event in cls._initialized_events:
			event.wait()

