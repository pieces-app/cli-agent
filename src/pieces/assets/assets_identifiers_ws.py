import asyncio
import pieces_os_client as pos_client
import websocket
from pieces.settings import Settings
import threading


class AssetsIdentifiersWS:
    def __new__(cls,*args,**kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AssetsIdentifiersWS, cls).__new__(cls)
        return cls.instance
    
    def __init__(self, on_message_callback):
        self.ws = None
        self.on_message_callback = on_message_callback

        # Create a new event loop
        self.loop = asyncio.new_event_loop()

        # Run the event loop in a new thread
        self.thread = threading.Thread(target=self.open_websocket)
        self.thread.start()
    

    def open_websocket(self):
        """Opens a websocket connection"""
        if self.ws: # connect only once
            return
        self.ws = websocket.WebSocketApp(Settings.ASSETS_IDENTIFIERS_WS_URL,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.on_open = self.on_open
        self.ws.run_forever()

    def on_message(self, ws, message):
        """Handle incoming websocket messages."""
        self.on_message_callback(pos_client.StreamedIdentifiers.from_json(message))

    def on_error(self, ws, error):
        """Handle websocket errors."""
        self.ws = None
        print(error)

    def on_close(self, ws, close_status_code, close_msg):
        """Handle websocket closure."""
        self.ws = None

    def on_open(self, ws):
        """Handle websocket opening."""
        pass

    def close_websocket_connection(self):
        """Close the websocket connection."""
        if self.ws:
            self.ws.close()