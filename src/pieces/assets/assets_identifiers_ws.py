import asyncio
import pieces_os_client as pos_client
import websocket
from pieces.settings import Settings
import threading
from abc import ABC, abstractmethod

class BaseWebsocket(ABC):
    instances = []

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(BaseWebsocket, cls).__new__(cls)
        return cls.instance

    def __init__(self, on_message_callback):
        self.ws = None
        self.on_message_callback = on_message_callback
        self.loop = asyncio.new_event_loop()
        self.thread = None
        if self not in BaseWebsocket.instances:
            BaseWebsocket.instances.append(self)

    @abstractmethod
    def get_url(self):
        pass

    @abstractmethod
    def on_message(self, ws, message):
        pass

    def on_error(self, ws, error):
        print(f"Error: {error}")
        self.ws = None

    def on_close(self, ws, close_status_code, close_msg):
        print(f"WebSocket closed: {close_status_code} - {close_msg}")
        self.ws = None

    def on_open(self, ws):
        print("WebSocket connection opened")

    def open_websocket(self):
        if self.ws:
            return
        self.ws = websocket.WebSocketApp(
            self.get_url(),
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open
        )
        self.ws.run_forever()

    def start(self):
        self.thread = threading.Thread(target=self.open_websocket)
        self.thread.start()

    def close_websocket_connection(self):
        if self.ws:
            self.ws.close()
        if self.thread:
            self.thread.join()

    @classmethod
    def close_all(cls):
        for instance in cls.instances:
            instance.close_websocket_connection()

class AssetsIdentifiersWS(BaseWebsocket):
    def __init__(self, on_message_callback):
        super().__init__(on_message_callback)
        self.start()  # Using the start method from BaseWebsocket

    def get_url(self):
        return Settings.ASSETS_IDENTIFIERS_WS_URL

    def on_message(self, ws, message):
        """Handle incoming websocket messages."""
        self.on_message_callback(pos_client.StreamedIdentifiers.from_json(message))

    def on_error(self, ws, error):
        """Handle websocket errors."""
        super().on_error(ws, error)
        print(error)

    def on_close(self, ws, close_status_code, close_msg):
        """Handle websocket closure."""
        super().on_close(ws, close_status_code, close_msg)

    def on_open(self, ws):
        """Handle websocket opening."""
        super().on_open(ws)

    def open_websocket(self):
        """Opens a websocket connection"""
        super().open_websocket()

    def close_websocket_connection(self):
        """Close the websocket connection."""
        super().close_websocket_connection()

    @classmethod
    def close_all(cls):
        """Close all websocket connections."""
        super().close_all()

