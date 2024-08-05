import asyncio
import pieces_os_client as pos_client
import websocket
from pieces.settings import Settings
import threading
from base_websocket import BaseWebsocket
import json
from typing import Dict ,Any


class AssetsIdentifiersWS(BaseWebsocket):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AssetsIdentifiersWS, cls).__new__(cls)
        return cls.instance

    @property
    def url(self):
        return Settings.ASSETS_IDENTIFIERS_WS_URL

    def open_websocket(self):
        """Opens a websocket connection"""
        if self.ws:  # connect only once
            return
        self.ws = websocket.WebSocketApp(self.url,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.on_open = self.on_open
        self.ws.run_forever()

    def on_message(self, ws, message):
        """Handle incoming websocket messages."""
        streamed_identifiers = pos_client.StreamedIdentifiers.from_json(message)
        self.on_message_callback(streamed_identifiers)

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
